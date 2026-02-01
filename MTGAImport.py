import cv2
import pytesseract
import re
import requests

# Uncomment and set the path if Tesseract is not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    text = pytesseract.image_to_string(img)
    return text

def clean_ocr_text(text):
    # Remove common OCR artifacts: punctuation, special chars, etc.
    text = re.sub(r'[®_@=–—:;,()\[\]{}\\*•“”‘’´`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Common OCR misreads fixes - expand as needed
    fixes = {
        'Ge ': '3 ',
        '6a': '3',
        '8 ': '3 ',
        '9 ': '4 ',
        'Gx': '',
        'ptimistic': 'Optimistic',
        'GqGpiteturHexmage': 'Spiteful Hexmage',
        'Sal ibxitter': 'Bitter',
        'Deep Deep-CavernBat': 'Deep-Cavern Bat',
        'vGeamkip': 'Seam Rip',
        'AGandit’s Tatent8': "Bandit's Talent",
        'Grchenemy\'s Charm': "Archenemy's Charm",
        'ACesyAcolyte': 'Elegy Acolyte',
    }
    for wrong, correct in fixes.items():
        text = text.replace(wrong, correct)
    
    return text

def parse_card_lines(text):
    deck = []
    # Find all non-overlapping matches of count + card name
    pattern = re.compile(r'(\d+)\s+([A-Za-z0-9 \-\',\/]+)')
    matches = pattern.finditer(text)
    for match in matches:
        count = int(match.group(1))
        name = match.group(2).strip()
        deck.append({'card_name': name, 'count': count})
    return deck



def get_scryfall_arena_card_info(card_name):
    query_name = card_name.replace(' ', '+')
    url = f"https://api.scryfall.com/cards/search?q=!{query_name}+arena:1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['total_cards'] > 0:
            card = data['data'][0]
            return {
                "card_name": card['name'],
                "set_code": card['set'].upper(),
                "collector_number": card['collector_number']
            }
        else:
            print(f"No Arena-legal card found for '{card_name}'.")
    else:
        print(f"Scryfall request failed for '{card_name}', status code {response.status_code}")
    return None

def build_decklist(deck):
    deck_output = []
    for entry in deck:
        print(f"Querying Scryfall for: {entry['card_name']}")  # Debug output
        card_info = get_scryfall_arena_card_info(entry['card_name'])
        if card_info:
            deck_output.append(f"{entry['count']} {card_info['card_name']} ({card_info['set_code']}) {card_info['collector_number']}")
        else:
            deck_output.append(f"{entry['count']} {entry['card_name']}")
    return deck_output

def main(image_paths):
    combined_text = ""
    for path in image_paths:
        combined_text += extract_text_from_image(path) + "\n"
    cleaned_text = clean_ocr_text(combined_text)
    print("Cleaned OCR Text:\n", cleaned_text)  # Debug
    
    deck = parse_card_lines(cleaned_text)
    print("Parsed deck entries:")
    for entry in deck:
        print(entry['count'], entry['card_name'])
    
    decklist = build_decklist(deck)
    print("Deck")
    for line in decklist:
        print(line)
        
# Example usage with your image paths
image_files = [
    'C:/Users/aigis/MTGAImageImport/images/deck1.png',
    'C:/Users/aigis/MTGAImageImport/images/deck2.png'
]

if __name__ == "__main__":
    main(image_files)
