from src.card_detector import detect_card

def test_card_detector():
    print("Testing card detection")

    path = detect_card()
    if path:
        print(f"Detected path: {path}")
    else:
        print("No path detected.")

if __name__ == "__main__":
    test_card_detector()