import easyocr
import re
from PIL import Image

def extract_text_from_image(image_path):
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English
    results = reader.readtext(image_path)
    text = ""
    for (bbox, text_content, prob) in results:
        text += text_content + "\n"
    return text

def parse_receipt_text(text):
    items = []
    # Regex to find lines with item name, quantity, and price.  More robust.
    pattern = re.compile(r"([A-Za-z0-9\s&]+)\s+(\d+)\s*x\s*([\d.]+)", re.IGNORECASE)
    for match in pattern.finditer(text):
        item_name = match.group(1).strip()
        quantity = int(match.group(2))
        price = float(match.group(3))
        items.append({"item": item_name, "qty": quantity, "price": price})
    return items
