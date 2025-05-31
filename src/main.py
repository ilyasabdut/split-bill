import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# src/main.py
import streamlit as st
from src import split_logic
import pandas as pd
import time
from src import gemini_ocr
import io
from PIL import Image as PILImage, UnidentifiedImageError
import json
import os
from src import minio_utils
from typing import Dict, Any 
import hashlib # For idempotency key

# --- SESSION STATE INITIALIZATION (MOVED TO TOP) ---
if 'current_step' not in st.session_state: st.session_state.current_step = 0
if 'view_split_id' not in st.session_state: st.session_state.view_split_id = None
if 'loaded_share_data' not in st.session_state: st.session_state.loaded_share_data = None
if 'parsed_data' not in st.session_state: st.session_state.parsed_data = None
if 'last_uploaded_file_info' not in st.session_state: st.session_state.last_uploaded_file_info = None
if 'uploaded_image_bytes' not in st.session_state: st.session_state.uploaded_image_bytes = None
if 'processed_image_bytes_for_minio' not in st.session_state: st.session_state.processed_image_bytes_for_minio = None
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
    st.session_state.processed_image_bytes_for_minio = None; st.session_state.minio_image_object_name = None
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
            st.query_params.clear()


def compress_image(image_bytes: bytes, target_size_bytes: int = MAX_IMAGE_SIZE_BYTES, quality: int = 90, min_quality: int = 70) -> bytes | None:
    try:
        img = PILImage.open(io.BytesIO(image_bytes))
        if img.mode not in ('RGB', 'L'): img = img.convert('RGB')
        compressed_bytes = None 
        for q in range(quality, min_quality -1 , -5):
            buffer = io.BytesIO(); img.save(buffer, format="JPEG", quality=q, optimize=True)
            compressed_bytes = buffer.getvalue()
            if len(compressed_bytes) <= target_size_bytes:
                print(f"Image compressed to {len(compressed_bytes)/1024:.2f} KB with quality {q}.")
                return compressed_bytes
        if compressed_bytes and len(compressed_bytes) > target_size_bytes:
            ratio = (target_size_bytes / len(compressed_bytes))**0.5 
            new_width = int(img.width * ratio); new_height = int(img.height * ratio)
            if new_width > 0 and new_height > 0:
                img_resized = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                buffer = io.BytesIO(); img_resized.save(buffer, format="JPEG", quality=min_quality, optimize=True)
                compressed_bytes = buffer.getvalue()
                print(f"Resized/compressed image size: {len(compressed_bytes)/1024:.2f} KB.")
                return compressed_bytes
        return compressed_bytes
    except UnidentifiedImageError: st.error("Cannot identify image file."); return None
    except Exception as e: st.error(f"Image compression error: {e}"); return image_bytes

def load_shared_split_data(split_id: str) -> dict[str, Any] | None:
    metadata = minio_utils.get_metadata_from_minio(split_id)
    if metadata:
        image_bytes_for_display = None
        minio_img_obj_name = metadata.get("minio_image_object_name")
        if minio_img_obj_name:
            base_img_name = minio_img_obj_name.replace(minio_utils.IMAGE_PREFIX, "", 1)
            image_bytes_for_display = minio_utils.get_image_from_minio(base_img_name)
        metadata['image_bytes_for_display'] = image_bytes_for_display if image_bytes_for_display else None
        return metadata
    else: st.error(f"Split data for ID '{split_id}' not found."); return None

def main_app_flow():
    st.title("🧾 Bill Splitter")

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
                st.session_state.processed_image_bytes_for_minio = compress_image(raw_image_bytes)
                if not st.session_state.processed_image_bytes_for_minio: st.error("Image processing failed."); st.stop()
                try:
                    pil_image_display = PILImage.open(io.BytesIO(st.session_state.processed_image_bytes_for_minio))
                    st.image(pil_image_display, caption="Processing this image...", use_container_width=True)
                except Exception as e: st.error(f"Could not display image: {e}")
                with st.spinner(f'⚙️ Processing receipt...'):
                    parsed_data_dict = gemini_ocr.extract_receipt_data_with_gemini(st.session_state.processed_image_bytes_for_minio)
                    st.session_state.parsed_data = parsed_data_dict
                    if "Error" in parsed_data_dict: st.error(f"Processing error: {parsed_data_dict['Error']}")
                    elif not parsed_data_dict.get('line_items') and not parsed_data_dict.get('total_amount'): st.warning("Could not extract details.")
                    else: 
                        subtotal_from_gemini = st.session_state.parsed_data.get("subtotal", 0.0)
                        st.session_state.extracted_subtotal_from_gemini = split_logic.clean_and_convert_number(subtotal_from_gemini) or 0.0
                        total_discount = 0.0
                        if isinstance(st.session_state.parsed_data.get("discounts"), list):
                            for disc in st.session_state.parsed_data.get("discounts", []): total_discount += (split_logic.clean_and_convert_number(disc.get("amount")) or 0.0)
                        st.session_state.extracted_total_discount = total_discount
                        st.success(f"Receipt processed!"); st.session_state.current_step = 1; st.rerun()
            elif st.session_state.parsed_data is not None and "Error" not in st.session_state.parsed_data:
                if st.button("Proceed with current receipt", type="primary"): st.session_state.current_step = 1; st.rerun()

    is_view_mode = st.session_state.view_split_id is not None and st.session_state.loaded_share_data is not None
    data_source = st.session_state.loaded_share_data if is_view_mode else st.session_state.parsed_data
    gemini_items_list = []
    store_name, receipt_date, receipt_time_val = None, None, None
    total_tax_from_processor_str, tip_from_processor_str = "0.0", "0.0"
    display_image_bytes_source = None

    if data_source and "Error" not in data_source:
        store_name = data_source.get("store_name"); receipt_date = data_source.get("transaction_date"); receipt_time_val = data_source.get("transaction_time")
        if is_view_mode: display_image_bytes_source = data_source.get('image_bytes_for_display')
        elif st.session_state.processed_image_bytes_for_minio: display_image_bytes_source = st.session_state.processed_image_bytes_for_minio
        elif st.session_state.uploaded_image_bytes: display_image_bytes_source = st.session_state.uploaded_image_bytes
        raw_items = data_source.get("line_items", [])
        if isinstance(raw_items, list):
            for item_struct in raw_items:
                if isinstance(item_struct, dict): gemini_items_list.append({"item": item_struct.get("item_description", "Unknown"), "qty": str(item_struct.get("quantity", 1.0)), "price": str(item_struct.get("item_total_price", 0.0))})
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
            if display_image_bytes_source:
                try: img_disp = PILImage.open(io.BytesIO(display_image_bytes_source)); st.image(img_disp, caption="Receipt Image", width=400)
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
                        qty_float = split_logic.clean_and_convert_number(item_data_ui.get('qty', '1'), is_quantity=True) or 1.0
                        qty_display = int(qty_float) if qty_float == int(qty_float) else qty_float
                        price_float = split_logic.clean_and_convert_number(item_data_ui.get('price', '0.0')) or 0.0
                    except Exception: qty_display = item_data_ui.get('qty', '1'); price_float = 0.0
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
        initial_tax = split_logic.clean_and_convert_number(total_tax_from_processor_str) or 0.0
        initial_tip = split_logic.clean_and_convert_number(tip_from_processor_str) or 0.0
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
                    idempotency_key_material = {
                        "image_bytes_hash": hashlib.sha256(st.session_state.processed_image_bytes_for_minio or b"").hexdigest(),
                        "people": sorted(st.session_state.person_names_list),
                        "assignments": sorted(
                            [{"item_desc": a["item_details"].get("item", ""), "item_qty": a["item_details"].get("qty", ""), "item_price": a["item_details"].get("price", ""), "assigned_to": sorted(a.get("assigned_to", []))} for a in final_assignments_for_calc],
                            key=lambda x: x["item_desc"]
                        ) if not st.session_state.split_evenly else "SPLIT_EVENLY",
                        "tax": f"{st.session_state.tax_amount_input:.2f}", "tip": f"{st.session_state.tip_amount_input:.2f}",
                        "split_evenly": st.session_state.split_evenly,
                        "extracted_subtotal": f"{st.session_state.extracted_subtotal_from_gemini:.2f}" if st.session_state.split_evenly else None,
                        "extracted_discount": f"{st.session_state.extracted_total_discount:.2f}"
                    }
                    id_hasher = hashlib.sha256(); id_hasher.update(json.dumps(idempotency_key_material, sort_keys=True).encode('utf-8'))
                    split_id = id_hasher.hexdigest()[:12]
                    print(f"Generated content-based split_id: {split_id}")
                    existing_metadata = minio_utils.get_metadata_from_minio(split_id)
                    if existing_metadata and existing_metadata.get("share_link"):
                        st.success("This exact split has been calculated and saved before!")
                        st.session_state.share_link = existing_metadata["share_link"]
                        st.session_state.split_results = existing_metadata.get("calculated_split_results")
                        st.session_state.minio_image_object_name = existing_metadata.get("minio_image_object_name")
                        st.session_state.person_names_list = existing_metadata.get("person_names", st.session_state.person_names_list)
                        st.session_state.item_assignments = existing_metadata.get("item_assignments", st.session_state.item_assignments)
                        st.session_state.tax_amount_input = existing_metadata.get("user_adjusted_tax", st.session_state.tax_amount_input)
                        st.session_state.tip_amount_input = existing_metadata.get("user_adjusted_tip", st.session_state.tip_amount_input)
                        st.session_state.split_evenly = existing_metadata.get("split_evenly_choice", st.session_state.split_evenly)
                        st.session_state.extracted_total_discount = existing_metadata.get("total_discount_applied", st.session_state.extracted_total_discount)
                        st.session_state.parsed_data = existing_metadata.get("original_parsed_data", st.session_state.parsed_data)
                        print(f"Using existing share link for split_id {split_id}: {st.session_state.share_link}")
                    else:
                        print(f"New split or metadata not found for {split_id}. Proceeding.")
                        subtotal_for_even_split = st.session_state.extracted_subtotal_from_gemini if st.session_state.split_evenly else 0.0
                        calculated_split = split_logic.calculate_split(final_assignments_for_calc, str(st.session_state.tax_amount_input), str(st.session_state.tip_amount_input), st.session_state.person_names_list, split_evenly_flag=st.session_state.split_evenly, overall_subtotal_for_even_split=subtotal_for_even_split, total_discount_amount=st.session_state.extracted_total_discount)
                        st.session_state.split_results = calculated_split
                        if "Error" not in calculated_split:
                            st.session_state.minio_image_object_name = None
                            if st.session_state.processed_image_bytes_for_minio:
                                base_image_name = f"{split_id}.jpg"
                                full_image_obj_name = minio_utils.upload_image_to_minio(st.session_state.processed_image_bytes_for_minio, base_image_name, "image/jpeg")
                                if full_image_obj_name: st.session_state.minio_image_object_name = full_image_obj_name
                                else: st.error("Failed to save receipt image to cloud.")
                            app_base_url = os.environ.get("APP_BASE_URL", "http://localhost:8501")
                            current_share_link = f"{app_base_url}?split_id={split_id}"
                            metadata_to_save = {"split_id": split_id, "original_parsed_data": st.session_state.parsed_data, "person_names": st.session_state.person_names_list, "item_assignments": final_assignments_for_calc, "split_evenly_choice": st.session_state.split_evenly, "total_discount_applied": st.session_state.extracted_total_discount, "user_adjusted_tax": st.session_state.tax_amount_input, "user_adjusted_tip": st.session_state.tip_amount_input, "calculated_split_results": calculated_split, "minio_image_object_name": st.session_state.minio_image_object_name, "share_link": current_share_link, "creation_timestamp": time.time()}
                            meta_upload_obj_name = minio_utils.upload_metadata_to_minio(metadata_to_save, split_id)
                            if meta_upload_obj_name: st.session_state.share_link = current_share_link; st.success(f"Split saved! Share link: ID: {split_id}")
                            else: st.error(f"Failed to save split metadata."); st.session_state.share_link = None
                    st.session_state.current_step = 4; st.rerun()

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
        if st.button("✨ Start New Split", type="primary", use_container_width=True): reset_to_step(0); st.rerun()
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
        
        loaded_data_dict = load_shared_split_data(shared_split_id_from_url)
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
