# main.py
import streamlit as st
import split_logic
import pandas as pd
import time
import gemini_ocr
import io
from PIL import Image

def main():
    st.set_page_config(layout="wide")
    st.title("🧾 Gemini Powered Receipt Splitter")

    # Initialize session state
    st.session_state.setdefault('parsed_data', None)
    st.session_state.setdefault('last_uploaded_file_info', None)
    # st.session_state.setdefault('ocr_backend', 'Detecting...') # Not relevant anymore

    # --- UI Layout ---
    col_upload, col_display = st.columns([1, 2])

    with col_upload:
        st.header("1. Upload Receipt")
        uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        st.caption("Powered by Google Gemini")


    # Initialize variables
    store_name = None
    receipt_date = None # Renamed from 'date' for clarity
    receipt_time_val = None
    items = []
    detected_tax_str = "0.0" # We'll derive this from Gemini's output
    detected_tip_str = "0.0" # We'll derive this from Gemini's output

    if uploaded_file is not None:
        current_file_info = (uploaded_file.name, uploaded_file.size)

        if st.session_state.parsed_data is None or st.session_state.last_uploaded_file_info != current_file_info:
            st.session_state.last_uploaded_file_info = current_file_info
            st.session_state.parsed_data = None # Reset for new file

            with col_upload:
                # Display image using PIL directly for consistency
                from PIL import Image as PILImage # Alias to avoid conflict if Image was used elsewhere
                try:
                    image_bytes_for_display = uploaded_file.getvalue() # Get bytes for display
                    pil_image = PILImage.open(io.BytesIO(image_bytes_for_display))
                    st.image(pil_image, caption="Uploaded Receipt", use_column_width=True)
                except Exception as e:
                    st.error(f"Could not display image: {e}")


            with st.spinner(f'⚙️ Processing receipt with Gemini... This may take a few moments.'):
                processing_start_time = time.time()
                
                # Get image bytes for Gemini
                # uploaded_file.seek(0) # Reset file pointer if already read by st.image
                image_bytes_for_gemini = uploaded_file.getvalue() # Get fresh bytes

                # Call Gemini OCR
                parsed_data_dict = gemini_ocr.extract_receipt_data_with_gemini(image_bytes_for_gemini)
                
                st.session_state.parsed_data = parsed_data_dict

                if "Error" in parsed_data_dict:
                    st.error(f"Gemini processing error: {parsed_data_dict['Error']}")
                elif not parsed_data_dict.get('line_items') and not parsed_data_dict.get('total_amount'):
                    st.warning("Gemini processed the image, but could not extract significant details (e.g., no items or total amount found). Please check the receipt quality or prompt.")
                else:
                    num_items_found = len(parsed_data_dict.get('line_items', []))
                    st.success(f"Gemini successfully processed the receipt! Found {num_items_found} line item(s).")
                
                print(f"Total Gemini processing time: {time.time() - processing_start_time:.2f} seconds")
                print("Data from Gemini:", parsed_data_dict)


    # --- Display and Interaction Logic (largely the same, but fed by Gemini's output) ---
    parsed_data_from_state = st.session_state.get('parsed_data')

    with col_display:
        st.header("2. Review & Split Bill")
        if parsed_data_from_state:
            if "Error" in parsed_data_from_state:
                # Error already shown above, could add more specific instructions here
                st.info("Please review any error messages or try uploading again.")
            
            # Extract data from Gemini's structured output
            store_name = parsed_data_from_state.get("store_name")
            receipt_date = parsed_data_from_state.get("transaction_date")
            receipt_time_val = parsed_data_from_state.get("transaction_time")
            
            # Convert Gemini's line_items to the format expected by the rest of the app
            gemini_line_items = parsed_data_from_state.get("line_items", [])
            items = []
            if isinstance(gemini_line_items, list):
                for g_item in gemini_line_items:
                    if isinstance(g_item, dict): # Ensure item is a dict
                        items.append({
                            "item": g_item.get("item_description", "Unknown Item"),
                            "qty": str(g_item.get("quantity", 1.0)), # Ensure qty is string for split_logic initially
                            "price": str(g_item.get("item_total_price", 0.0)) # Ensure price is string
                        })
            
            # Aggregate tax from tax_details
            total_tax_from_gemini = 0.0
            if isinstance(parsed_data_from_state.get("tax_details"), list):
                for tax_item in parsed_data_from_state["tax_details"]:
                    if isinstance(tax_item, dict) and isinstance(tax_item.get("tax_amount"), (int, float)):
                        total_tax_from_gemini += tax_item.get("tax_amount", 0.0)
            detected_tax_str = str(total_tax_from_gemini)
            
            # Get tip
            tip_from_gemini = parsed_data_from_state.get("tip_amount", 0.0)
            detected_tip_str = str(tip_from_gemini if isinstance(tip_from_gemini, (int, float)) else 0.0)

            # Display extracted information
            if store_name: st.subheader(f"🏪 Store: {store_name}")
            if receipt_date or receipt_time_val:
                st.write(f"🗓️ Date: {receipt_date if receipt_date else 'N/A'} | 🕒 Time: {receipt_time_val if receipt_time_val else 'N/A'}")

            # --- Bill Splitting UI (mostly unchanged from your previous version) ---
            st.markdown("---")
            st.subheader("👥 People Splitting")
            person_names_input = st.text_input(
                "Enter names (comma-separated)", value="Person 1, Person 2", key="person_names_input"
            )
            person_names = [name.strip() for name in person_names_input.split(',') if name.strip()] or ["Person 1"]
            num_people = len(person_names)
            st.write(f"Splitting among: **{', '.join(person_names)}** ({num_people} people)")

            st.subheader("🛒 Assign Items")
            item_assignments = []

            if not items:
                st.info("No items extracted by Gemini or an error occurred. You can manually add items below.")

            with st.expander("Manually Add Item", expanded=(not items)):
                with st.form("manual_item_entry", clear_on_submit=True):
                    manual_item_name = st.text_input("Item Name")
                    manual_item_qty = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
                    manual_item_price = st.number_input("Total Price for this quantity", min_value=0.0, step=1000.0, format="%.2f")
                    
                    submitted_manual = st.form_submit_button("➕ Add Manual Item")
                    if submitted_manual and manual_item_name and manual_item_price >= 0:
                        # Ensure items list exists in session state for manual additions
                        if st.session_state.parsed_data is None: st.session_state.parsed_data = {}
                        current_items_list = st.session_state.parsed_data.get("items_for_ui", []) # Use a different key if needed
                        if not isinstance(current_items_list, list): current_items_list = []
                        
                        current_items_list.append({
                            "item": manual_item_name, "qty": str(manual_item_qty), "price": str(manual_item_price)
                        })
                        st.session_state.parsed_data["items_for_ui"] = current_items_list # Update the list
                        # We also need to update the 'items' variable used by the loop below
                        items = current_items_list # This updates the local 'items'
                        st.success(f"Added '{manual_item_name}' manually!")
                        st.rerun()

            if items:
                for i, item_data in enumerate(items):
                    item_key_suffix = item_data.get('item', f'unknown_item_{i}')
                    col_item, col_qty_price, col_assign = st.columns([3, 2, 3])
                    with col_item: st.write(f"**{item_data.get('item', 'Unknown Item')}**")
                    with col_qty_price:
                        try:
                            qty_float = split_logic.clean_and_convert_number(item_data.get('qty', '1'), is_quantity=True) or 1.0
                            qty_display = int(qty_float) if qty_float == int(qty_float) else qty_float
                            price_float = split_logic.clean_and_convert_number(item_data.get('price', '0.0')) or 0.0
                        except Exception as e:
                            qty_display = item_data.get('qty', '1'); price_float = 0.0
                            print(f"Error converting qty/price for display: {e}")
                        st.write(f"{qty_display} x IDR {price_float:,.2f}")
                    with col_assign:
                        assigned_to = st.multiselect(
                            "Assigned to:", person_names,
                            default=person_names if num_people == 1 else [],
                            key=f"assign_{i}_{item_key_suffix.replace(' ', '_').replace('.', '_')}" # Sanitize key
                        )
                    item_assignments.append({"item_details": item_data, "assigned_to": assigned_to})
            
            st.subheader("💸 Tax & Tip")
            default_tax_value = split_logic.clean_and_convert_number(detected_tax_str) or 0.0
            default_tip_value = split_logic.clean_and_convert_number(detected_tip_str) or 0.0

            tax_amount_input = st.number_input("Tax Amount (IDR)", min_value=0.0, value=default_tax_value, step=100.0, key="tax_input", format="%.2f")
            tip_amount_input = st.number_input("Tip Amount (IDR)", min_value=0.0, value=default_tip_value, step=100.0, key="tip_input", format="%.2f")

            if st.button("🧮 Calculate Split", type="primary", use_container_width=True):
                # ... (The rest of your calculate split and display logic from previous main.py can go here) ...
                # Ensure it correctly uses 'item_assignments', 'tax_amount_input', 'tip_amount_input', 'person_names'
                if not item_assignments and (tax_amount_input == 0 and tip_amount_input == 0) :
                    st.warning("Please add/assign items or enter tax/tip before calculating.")
                elif not item_assignments and (tax_amount_input > 0 or tip_amount_input > 0):
                    st.info("No items assigned. Tax/tip will be split evenly among all people.")
                    split_results = split_logic.calculate_split([], str(tax_amount_input), str(tip_amount_input), person_names)
                else: # Items are assigned
                    split_results = split_logic.calculate_split(item_assignments, str(tax_amount_input), str(tip_amount_input), person_names)

                if 'split_results' in locals(): # Check if split_results was defined
                    st.subheader("📊 Split Results")
                    if isinstance(split_results, dict) and "Error" in split_results:
                        st.error(split_results["Error"])
                    else:
                        summary_data = []
                        for person, data in split_results.items():
                            summary_data.append({
                                "Person": person, "Subtotal": data.get("subtotal", 0.0),
                                "Tax": data.get("tax", 0.0), "Tip": data.get("tip", 0.0), "Total": data.get("total", 0.0)
                            })
                        summary_df = pd.DataFrame(summary_data)
                        for col_format in ["Subtotal", "Tax", "Tip", "Total"]:
                            summary_df[col_format] = summary_df[col_format].apply(lambda x: f"IDR {x:,.2f}")
                        st.dataframe(summary_df.set_index("Person"), use_container_width=True)

                        st.subheader("🧾 Item Breakdown per Person")
                        for person, data in split_results.items():
                            if data.get("items"):
                                with st.expander(f"{person}'s Items ({len(data['items'])} items) - Subtotal: IDR {data.get('subtotal', 0):,.2f}"):
                                    item_breakdown_data = []
                                    for item_share in data["items"]:
                                        item_breakdown_data.append({
                                            "Item": item_share.get("item", "N/A"),
                                            "Qty Shared": f"{item_share.get('qty_share', 0):.2f}",
                                            "Unit Price": f"IDR {item_share.get('price_per_unit', 0):,.2f}",
                                            "Your Cost": f"IDR {item_share.get('share_cost', 0):,.2f}"
                                        })
                                    item_breakdown_df = pd.DataFrame(item_breakdown_data)
                                    st.dataframe(item_breakdown_df, use_container_width=True)
        else:
            st.info("👋 Welcome! Please upload a receipt image to start splitting your bill.")
            # ... (Your welcome message) ...

if __name__ == "__main__":
    main()
