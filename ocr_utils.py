import easyocr
import re
from PIL import Image # PIL is imported but not used in extract_text_from_image, could be removed if not needed elsewhere

def extract_text_from_image(uploaded_file):
    """
    Extracts text from an uploaded image file using EasyOCR.

    Args:
        uploaded_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The file uploaded via Streamlit.

    Returns:
        str: The extracted text.
    """
    # Initialize EasyOCR reader for English.
    # Consider moving this outside the function or using caching (st.cache_resource)
    # if initialization is slow and happens frequently.
    # Note: The main.py file now has a cached reader function, but this function
    # currently initializes its own. For performance, this function should ideally
    # accept the cached reader as an argument.
    reader = easyocr.Reader(['en'])

    # Read the content of the uploaded file as bytes
    image_bytes = uploaded_file.getvalue()

    # Pass the bytes content to EasyOCR's readtext function
    results = reader.readtext(image_bytes)

    text = ""
    # Sort results by vertical position to improve text flow
    # Sort by y-coordinate of the top-left corner of the bounding box
    results.sort(key=lambda r: r[0][0][1])

    for (bbox, text_content, prob) in results:
        text += text_content + "\n"
    return text

def parse_receipt_text(text):
    """
    Parses the raw text extracted from a receipt to find items, quantities, and prices.

    Args:
        text (str): The raw text extracted from the receipt.

    Returns:
        list: A list of dictionaries, where each dictionary represents an item
              with keys 'item', 'qty', and 'price'.
    """
    print("\n--- Raw Text for Parsing ---")
    print(text)
    print("----------------------------\n")

    items = []
    # Updated regex pattern to handle commas and dots in the price part.
    # Looks for:
    # 1. Item name (any characters, non-greedy) - captured in group 1
    # 2. One or more spaces
    # 3. Quantity (one or more digits) - captured in group 2
    # 4. One or more spaces (allowing for no 'x' or other separators)
    # 5. Price (digits, commas, or dots) - captured as a string in group 3
    # We will clean the price string after matching.
    pattern = re.compile(r"(.+?)\s+(\d+)\s+([\d,.]+)", re.IGNORECASE)

    # Alternative pattern if quantity is often 1 and not explicitly listed,
    # looking for Item Name followed by Price near the end of the line.
    # pattern_no_qty = re.compile(r"(.+?)\s+([\d]+\.?\d*)$", re.IGNORECASE)


    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            item_name = match.group(1).strip()
            quantity = int(match.group(2))
            price_str = match.group(3)

            # Clean the price string: remove commas, ensure decimal is a dot
            cleaned_price_str = price_str.replace(',', '') # Remove thousands separators
            # If the last character before potential decimal is a comma, assume it's a decimal comma
            # This is a simple heuristic, might need refinement for different locales
            if '.' not in cleaned_price_str and ',' in price_str:
                 # If original had comma but cleaned doesn't have dot, and comma was last non-digit/dot char
                 # This logic is tricky. Let's assume comma is always thousands separator for now.
                 pass # Commas are just removed

            try:
                price = float(cleaned_price_str)
            except ValueError:
                print(f"Warning: Could not convert price '{price_str}' to float after cleaning.")
                continue # Skip this item if price is invalid

            # Basic validation: price should probably be > 0
            if price > 0:
                 items.append({"item": item_name, "qty": quantity, "price": price})
        # Add logic here to try alternative patterns if the first one fails on a line
        # elif pattern_no_qty.search(line):
        #    ... handle items with implied quantity 1 ...

    return items
