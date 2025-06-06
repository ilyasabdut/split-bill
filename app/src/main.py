import sys
import os
import streamlit as st
import pandas as pd
import requests
import base64
import io
from PIL import Image as PILImage, UnidentifiedImageError
import json
import time # Still needed for creation_timestamp in metadata for share link
import streamlit.components.v1 as components

# Removed: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuration for FastAPI backend URL
FASTAPI_API_URL = os.environ.get("FASTAPI_API_URL", "http://localhost:8000") # Updated for Docker Compose internal network
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8501") # For generating share links
API_KEY = os.environ.get("API_KEY") # Get API key from environment variable

st.set_page_config(
    page_title="Split Bill",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Umami Analytics Script ---
components.html(
    f"""
    <script async defer 
        data-website-id="0e96ff0f-f450-4e3b-8446-ad2a232b1268" 
        src="https://umami.ilyasabdut.loseyourip.com/script.js"> 
    </script>
    """,
    height=0 # Set height to 0 as the script has no visible output
)


# --- SESSION STATE INITIALIZATION (MOVED TO TOP) ---
if 'current_step' not in st.session_state: st.session_state.current_step = 0
if 'view_split_id' not in st.session_state: st.session_state.view_split_id = None
if 'loaded_share_data' not in st.session_state: st.session_state.loaded_share_data = None
if 'parsed_data' not in st.session_state: st.session_state.parsed_data = None
if 'last_uploaded_file_info' not in st.session_state: st.session_state.last_uploaded_file_info = None
if 'uploaded_image_bytes' not in st.session_state: st.session_state.uploaded_image_bytes = None
if 'processed_image_bytes_for_minio_base64' not in st.session_state: st.session_state.processed_image_bytes_for_minio_base64 = None # Now base64 string
if 'minio_image_object_name' not in st.session_state: st.session_state.minio_image_object_name = None
if 'person_names_list' not in st.session_state: st.session_state.person_names_list = ["Person 1", "Person 2"]
if 'current_name_input' not in st.session_state: st.session_state.current_name_input = ""
if 'item_assignments' not in st.session_state: st.session_state.item_assignments = []
if 'tax_amount_input' not in st.session_state: st.session_state.tax_amount_input = 0.0
if 'tip_amount_input' not in st.session_state: st.session_state.tip_amount_input = 0.0
if 'split_results' not in st.session_state: st.session_state.split_results = None
if 'share_link' not in st.session_state: st.session_state.share_link = None
if 'split_evenly' not in st.session_state: st.session_state.split_evenly = False
if 'extracted_subtotal_from_gemini' not in st.session_state: st.session_state.extracted_subtotal_from_gemini = 0.0
if 'extracted_total_discount' not in st.session_state: st.session_state.extracted_total_discount = 0.0
# Removed access_token and logged_in_user from session state
# --- END SESSION STATE INITIALIZATION ---

# --- Helper functions for on_change callbacks ---
def update_tax_amount():
    st.session_state.tax_amount_input = st.session_state.tax_input_s3
    st.rerun()

def update_tip_amount():
    st.session_state.tip_amount_input = st.session_state.tip_input_s3
    st.rerun()

# --- Constants and Configuration ---
MAX_IMAGE_SIZE_MB = 2
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

def reset_app_state_full():
    st.session_state.current_step = 0; st.session_state.parsed_data = None
    st.session_state.last_uploaded_file_info = None; st.session_state.uploaded_image_bytes = None
    st.session_state.processed_image_bytes_for_minio_base66 = None; st.session_state.minio_image_object_name = None
    st.session_state.item_assignments = []; st.session_state.split_results = None
    st.session_state.share_link = None; st.session_state.view_split_id = None
    st.session_state.loaded_share_data = None; 
    # Do not clear query_params here in reset_app_state_full directly, 
    # as it might be called when loading a shared link before the main check.
    # It's cleared in the main block after successful load.
    st.session_state.split_evenly = False
    st.session_state.extracted_subtotal_from_gemini = 0.0
    st.session_state.extracted_total_discount = 0.0

def reset_to_step(step_number: int):
    st.session_state.current_step = step_number
    if step_number <= 2: st.session_state.split_results = None; st.session_state.share_link = None
    if step_number <= 1: st.session_state.item_assignments = []; st.session_state.split_evenly = False
    if step_number <= 0: 
        reset_app_state_full()
        # If resetting to step 0 (start new), explicitly clear query params
        # so that if user was on a shared link, they truly start fresh.
        if "split_id" in st.query_params:
            # Remove all query params from the URL bar
            st.experimental_set_query_params()  # clears all query params

def get_api_headers():
    headers = {}
    if API_KEY: # Use the global API_KEY
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers

def load_shared_split_data_from_api(split_id: str) -> dict[str, any] | None:
    try:
        headers = get_api_headers()
        response = requests.get(f"{FASTAPI_API_URL}/view-split/{split_id}", headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading shared split data: {e}")
        return None

def main_app_flow():
    st.title("🧾 Split Bill")

    if not API_KEY:
        st.error("API_KEY environment variable is not set. Please set it to connect to the backend API.")
        st.stop() # Stop execution if API_KEY is missing

    # Check for split_id in query params and reset state if present
    query_params = st.query_params
    shared_split_id_from_url = query_params.get("split_id")
    if shared_split_id_from_url:
        reset_app_state_full()  # Reset state for a new split
        st.session_state.view_split_id = None  # Clear view_split_id to start fresh
        st.session_state.current_step = 0  # Start at the first step
        st.experimental_set_query_params()  # Clear query params from the URL

    # --- STEP 0: Upload Image ---
    if st.session_state.current_step == 0:
        st.header("Step 1: Upload Receipt")
        uploaded_file = st.file_uploader("Select a receipt image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file is not None:
            if uploaded_file.size > MAX_IMAGE_SIZE_BYTES: st.error(f"Image too large ({uploaded_file.size / (1024*1024):.2f} MB). Max {MAX_IMAGE_SIZE_MB} MB."); st.stop()
            current_file_info = (uploaded_file.name, uploaded_file.size)
            if st.session_state.parsed_data is None or st.session_state.last_uploaded_file_info != current_file_info:
                st.session_state.last_uploaded_file_info = current_file_info; st.session_state.parsed_data = None
                raw_image_bytes = uploaded_file.getvalue(); st.session_state.uploaded_image_bytes = raw_image_bytes
                
                response = None # Initialize response to None
                with st.spinner(f'⚙️ Processing receipt...'):
                    try:
                        files = {'file': (uploaded_file.name, raw_image_bytes, uploaded_file.type)}
                        headers = get_api_headers()
                        response = requests.post(f"{FASTAPI_API_URL}/upload-receipt", files=files, headers=headers)
                        response.raise_for_status()
                        api_response = response.json()

                        st.session_state.parsed_data = api_response['parsed_data']
                        st.session_state.processed_image_bytes_for_minio_base64 = api_response.get('processed_image_bytes_base64')
                        st.session_state.extracted_subtotal_from_gemini = api_response['extracted_subtotal_from_gemini']
                        st.session_state.extracted_total_discount = api_response['extracted_total_discount']

                        if st.session_state.processed_image_bytes_for_minio_base64:
                            try:
                                pil_image_display = PILImage.open(io.BytesIO(base64.b64decode(st.session_state.processed_image_bytes_for_minio_base64)))
                                st.image(pil_image_display, caption="Processing this image...", use_container_width=True)
                            except Exception as e: st.error(f"Could not display image: {e}")
                        
                        st.success(f"Receipt processed!"); st.session_state.current_step = 1; st.rerun()

                    except requests.exceptions.RequestException as e:
                        st.error(f"API Error during receipt processing: {e}")
                        if response is not None and response.status_code: # Check if response is not None
                            st.error(f"Status Code: {response.status_code}")
                            try:
                                error_detail = response.json().get("detail", "No additional detail.")
                                # Specific error handling for "NOT_A_RECEIPT"
                                if response.status_code == 400 and "not appear to be a receipt" in error_detail:
                                    st.warning("⚠️ The uploaded image does not appear to be a receipt. Please upload a valid receipt image.")
                                else:
                                    st.error(f"Detail: {error_detail}")
                            except json.JSONDecodeError:
                                st.error(f"Response: {response.text}")
                        st.stop()
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
                        st.stop()
            elif st.session_state.parsed_data is not None and "Error" not in st.session_state.parsed_data:
                if st.button("Proceed with current receipt", type="primary"): st.session_state.current_step = 1; st.rerun()

    is_view_mode = st.session_state.view_split_id is not None and st.session_state.loaded_share_data is not None
    data_source = st.session_state.loaded_share_data if is_view_mode else st.session_state.parsed_data
    gemini_items_list = []
    store_name, receipt_date, receipt_time_val = None, None, None
    total_tax_from_processor_str, tip_from_processor_str = "0.0", "0.0"
    display_image_bytes_source_base64 = None # Now base64 string

    if data_source and "Error" not in data_source:
        store_name = data_source.get("store_name"); receipt_date = data_source.get("transaction_date"); receipt_time_val = data_source.get("transaction_time")
        if is_view_mode: display_image_bytes_source_base64 = data_source.get('image_bytes_for_display_base64')
        elif st.session_state.processed_image_bytes_for_minio_base64: display_image_bytes_source_base64 = st.session_state.processed_image_bytes_for_minio_base64
        
        raw_items = data_source.get("line_items", [])
        if isinstance(raw_items, list):
            for item_struct in raw_items:
                if isinstance(item_struct, dict): 
                    # Ensure 'qty' and 'price' are strings for consistency with original logic
                    qty_val = item_struct.get("quantity", 1.0)
                    price_val = item_struct.get("item_total_price", 0.0)
                    gemini_items_list.append({
                        "item": item_struct.get("item_description", "Unknown"), 
                        "qty": str(qty_val), 
                        "price": str(price_val)
                    })
        tax_sum = 0.0
        if isinstance(data_source.get("tax_details"), list):
            for tax_item in data_source.get("tax_details", []):
                if isinstance(tax_item, dict) and isinstance(tax_item.get("tax_amount"), (int, float)): tax_sum += tax_item.get("tax_amount", 0.0)
        total_tax_from_processor_str = str(tax_sum)
        tip_val = data_source.get("tip_amount", 0.0); tip_from_processor_str = str(tip_val if isinstance(tip_val, (int, float)) else 0.0)
    
    should_show_receipt_expander = bool(data_source and "Error" not in data_source and (st.session_state.current_step > 0))
    if should_show_receipt_expander:
        expanded_state = (st.session_state.current_step > 0 and st.session_state.current_step < 4) or is_view_mode
        with st.expander("Receipt Details", expanded=expanded_state):
            if store_name: st.write(f"🏪 **Store:** {store_name}")
            if receipt_date or receipt_time_val: st.write(f"🗓️ **Date:** {receipt_date or 'N/A'} | 🕒 **Time:** {receipt_time_val or 'N/A'}")
            if display_image_bytes_source_base64:
                try: 
                    img_disp = PILImage.open(io.BytesIO(base64.b64decode(display_image_bytes_source_base64)))
                    st.image(img_disp, caption="Receipt Image", width=400)
                except Exception as e: st.caption(f"Could not display image: {e}")

    if st.session_state.current_step == 1 and not is_view_mode:
        st.header("Step 2: Who's Splitting?")
        name_to_add = st.text_input("Enter a person's name to add:", key="current_name_input_field", value=st.session_state.current_name_input, on_change=lambda: (setattr(st.session_state, 'current_name_input', st.session_state.current_name_input_field), st.rerun()))
        if st.button("➕ Add Person", use_container_width=True):
            typed_name = st.session_state.current_name_input.strip()
            if typed_name and typed_name not in st.session_state.person_names_list: st.session_state.person_names_list.append(typed_name); st.session_state.current_name_input = ""; st.rerun()
            elif not typed_name: st.warning("Please enter a name.")
            elif typed_name in st.session_state.person_names_list: st.warning(f"'{typed_name}' is already in the list.")
        st.write("People added:")
        if not st.session_state.person_names_list: st.caption("No people added yet.")
        else:
            for i, name in enumerate(st.session_state.person_names_list):
                col1, col2 = st.columns([0.85, 0.15])
                with col1: st.markdown(f"<div style='background-color:#2E323A;color:white;padding:6px 12px;border-radius:5px;margin-bottom:5px;'>{name}</div>", unsafe_allow_html=True)
                with col2:
                    if st.button("➖", key=f"remove_person_{i}_{name.replace(' ','_')}", help=f"Remove {name}", use_container_width=True): st.session_state.person_names_list.pop(i); st.rerun()
            st.markdown(f"Total: **{len(st.session_state.person_names_list)}** people")
        st.markdown("---"); col_back1, col_next1 = st.columns(2)
        with col_back1:
            if st.button("⬅️ Change Receipt", use_container_width=True): reset_to_step(0); st.rerun()
        with col_next1:
            if st.button("Next: Assign Items ➡️", type="primary", use_container_width=True, disabled=(not st.session_state.person_names_list)): st.session_state.current_step = 2; st.rerun()

    if st.session_state.current_step == 2 and not is_view_mode:
        st.header("Step 3: How to Split Items?")
        st.session_state.split_evenly = st.checkbox("Split the entire bill (after discounts, before tax/tip) evenly among everyone?", value=st.session_state.split_evenly, key="split_evenly_checkbox")
        st.markdown("---")
        items_to_assign_ui = gemini_items_list; current_ui_assignments = []
        all_individual_items_assigned_flag = True if items_to_assign_ui else False
        if st.session_state.split_evenly:
            st.info("The bill subtotal will be split evenly. Individual item assignment below is disabled.")
            all_individual_items_assigned_flag = True 
        elif not items_to_assign_ui: st.warning("No items extracted. If not splitting evenly, please go back."); all_individual_items_assigned_flag = False
        else:
            st.write("For each item, select who shared it:")
            for i, item_data_ui in enumerate(items_to_assign_ui):
                item_key_suffix = item_data_ui.get('item', f'unknown_item_{i}'); col_item_detail, col_assign_person = st.columns([0.6, 0.4])
                with col_item_detail:
                    st.markdown(f"**{item_data_ui.get('item', 'Unknown Item')}**")
                    try:
                        qty_float = float(item_data_ui.get('qty', '1'))
                        qty_display = int(qty_float) if qty_float == int(qty_float) else qty_float
                        price_float = float(item_data_ui.get('price', '0.0'))
                    except ValueError: # Fallback if conversion fails
                        qty_display = item_data_ui.get('qty', '1')
                        price_float = 0.0
                    st.caption(f"{qty_display} x IDR {price_float:,.2f}")
                with col_assign_person:
                    default_sel = []
                    assigned_to = st.multiselect("Shared by:", st.session_state.person_names_list, default=default_sel, key=f"assign_{i}_{item_key_suffix.replace(' ', '_').replace('.', '_').replace('/', '_')}", label_visibility="collapsed")
                current_ui_assignments.append({"item_details": item_data_ui, "assigned_to": assigned_to})
                if not assigned_to: all_individual_items_assigned_flag = False
                if i < len(items_to_assign_ui) - 1: st.markdown("---")
        st.markdown("---"); col_back2, col_next2 = st.columns(2)
        with col_back2:
            if st.button("⬅️ Back to People", use_container_width=True): 
                if not st.session_state.split_evenly : st.session_state.item_assignments = current_ui_assignments
                reset_to_step(1); st.rerun()
        with col_next2:
            next_button_disabled_step2 = (not st.session_state.split_evenly) and ((not items_to_assign_ui) or (not all_individual_items_assigned_flag))
            if st.button("Next: Tax & Tip ➡️", type="primary", use_container_width=True, disabled=next_button_disabled_step2):
                if not st.session_state.split_evenly: st.session_state.item_assignments = current_ui_assignments
                else: st.session_state.item_assignments = [] 
                st.session_state.current_step = 3; st.rerun()
            if not st.session_state.split_evenly and not all_individual_items_assigned_flag and items_to_assign_ui: st.caption("⚠️ Please assign all items if not splitting evenly.")

    if st.session_state.current_step == 3 and not is_view_mode:
        st.header("Step 4: Tax, Tip & Calculate")
        if st.session_state.extracted_total_discount > 0: st.info(f"An overall discount of IDR {st.session_state.extracted_total_discount:,.2f} will be applied.")
        
        # Use the extracted values from API response as initial values
        # Ensure that parsed_data is not None before attempting to access its keys
        initial_tax = float(st.session_state.parsed_data.get("tax_details", [{}])[0].get("tax_amount") or 0.0) if st.session_state.parsed_data and st.session_state.parsed_data.get("tax_details") else 0.0
        initial_tip = float(st.session_state.parsed_data.get("tip_amount") or 0.0) if st.session_state.parsed_data else 0.0

        st.session_state.tax_amount_input = st.number_input("Tax (IDR)", min_value=0.0, value=initial_tax, step=100.0, key="tax_input_s3", format="%.2f", on_change=update_tax_amount)
        st.session_state.tip_amount_input = st.number_input("Tip (IDR)", min_value=0.0, value=initial_tip, step=100.0, key="tip_input_s3", format="%.2f", on_change=update_tip_amount)
        st.markdown("---"); col_back3, col_calc = st.columns(2)
        with col_back3:
            if st.button("⬅️ Back to Assign Items", use_container_width=True): reset_to_step(2); st.rerun()
        with col_calc:
            if st.button("🧮 Calculate Split & Get Link", type="primary", use_container_width=True):
                final_assignments_for_calc = st.session_state.item_assignments
                if not st.session_state.split_evenly and not final_assignments_for_calc and (st.session_state.tax_amount_input == 0 and st.session_state.tip_amount_input == 0):
                    st.warning("Please assign items or enter tax/tip.")
                else:
                    # Prepare data for API request
                    calculate_payload = {
                        "person_names": st.session_state.person_names_list,
                        "item_assignments": final_assignments_for_calc,
                        "tax_amount_input": st.session_state.tax_amount_input,
                        "tip_amount_input": st.session_state.tip_amount_input,
                        "split_evenly": st.session_state.split_evenly,
                        "extracted_subtotal_from_gemini": st.session_state.extracted_subtotal_from_gemini,
                        "extracted_total_discount": st.session_state.extracted_total_discount,
                        "processed_image_bytes_for_minio_base64": st.session_state.processed_image_bytes_for_minio_base64,
                        "original_parsed_data": st.session_state.parsed_data
                    }
                    with st.spinner("Calculating split and generating link..."):
                        try:
                            headers = get_api_headers()
                            response = requests.post(f"{FASTAPI_API_URL}/calculate-split", json=calculate_payload, headers=headers)
                            response.raise_for_status()
                            api_response = response.json()

                            st.session_state.split_results = api_response['split_results']
                            st.session_state.share_link = f"{APP_BASE_URL}?split_id={api_response['split_id']}" # Use Streamlit's base URL for sharing
                            st.success(f"Split saved! Share link: ID: {api_response['split_id']}")
                            st.session_state.current_step = 4; st.rerun()

                        except requests.exceptions.RequestException as e:
                            st.error(f"API Error during split calculation: {e}")
                            if response is not None and response.status_code: # Check if response is not None
                                st.error(f"Status Code: {response.status_code}")
                                try:
                                    error_detail = response.json().get("detail", "No additional detail.")
                                    st.error(f"Detail: {error_detail}")
                                except json.JSONDecodeError:
                                    st.error(f"Response: {response.text}")
                            st.stop()
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
                            st.stop()

    if st.session_state.current_step == 4:
        st.header("🎉 Split Results 🎉")
        if st.session_state.share_link and not is_view_mode: st.success("Share this link:"); st.code(st.session_state.share_link)
        results_for_display = st.session_state.split_results if not is_view_mode else (st.session_state.loaded_share_data.get("calculated_split_results") if st.session_state.loaded_share_data else None)
        discount_applied_in_view = 0.0
        if is_view_mode and st.session_state.loaded_share_data: discount_applied_in_view = st.session_state.loaded_share_data.get("total_discount_applied", 0.0)
        elif not is_view_mode: discount_applied_in_view = st.session_state.extracted_total_discount
        if discount_applied_in_view > 0: st.info(f"An overall discount of IDR {discount_applied_in_view:,.2f} was applied.")
        if results_for_display:
            if isinstance(results_for_display, dict) and "Error" in results_for_display: st.error(results_for_display["Error"])
            else:
                summary_data = [];
                for person, data in results_for_display.items(): summary_data.append({"Person": person, "Subtotal": data.get("subtotal", 0.0), "Tax": data.get("tax", 0.0), "Tip": data.get("tip", 0.0), "Total": data.get("total", 0.0)})
                summary_df = pd.DataFrame(summary_data)
                cols_to_format = [col for col in ["Subtotal", "Tax", "Tip", "Total"] if col in summary_df.columns]
                for col_format in cols_to_format: summary_df[col_format] = summary_df[col_format].apply(lambda x: f"IDR {x:,.2f}")
                st.dataframe(summary_df.set_index("Person"), use_container_width=True)
                st.subheader("🧾 Item Breakdown per Person")
                people_for_breakdown = st.session_state.person_names_list
                if is_view_mode and st.session_state.loaded_share_data: people_for_breakdown = st.session_state.loaded_share_data.get("person_names", [])
                for person_name_iter in people_for_breakdown:
                    data = results_for_display.get(person_name_iter)
                    if data and data.get("items"):
                        with st.expander(f"{person_name_iter}'s Items ({len(data['items'])} items) - Subtotal: IDR {data.get('subtotal', 0):,.2f}"):
                            item_breakdown_data_list = []
                            for item_share in data["items"]: item_breakdown_data_list.append({"Item": item_share.get("item", "N/A"), "Qty Shared": f"{item_share.get('qty_share', 0):.3f}", "Unit Price": f"IDR {item_share.get('price_per_unit', 0):,.2f}", "Your Cost": f"IDR {item_share.get('share_cost', 0):,.2f}"})
                            item_breakdown_df = pd.DataFrame(item_breakdown_data_list)
                            item_breakdown_df.index = pd.RangeIndex(start=1, stop=len(item_breakdown_df) + 1, step=1); item_breakdown_df.index.name = "No."
                            st.dataframe(item_breakdown_df, use_container_width=True)
        else: st.warning("No results to display.")
        st.markdown("---")
        if st.button("✨ Start New Split", type="primary", use_container_width=True):
            # Remove query params from the browser URL, reset state, then rerun
            st.experimental_set_query_params()  # clears all query params
            st.session_state.view_split_id = None
            st.session_state.current_step = 0
            reset_app_state_full()  # full state reset without re-adding query params
            st.rerun()
        if not is_view_mode:
            if st.button("⬅️ Adjust Split Details", use_container_width=True):
                st.session_state.share_link = None 
                if st.session_state.item_assignments or not st.session_state.split_evenly : reset_to_step(2)
                else: reset_to_step(3)
                st.rerun()

if __name__ == "__main__":
    query_params = st.query_params
    shared_split_id_from_url = query_params.get("split_id")
    if isinstance(shared_split_id_from_url, list): shared_split_id_from_url = shared_split_id_from_url[0] if shared_split_id_from_url else None
    
    # Only load if view_split_id is not already this ID, or if it's None (first load of a shared link)
    if shared_split_id_from_url and (st.session_state.view_split_id != shared_split_id_from_url or st.session_state.view_split_id is None) :
        print(f"URL has split_id: {shared_split_id_from_url}. Current view_split_id: {st.session_state.view_split_id}")
        reset_app_state_full() # Reset state before loading a potentially new shared link
        st.session_state.view_split_id = shared_split_id_from_url # Mark that we are attempting to view this
        
        # Check for API_KEY before loading shared data if it's a view mode
        if not API_KEY:
            st.error("API_KEY environment variable is not set. Cannot load shared split data.")
            st.stop()
        
        loaded_data_dict = load_shared_split_data_from_api(shared_split_id_from_url) # Use the new API function
        if loaded_data_dict:
            print(f"Successfully loaded data for shared split_id: {shared_split_id_from_url}")
            st.session_state.loaded_share_data = loaded_data_dict
            st.session_state.parsed_data = loaded_data_dict.get("original_parsed_data")
            st.session_state.person_names_list = loaded_data_dict.get("person_names", [])
            st.session_state.item_assignments = loaded_data_dict.get("item_assignments", [])
            st.session_state.tax_amount_input = loaded_data_dict.get("user_adjusted_tax", 0.0)
            st.session_state.tip_amount_input = loaded_data_dict.get("user_adjusted_tip", 0.0)
            st.session_state.split_results = loaded_data_dict.get("calculated_split_results")
            st.session_state.minio_image_object_name = loaded_data_dict.get("minio_image_object_name")
            st.session_state.split_evenly = loaded_data_dict.get("split_evenly_choice", False)
            st.session_state.extracted_total_discount = loaded_data_dict.get("total_discount_applied", 0.0)
            st.session_state.share_link = loaded_data_dict.get("share_link") # Also load the share link itself
            
            st.session_state.current_step = 4 # Go directly to results view
            # DO NOT clear query_params here, let them persist in the URL for bookmarking/sharing
            st.rerun()
        else:
            print(f"Failed to load data for shared split_id: {shared_split_id_from_url}. Resetting.")
            st.session_state.view_split_id = None # Reset if loading failed
            st.session_state.current_step = 0 
            # No need to clear query_params here, if user refreshes, it will try again. If they navigate away, it's fine.
            st.rerun()
            
    main_app_flow()
