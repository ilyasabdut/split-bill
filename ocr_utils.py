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
    This version attempts to handle price-item-quantity across multiple lines
    based on the provided example text structure.

    Args:
        text (str): The raw text extracted from the receipt.

    Returns:
        list: A list of dictionaries, where each dictionary represents an item
              with keys 'item', 'qty', and 'price'.
    """
    print("\n--- Raw Text for Parsing ---")
    print(text)
    print("----------------------------\n")

    lines = text.strip().splitlines()
    items = []
    i = 0

    # Regex for price: digits, commas, dots, potentially at the start/end of the line
    # Allows for optional currency symbols or spaces
    price_pattern = re.compile(r"^\s*[\$\£\€]?\s*([\d,.]+)\s*$", re.IGNORECASE)
    # Regex for quantity: digits, optional dot and digits, potentially at the start/end of the line
    quantity_pattern = re.compile(r"^\s*(\d+\.?\d*)\s*$", re.IGNORECASE)
    # Regex for item name: looks like text, contains at least two letters, not just numbers or symbols
    item_name_pattern = re.compile(r"[A-Za-z]{2,}")

    while i < len(lines):
        line = lines[i].strip()

        # Attempt to match the multi-line pattern: Price -> Item Name -> Quantity
        # Check if current line is a price, next is item name, line after is quantity
        if i + 2 < len(lines):
            price_match = price_pattern.match(line)
            if price_match:
                potential_item_name_line = lines[i+1].strip()
                potential_quantity_line = lines[i+2].strip()

                # Check if the next line looks like an item name
                if item_name_pattern.search(potential_item_name_line):
                     # Check if the line after that looks like a quantity
                     quantity_match = quantity_pattern.match(potential_quantity_line)

                     if quantity_match:
                        # Found the sequence: Price (line i), Item Name (line i+1), Quantity (line i+2)
                        price_str = price_match.group(1)
                        item_name = potential_item_name_line
                        quantity_str = quantity_match.group(1)

                        # Clean and convert price
                        cleaned_price_str = price_str.replace(',', '') # Remove thousands separators
                        try:
                            price = float(cleaned_price_str)
                        except ValueError:
                            print(f"Warning: Could not convert price '{price_str}' to float after cleaning. Skipping sequence starting at line {i+1}.")
                            i += 1 # Move to the next line
                            continue # Continue loop

                        # Convert quantity
                        try:
                            quantity = float(quantity_str) # Use float for 1.0, 2.0 etc.
                            # Convert to int if it's a whole number like 1.0 -> 1
                            if quantity.is_integer():
                                quantity = int(quantity)
                        except ValueError:
                             print(f"Warning: Could not convert quantity '{quantity_str}' to number. Skipping sequence starting at line {i+1}.")
                             i += 1 # Move to the next line
                             continue # Continue loop


                        # Basic validation: price and quantity should be > 0
                        if price > 0 and quantity > 0:
                             items.append({"item": item_name, "qty": quantity, "price": price})
                             i += 3 # Consume these three lines and move to the next potential item start
                             continue # Successfully parsed a multi-line item, continue loop from new position

        # If the multi-line pattern didn't match starting at line i,
        # check for a single-line pattern as a fallback.
        # This pattern looks for Item Name, Quantity, and Price all on the same line.
        # It's less likely to match the provided receipt structure but good as a fallback.
        single_line_pattern = re.compile(r"(.+?)\s+(\d+)\s+([\d,.]+)", re.IGNORECASE)
        single_match = single_line_pattern.search(line)
        if single_match:
            item_name = single_match.group(1).strip()
            quantity_str = single_match.group(2)
            price_str = single_match.group(3)

            # Clean and convert price
            cleaned_price_str = price_str.replace(',', '')
            try:
                price = float(cleaned_price_str)
            except ValueError:
                print(f"Warning: Could not convert price '{price_str}' to float after cleaning. Skipping single-line match on line {i+1}.")
                i += 1 # Move to the next line
                continue # Continue loop

            # Convert quantity
            try:
                quantity = int(quantity_str) # Single line pattern often implies integer quantity
            except ValueError:
                 print(f"Warning: Could not convert quantity '{quantity_str}' to integer. Skipping single-line match on line {i+1}.")
                 i += 1 # Move to the next line
                 continue # Continue loop

            if price > 0 and quantity > 0:
                 items.append({"item": item_name, "qty": quantity, "price": price})
                 i += 1 # Consume this line
                 continue # Successfully parsed a single-line item, continue loop from new position


        # If neither pattern matched starting at line i, just move to the next line
        i += 1

    # Optional: Add logic here to try and identify TAX, TIP, SUBTOTAL, TOTAL lines
    # based on keywords and price patterns, and return them separately or store them.
    # For now, focusing on item parsing.

    return items
