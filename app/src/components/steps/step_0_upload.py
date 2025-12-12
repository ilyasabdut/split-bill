import streamlit as st
from constants import MAX_IMAGE_SIZE_BYTES, MAX_IMAGE_SIZE_MB
from utils.api import process_receipt_with_feedback


def render_upload_step():
    """Renders the UI for step 0: uploading a receipt."""
    st.header("Step 1: Upload Receipt", anchor="upload-step")
    uploaded_file = st.file_uploader(
        "Select a receipt image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        help="Upload a clear photo of your receipt for best results",
        accept_multiple_files=False,
    )
    if uploaded_file is not None:
        if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
            st.error(
                f"Image too large ({uploaded_file.size / (1024*1024):.2f} MB). Max {MAX_IMAGE_SIZE_MB} MB.",
            )
            st.stop()

        current_file_info = (uploaded_file.name, uploaded_file.size)
        if (
            st.session_state.parsed_data is None
            or st.session_state.last_uploaded_file_info != current_file_info
        ):
            st.session_state.last_uploaded_file_info = current_file_info
            st.session_state.parsed_data = None
            raw_image_bytes = uploaded_file.getvalue()
            st.session_state.uploaded_image_bytes = raw_image_bytes

            with st.container():
                col1, _ = st.columns([3, 1])
                with col1:
                    if st.button(
                        "Process Receipt",
                        type="primary",
                        use_container_width=True,
                        help="Click to start processing your receipt",
                    ):
                        result = process_receipt_with_feedback(
                            uploaded_file, raw_image_bytes
                        )
                        if result:
                            st.success("Receipt processed successfully!")
                            st.session_state.processing_status = "idle"
                            st.session_state.processing_progress = 0
                            st.session_state.current_step = 1
                            st.rerun()
                        else:
                            st.error(
                                "Failed to process receipt. Please try again.",
                            )
                            with st.expander("Recovery Suggestions", expanded=True):
                                st.markdown(
                                    """
                                **Try these solutions:**
                                - Take a clearer, well-lit photo
                                - Make sure the receipt is fully visible
                                - Try uploading a different image
                                - Wait a moment and try again
                                """
                                )
                            st.session_state.processing_status = "idle"
                            st.session_state.processing_progress = 0
