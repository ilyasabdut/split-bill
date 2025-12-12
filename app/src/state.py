import streamlit as st


def initialize_session_state():
    """Initializes all the session state variables."""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "view_split_id" not in st.session_state:
        st.session_state.view_split_id = None
    if "loaded_share_data" not in st.session_state:
        st.session_state.loaded_share_data = None
    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None
    if "last_uploaded_file_info" not in st.session_state:
        st.session_state.last_uploaded_file_info = None
    if "uploaded_image_bytes" not in st.session_state:
        st.session_state.uploaded_image_bytes = None
    if "processed_image_bytes_for_minio_base64" not in st.session_state:
        st.session_state.processed_image_bytes_for_minio_base64 = None
    if "minio_image_object_name" not in st.session_state:
        st.session_state.minio_image_object_name = None
    if "person_names_list" not in st.session_state:
        st.session_state.person_names_list = ["Person 1", "Person 2"]
    if "current_name_input" not in st.session_state:
        st.session_state.current_name_input = ""
    if "item_assignments" not in st.session_state:
        st.session_state.item_assignments = []
    if "tax_amount_input" not in st.session_state:
        st.session_state.tax_amount_input = 0.0
    if "tip_amount_input" not in st.session_state:
        st.session_state.tip_amount_input = 0.0
    if "split_results" not in st.session_state:
        st.session_state.split_results = None
    if "share_link" not in st.session_state:
        st.session_state.share_link = None
    if "split_evenly" not in st.session_state:
        st.session_state.split_evenly = False
    if "extracted_subtotal_from_gemini" not in st.session_state:
        st.session_state.extracted_subtotal_from_gemini = 0.0
    if "extracted_total_discount" not in st.session_state:
        st.session_state.extracted_total_discount = 0.0
    if "notes_input" not in st.session_state:
        st.session_state.notes_input = ""
    if "payment_details" not in st.session_state:
        st.session_state.payment_details = {
            "method": "Cash",
            "bank_name": None,
            "account_id": None,
            "account_holder": None,
            "e_wallet_provider": None,
        }
    if "notes_text" not in st.session_state:
        st.session_state.notes_text = ""
    if "_start_new_split_requested" not in st.session_state:
        st.session_state._start_new_split_requested = False
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = "idle"  # idle, processing, success, error
    if "processing_progress" not in st.session_state:
        st.session_state.processing_progress = 0


def reset_app_state_full():
    """Resets the entire app state to its initial values."""
    keys_to_reset = [
        "current_step",
        "parsed_data",
        "last_uploaded_file_info",
        "uploaded_image_bytes",
        "processed_image_bytes_for_minio_base64",
        "minio_image_object_name",
        "item_assignments",
        "split_results",
        "share_link",
        "view_split_id",
        "loaded_share_data",
        "split_evenly",
        "extracted_subtotal_from_gemini",
        "extracted_total_discount",
        "processing_status",
        "processing_progress",
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)

    # Re-initialize with defaults
    initialize_session_state()


def reset_to_step(step_number: int, full_reset: bool = False):
    """Resets the app state to a specific step."""
    st.session_state.current_step = step_number
    if full_reset:
        st.session_state._start_new_split_requested = True
        st.session_state._force_query_params_clear = True
    else:
        if step_number <= 2:
            st.session_state.split_results = None
            st.session_state.share_link = None
        if step_number <= 1:
            st.session_state.item_assignments = []
            st.session_state.split_evenly = False
        if step_number <= 0:
            st.session_state._start_new_split_requested = True
