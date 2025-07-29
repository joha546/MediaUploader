import wmi
import tkinter as tk
from tkinter import messagebox, filedialog
import logging
import os
import glob
import subprocess
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_all_wmi_devices():
    """Debug function to list all WMI devices for analysis"""
    try:
        c = wmi.WMI()
        logger.info("=== ALL WMI DEVICES DEBUG ===")
        
        # Check all PnP devices
        print("\n=== PnP Devices ===")
        for device in c.Win32_PnPEntity():
            if device.Caption and any(keyword in device.Caption.upper() for keyword in 
                                    ['USB', 'ANDROID', 'PHONE', 'MTP', 'PORTABLE', 'SAMSUNG', 'XIAOMI', 'HUAWEI']):
                print(f"PnP Device: {device.Caption}")
                logger.debug(f"PnP Device: {device.Caption}")
                if hasattr(device, 'DeviceID'):
                    logger.debug(f"  DeviceID: {device.DeviceID}")
        
        # Check logical disks
        print("\n=== Logical Disks ===")
        for disk in c.Win32_LogicalDisk():
            print(f"Drive: {disk.DeviceID} | Type: {disk.DriveType} | Description: {disk.Description}")
            logger.debug(f"Drive: {disk.DeviceID} | Type: {disk.DriveType} | Description: {disk.Description}")
        
        # Check volume information
        print("\n=== Volumes ===")
        for volume in c.Win32_Volume():
            if volume.DriveLetter:
                print(f"Volume: {volume.DriveLetter} | Label: {volume.Label}")
                logger.debug(f"Volume: {volume.DriveLetter} | Label: {volume.Label}")
        
    except Exception as e:
        logger.error(f"Error getting WMI devices: {str(e)}")
        print(f"Error getting WMI devices: {str(e)}")

def check_powershell_devices():
    """Use PowerShell to detect portable devices and return device names"""
    try:
        # PowerShell command to get portable devices
        ps_command = '''
        Get-WmiObject -Class Win32_PnPEntity | Where-Object {
            $_.Caption -match "MTP|Portable|Android|Phone" -or 
            $_.DeviceID -match "USB.*MTP|USB.*ANDROID"
        } | Select-Object Caption, DeviceID, Status | Format-Table -AutoSize
        '''
        
        result = subprocess.run(['powershell', '-Command', ps_command], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            print("\n=== PowerShell Portable Devices ===")
            print(result.stdout)
            logger.info(f"PowerShell devices: {result.stdout}")
            
            # Extract device names from PowerShell output
            devices = []
            lines = result.stdout.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('-') and 'Caption' not in line and line:
                    # Extract the caption part (first column before DeviceID)
                    parts = line.split()
                    if parts:
                        # Take everything before what looks like a device ID
                        caption_parts = []
                        for part in parts:
                            if 'USB\\' in part or 'HID\\' in part:
                                break
                            caption_parts.append(part)
                        if caption_parts:
                            device_name = ' '.join(caption_parts)
                            devices.append(device_name)
            
            return devices
        return []
    except Exception as e:
        logger.error(f"PowerShell command failed: {str(e)}")
        return []

def detect_card():
    """
    Enhanced detection for removable drives, mobile devices, and MTP devices.
    """
    root = tk.Tk()
    root.withdraw()
    
    try:
        # Debug: Show all devices first
        print("=== DEBUGGING: Listing all detected devices ===")
        get_all_wmi_devices()
        powershell_devices = check_powershell_devices()
        
        c = wmi.WMI()
        
        # Step 1: Check removable drives (DriveType 2)
        print("\n=== Checking Removable Drives ===")
        for disk in c.Win32_LogicalDisk(DriveType=2):
            if disk.Size:
                drive_path = disk.DeviceID + "\\"
                logger.info(f"Found removable drive: {drive_path}")
                print(f"Found removable drive: {drive_path}")
                root.destroy()
                return drive_path
        
        # Step 2: Enhanced mobile device detection (WMI)
        print("\n=== Checking Mobile/MTP Devices (WMI) ===")
        mobile_devices = []
        
        for device in c.Win32_PnPEntity():
            if device.Caption and device.Status == "OK":
                caption_upper = device.Caption.upper()
                
                # Expanded keywords for phone detection
                phone_keywords = [
                    'MTP', 'PORTABLE DEVICE', 'ANDROID', 'PHONE', 
                    'SAMSUNG', 'XIAOMI', 'HUAWEI', 'ONEPLUS', 'OPPO', 'VIVO',
                    'MEDIA DEVICE', 'COMPOSITE DEVICE'
                ]
                
                if any(keyword in caption_upper for keyword in phone_keywords):
                    mobile_devices.append(device.Caption)
                    logger.info(f"Found mobile device (WMI): {device.Caption}")
                    print(f"Found mobile device (WMI): {device.Caption}")
        
        # Step 2b: Add PowerShell detected devices
        if powershell_devices:
            print(f"\n=== Adding PowerShell Detected Devices ===")
            for ps_device in powershell_devices:
                if ps_device not in mobile_devices:
                    mobile_devices.append(ps_device)
                    logger.info(f"Found mobile device (PowerShell): {ps_device}")
                    print(f"Found mobile device (PowerShell): {ps_device}")
        
        # Step 3: Check for drives that might be phones (DriveType 0 = Unknown, might be MTP)
        print("\n=== Checking Unknown Drive Types ===")
        for disk in c.Win32_LogicalDisk():
            if disk.DriveType == 0 and disk.Size:  # Unknown type, might be MTP
                drive_path = disk.DeviceID + "\\"
                logger.info(f"Found unknown type drive (possibly MTP): {drive_path}")
                print(f"Found unknown type drive (possibly MTP): {drive_path}")
                
                # Test if we can access it
                try:
                    test_files = os.listdir(drive_path)
                    print(f"  Can access {drive_path}, files: {len(test_files)}")
                    root.destroy()
                    return drive_path
                except:
                    print(f"  Cannot access {drive_path}")
        
        # If mobile devices found, prompt user
        if mobile_devices:
            device_list = '\n'.join(f"• {device}" for device in mobile_devices)
            response = messagebox.askyesno(
                "Phone/Mobile Device Detected!",
                f"Found your device(s):\n{device_list}\n\n"
                "Your phone is connected but appears as an MTP device\n"
                "(this is normal for modern Android phones).\n\n"
                "Click 'Yes' to browse and select your phone's folder\n"
                "(look for your phone name under 'This PC'),\n"
                "or 'No' to retry detection."
            )
            
            if response:
                folder_path = filedialog.askdirectory(
                    title="Select Device Folder (usually under 'This PC' > Your Phone)"
                )
                if folder_path:
                    folder_path = folder_path.replace("/", "\\")
                    if not folder_path.endswith("\\"):
                        folder_path += "\\"
                    
                    logger.info(f"User selected device folder: {folder_path}")
                    print(f"Selected device folder: {folder_path}")
                    
                    # Test folder access
                    try:
                        files = glob.glob(os.path.join(folder_path, "*.*"))
                        print(f"Files in folder: {len(files)}")
                        if files[:5]:  # Show first 5 files
                            print(f"Sample files: {[os.path.basename(f) for f in files[:5]]}")
                        logger.info(f"Successfully accessed folder with {len(files)} files")
                    except Exception as e:
                        print(f"Warning: Could not list files in folder: {e}")
                        logger.warning(f"Could not list files: {e}")
                    
                    root.destroy()
                    return folder_path
                else:
                    logger.warning("No folder selected for mobile device")
            else:
                root.destroy()
                return detect_card()  # Retry
        
        # Step 4: Nothing found, give options
        response = messagebox.askyesno(
            "No Device Detected",
            "No memory card or phone detected automatically.\n\n"
            "Make sure your phone is:\n"
            "1. Connected via USB\n"
            "2. Set to 'File Transfer' or 'MTP' mode\n"
            "3. Unlocked and trusted this computer\n\n"
            "Click 'Yes' to retry, or 'No' to select a folder manually."
        )
        
        if response:
            root.destroy()
            return detect_card()  # Retry
        else:
            folder_path = filedialog.askdirectory(
                title="Manually Select Phone/Device Folder"
            )
            if folder_path:
                folder_path = folder_path.replace("/", "\\")
                if not folder_path.endswith("\\"):
                    folder_path += "\\"
                logger.info(f"Manual folder selection: {folder_path}")
                root.destroy()
                return folder_path
            else:
                logger.warning("No manual folder selected")
                messagebox.showerror("Error", "No folder selected. Exiting.")
                root.destroy()
                return None
                
    except Exception as e:
        logger.error(f"Error in detect_card: {str(e)}")
        print(f"Error: {str(e)}")
        messagebox.showerror("Error", f"Detection failed: {str(e)}")
        root.destroy()
        return None

if __name__ == "__main__":
    print("Starting enhanced device detection...")
    print("Make sure your phone is connected and set to File Transfer mode.")
    
    path = detect_card()
    if path:
        print(f"\nSUCCESS! Detected path: {path}")
        logger.info(f"Final detected path: {path}")
    else:
        print("\nDetection failed - no path returned")
        logger.error("Detection failed - no path returned")