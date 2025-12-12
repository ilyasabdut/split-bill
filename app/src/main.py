import base64
import io
import os
import time
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components
from constants import (
    MAX_IMAGE_SIZE_BYTES,
    MAX_IMAGE_SIZE_MB,
)
from PIL import Image as PILImage

# Configuration for FastAPI backend URL
FASTAPI_API_URL = os.environ.get(
    "FASTAPI_API_URL", "http://localhost:8000"
)  # Updated for Docker Compose internal network
APP_BASE_URL = os.environ.get(
    "APP_BASE_URL", "http://localhost:8501"
)  # For generating share links
API_KEY = os.environ.get("API_KEY")  # Get API key from environment variable

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"


# Apply theme CSS
def apply_theme():
    theme_css = {
        "light": """
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stApp {
            background-color: #ffffff;
        }
        </style>
        """,
        "dark": """
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stButton > button {
            background-color: #1f2937;
            color: #ffffff;
            border: 1px solid #374151;
        }
        .stTextInput > div > div > input {
            background-color: #374151;
            color: #ffffff;
            border: 1px solid #4b5563;
        }
        .stSelectbox > div > div {
            background-color: #374151;
            color: #ffffff;
        }
        .stFileUploader {
            background-color: #374151;
            color: #ffffff;
        }
        .stAlert {
            background-color: #374151;
            color: #ffffff;
        }
        </style>
        """,
    }

    st.markdown(theme_css[st.session_state.theme], unsafe_allow_html=True)


# Apply initial theme
apply_theme()

st.set_page_config(
    page_title="Split Bill",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Accessibility: Add skip link and ARIA labels ---
components.html(
    """
    <style>
    .skip-link {
        position: absolute;
        top: -40px;
        left: 6px;
        background: #000;
        color: #fff;
        padding: 8px;
        text-decoration: none;
        z-index: 1000;
    }
    .skip-link:focus {
        top: 6px;
    }
    </style>
    <a href="#main-content" class="skip-link" aria-label="Skip to main content">Skip to main content</a>
    """,
    height=0,
)

# --- Umami Analytics Script ---
components.html(
    """
    <script async defer
        data-website-id="0e96ff0f-f450-4e3b-8446-ad2a232b1268"
        src="https://umami.ilyasabdut.loseyourip.com/script.js">
    </script>
    """,
    height=0,
)

# --- Theme Toggle ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(
        "🌙" if st.session_state.theme == "light" else "☀️",
        help="Toggle dark/light theme",
        key="theme_toggle",
    ):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        apply_theme()
        st.rerun()

# --- Accessibility: ARIA Live Region for Status Updates ---
components.html(
    """
    <div id="status-announcer" aria-live="polite" aria-atomic="true" style="position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden;"></div>
    """,
    height=0,
)

# --- SESSION STATE INITIALIZATION ---
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

# --- Mobile Responsive CSS ---
components.html(
    """
    <style>
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem;
        }
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            font-size: 16px; /* Prevents zoom on iOS */
        }
        .mobile-stack {
            flex-direction: column;
        }
        .mobile-full-width {
            width: 100%;
        }
    }
    </style>
    """,
    height=0,
)


# --- Enhanced Status Update Function ---
def update_status(message: str, progress: int | None = None):
    """Update processing status with accessibility announcements."""
    if progress is not None:
        st.session_state.processing_progress = max(
            0, min(100, progress)
        )  # Clamp between 0-100

    # Update ARIA live region
    components.html(
        f"""
        <script>
        document.getElementById('status-announcer').textContent = '{message}';
        </script>
        """,
        height=0,
    )

    # Update Streamlit status
    st.session_state.processing_status = message


# --- Helper functions ---
def update_tax_amount():
    st.session_state.tax_amount_input = st.session_state.tax_input_s3
    st.rerun()


def update_tip_amount():
    st.session_state.tip_amount_input = st.session_state.tip_input_s3
    st.rerun()


def reset_app_state_full():
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
    st.session_state.current_step = 0
    st.session_state.person_names_list = ["Person 1", "Person 2"]
    st.session_state.current_name_input = ""
    st.session_state.tax_amount_input = 0.0
    st.session_state.tip_amount_input = 0.0
    st.session_state.processing_status = "idle"
    st.session_state.processing_progress = 0


def reset_to_step(step_number: int, full_reset: bool = False):
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


def get_api_headers():
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def load_shared_split_data_from_api(split_id: str) -> dict[str, Any] | None:
    try:
        headers = get_api_headers()
        response = requests.get(
            f"{FASTAPI_API_URL}/splits/view/{split_id}", headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading shared split data: {e}")
        return None


# --- Enhanced Processing Function with Real-time Feedback ---
def process_receipt_with_feedback(uploaded_file, raw_image_bytes):
    """Process receipt with real-time progress updates."""

    # Step 1: Preparing
    update_status("Preparing to process receipt...", 10)
    time.sleep(0.5)

    # Step 2: Uploading
    update_status("Uploading receipt to server...", 25)

    try:
        files = {
            "file": (
                uploaded_file.name,
                raw_image_bytes,
                uploaded_file.type,
            )
        }
        headers = get_api_headers()

        # Step 3: Processing with OCR
        update_status("Processing receipt with AI (OCR)...", 50)

        response = requests.post(
            f"{FASTAPI_API_URL}/upload-receipt",
            files=files,
            headers=headers,
        )

        # Step 4: Parsing results
        update_status("Parsing receipt data...", 75)

        response.raise_for_status()
        api_response = response.json()

        # Step 5: Finalizing
        update_status("Finalizing results...", 90)

        # Update session state
        st.session_state.parsed_data = api_response["parsed_data"]
        st.session_state.processed_image_bytes_for_minio_base64 = api_response.get(
            "processed_image_bytes_base64"
        )
        st.session_state.extracted_subtotal_from_gemini = api_response[
            "extracted_subtotal_from_gemini"
        ]
        st.session_state.extracted_total_discount = api_response[
            "extracted_total_discount"
        ]

        # Complete
        update_status("Receipt processed successfully!", 100)
        time.sleep(0.5)

        return api_response

    except requests.exceptions.RequestException as e:
        update_status(f"Error processing receipt: {str(e)}", 0)
        return None


# --- Main App Flow ---
def main_app_flow():
    st.title("🧾 Split Bill")

    # Accessibility: Main content identifier
    st.markdown('<div id="main-content">', unsafe_allow_html=True)

    if not API_KEY:
        st.error(
            "API_KEY environment variable is not set. Please set it to connect to the backend API.",
            icon="⚠️",
        )
        st.stop()

    # --- Processing Status Display ---
    if st.session_state.processing_status != "idle":
        st.progress(st.session_state.processing_progress / 100)
        st.info(f"Status: {st.session_state.processing_status}", icon="⏳")

    # --- STEP 0: Upload Image ---
    if st.session_state.current_step == 0:
        st.header("📸 Step 1: Upload Receipt", anchor="upload-step")

        # Mobile-friendly file uploader
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
                    f"📏 Image too large ({uploaded_file.size / (1024*1024):.2f} MB). Max {MAX_IMAGE_SIZE_MB} MB.",
                    icon="⚠️",
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

                # Enhanced processing with progress feedback
                with st.container():
                    # Create columns for better mobile layout
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        if st.button(
                            "🚀 Process Receipt",
                            type="primary",
                            use_container_width=True,
                            help="Click to start processing your receipt",
                        ):

                            # Process with enhanced feedback
                            result = process_receipt_with_feedback(
                                uploaded_file, raw_image_bytes
                            )

                            if result:
                                # Display processed image
                                if (
                                    st.session_state.processed_image_bytes_for_minio_base64
                                ):
                                    try:
                                        pil_image_display = PILImage.open(
                                            io.BytesIO(
                                                base64.b64decode(
                                                    st.session_state.processed_image_bytes_for_minio_base64
                                                )
                                            )
                                        )
                                        st.image(
                                            pil_image_display,
                                            caption="✅ Processed receipt image",
                                            use_container_width=True,
                                        )
                                    except Exception as e:
                                        st.warning(f"Could not display image: {e}")

                                st.success(
                                    "🎉 Receipt processed successfully!", icon="✅"
                                )

                                # Reset processing status
                                st.session_state.processing_status = "idle"
                                st.session_state.processing_progress = 0

                                # Move to next step
                                st.session_state.current_step = 1
                                st.rerun()
                            else:
                                # Enhanced error handling
                                st.error(
                                    "❌ Failed to process receipt. Please try again.",
                                    icon="🚫",
                                )

                                # Recovery suggestions
                                with st.expander(
                                    "💡 Recovery Suggestions", expanded=True
                                ):
                                    st.markdown(
                                        """
                                    **Try these solutions:**
                                    - 📸 Take a clearer, well-lit photo
                                    - ✂️ Make sure the receipt is fully visible
                                    - 🔄 Try uploading a different image
                                    - ⏰ Wait a moment and try again
                                    """
                                    )

                                # Reset processing status
                                st.session_state.processing_status = "idle"
                                st.session_state.processing_progress = 0

    # Close main content div
    st.markdown("</div>", unsafe_allow_html=True)


# Run the app
if __name__ == "__main__":
    main_app_flow()
