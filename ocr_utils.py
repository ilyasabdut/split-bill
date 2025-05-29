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
    results.sort(key=lambda r: r[0][0][1]) # Sort by y-coordinate of the first point

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
    # More flexible regex pattern:
    # Looks for:
    # 1. Item name (any characters, non-greedy) - captured in group 1
    # 2. One or more spaces
    # 3. Quantity (one or more digits) - captured in group 2
    # 4. One or more spaces (allowing for no 'x' or other separators)
    # 5. Price (digits, optionally with a decimal point and digits after) - captured in group 3
    # This pattern is more lenient with separators between Qty and Price.
    # It assumes the order is Item Name, Quantity, Price.
    pattern = re.compile(r"(.+?)\s+(\d+)\s+([\d]+\.?\d*)", re.IGNORECASE)

    # Alternative pattern if quantity is often 1 and not explicitly listed,
    # looking for Item Name followed by Price near the end of the line.
    # pattern_no_qty = re.compile(r"(.+?)\s+([\d]+\.?\d*)$", re.IGNORECASE)


    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            item_name = match.group(1).strip()
            quantity = int(match.group(2))
            price = float(match.group(3))
            # Basic validation: price should probably be > 0
            if price > 0:
                 items.append({"item": item_name, "qty": quantity, "price": price})
        # Add logic here to try alternative patterns if the first one fails on a line
        # elif pattern_no_qty.search(line):
        #    ... handle items with implied quantity 1 ...

    return items
