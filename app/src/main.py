import streamlit as st
from components.ui import (
    inject_custom_html,
    render_current_step,
    render_receipt_details,
)
from state import initialize_session_state, reset_app_state_full
from utils.api import API_KEY, load_shared_split_data_from_api
from utils.ui import apply_theme


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Split Bill",
        page_icon=None,
        layout="centered",
        initial_sidebar_state="auto",
    )

    initialize_session_state()
    apply_theme()
    inject_custom_html()

    st.title("Split Bill")
    st.markdown('<div id="main-content">', unsafe_allow_html=True)

    if not API_KEY:
        st.error(
            "API_KEY environment variable is not set. Please set it to connect to the backend API.",
        )
        st.stop()

    if st.session_state.processing_status != "idle":
        st.progress(st.session_state.processing_progress / 100)
        st.info(f"Status: {st.session_state.processing_status}")

    is_view_mode = (
        st.session_state.view_split_id is not None
        and st.session_state.loaded_share_data is not None
    )
    data_source = (
        st.session_state.loaded_share_data
        if is_view_mode
        else st.session_state.parsed_data
    )

    if (
        data_source
        and "Error" not in data_source
        and (st.session_state.current_step > 0)
    ):
        render_receipt_details(data_source, is_view_mode)

    gemini_items_list = []
    if data_source and "Error" not in data_source:
        raw_items = data_source.get("line_items", [])
        if isinstance(raw_items, list):
            for item_struct in raw_items:
                if isinstance(item_struct, dict):
                    qty_val = item_struct.get("quantity", 1.0)
                    price_val = item_struct.get("item_total_price", 0.0)
                    gemini_items_list.append(
                        {
                            "item": item_struct.get("item_description", "Unknown"),
                            "qty": str(qty_val),
                            "price": str(price_val),
                        }
                    )

    render_current_step(gemini_items_list, is_view_mode)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize session state first to prevent KeyError
    initialize_session_state()

    if st.session_state.pop("_start_new_split_requested", False):
        if st.session_state.pop("_force_query_params_clear", False):
            st.query_params.clear()
        reset_app_state_full()
        st.rerun()

    query_params = st.query_params
    shared_split_id_from_url = query_params.get("split_id")
    if isinstance(shared_split_id_from_url, list):
        shared_split_id_from_url = (
            shared_split_id_from_url[0] if shared_split_id_from_url else None
        )

    if shared_split_id_from_url and (
        st.session_state.view_split_id != shared_split_id_from_url
        or st.session_state.view_split_id is None
    ):
        reset_app_state_full()
        st.session_state.view_split_id = shared_split_id_from_url
        if not API_KEY:
            st.error(
                "API_KEY environment variable is not set. Cannot load shared split data."
            )
            st.stop()
        loaded_data_dict = load_shared_split_data_from_api(shared_split_id_from_url)
        if loaded_data_dict:
            st.session_state.loaded_share_data = loaded_data_dict
            st.session_state.parsed_data = loaded_data_dict.get("original_parsed_data")
            st.session_state.person_names_list = loaded_data_dict.get(
                "person_names", []
            )
            st.session_state.item_assignments = loaded_data_dict.get(
                "item_assignments", []
            )
            st.session_state.tax_amount_input = loaded_data_dict.get(
                "user_adjusted_tax", 0.0
            )
            st.session_state.tip_amount_input = loaded_data_dict.get(
                "user_adjusted_tip", 0.0
            )
            st.session_state.split_results = loaded_data_dict.get(
                "calculated_split_results"
            )
            st.session_state.minio_image_object_name = loaded_data_dict.get(
                "minio_image_object_name"
            )
            st.session_state.split_evenly = loaded_data_dict.get(
                "split_evenly_choice", False
            )
            st.session_state.extracted_total_discount = loaded_data_dict.get(
                "total_discount_applied", 0.0
            )
            st.session_state.share_link = loaded_data_dict.get("share_link")
            st.session_state.notes_input = loaded_data_dict.get("notes_text", "")
            st.session_state.payment_details = loaded_data_dict.get(
                "payment_details", {"method": "Cash"}
            )
            st.session_state.current_step = 4
            st.rerun()
        else:
            st.session_state.view_split_id = None
            st.session_state.current_step = 0
            st.rerun()

    main()
