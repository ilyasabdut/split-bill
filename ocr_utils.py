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
    items = []
    # Regex to find lines with item name, quantity, and price. More robust.
    # This pattern looks for:
    # 1. Item name (alphanumeric, spaces, &) - captured in group 1
    # 2. One or more spaces
    # 3. Quantity (one or more digits) - captured in group 2
    # 4. Optional spaces followed by 'x' followed by optional spaces
    # 5. Price (digits, possibly with a decimal point) - captured in group 3
    pattern = re.compile(r"([A-Za-z0-9\s&]+)\s+(\d+)\s*x\s*([\d.]+)", re.IGNORECASE)

    for match in pattern.finditer(text):
        item_name = match.group(1).strip()
        quantity = int(match.group(2))
        price = float(match.group(3))
        items.append({"item": item_name, "qty": quantity, "price": price})
    return items
