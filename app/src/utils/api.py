import os
import time
from typing import Any

import requests
import streamlit as st

# Configuration for FastAPI backend URL
FASTAPI_API_URL = os.environ.get("FASTAPI_API_URL", "http://localhost:8000")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8501")
API_KEY = os.environ.get("API_KEY")


def get_api_headers():
    """Prepares headers for API calls."""
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def load_shared_split_data_from_api(split_id: str) -> dict[str, Any] | None:
    """Fetches data for a shared split."""
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


def process_receipt_with_feedback(uploaded_file, raw_image_bytes):
    """Process receipt with real-time progress updates."""
    from .ui import update_status

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
            f"{FASTAPI_API_URL}/receipts/upload",
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
