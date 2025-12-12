import base64
import io

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image as PILImage

from .steps.step_0_upload import render_upload_step
from .steps.step_1_people import render_people_step
from .steps.step_2_assign_items import render_assign_items_step
from .steps.step_3_tax_tip import render_tax_tip_step
from .steps.step_4_results import render_results_step


def inject_custom_html():
    """Injects custom HTML for analytics, accessibility, and styling."""
    # Try to load external CSS file
    css_content = ""
    try:
        import os

        css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "main.css")
        with open(css_path, "r") as f:
            css_content = f.read()
    except (FileNotFoundError, OSError):
        # Fallback CSS if file not found
        css_content = """
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
        """

    components.html(
        f"""
        <style>
        {css_content}
        </style>
        <a href="#main-content" class="skip-link" aria-label="Skip to main content">Skip to main content</a>
        """,
        height=0,
    )
    components.html(
        """
        <script async defer
            data-website-id="0e96ff0f-f450-4e3b-8446-ad2a232b1268"
            src="https://umami.ilyasabdut.loseyourip.com/script.js">
        </script>
        """,
        height=0,
    )
    components.html(
        """
        <div id="status-announcer" aria-live="polite" aria-atomic="true" style="position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden;"></div>
        """,
        height=0,
    )


def render_receipt_details(data_source, is_view_mode):
    """Renders the receipt details expander."""
    if not data_source or "Error" in data_source:
        return

    store_name = data_source.get("store_name")
    receipt_date = data_source.get("transaction_date")
    receipt_time_val = data_source.get("transaction_time")
    display_image_bytes_source_base64 = None
    if is_view_mode:
        display_image_bytes_source_base64 = data_source.get(
            "image_bytes_for_display_base64"
        )
    elif st.session_state.processed_image_bytes_for_minio_base64:
        display_image_bytes_source_base64 = (
            st.session_state.processed_image_bytes_for_minio_base64
        )

    expanded_state = (
        st.session_state.current_step > 0 and st.session_state.current_step < 4
    ) or is_view_mode
    with st.expander("Receipt Details", expanded=expanded_state):
        if store_name:
            st.write(f"Store: {store_name}")
        if receipt_date or receipt_time_val:
            st.write(
                f"Date: {receipt_date or 'N/A'} | Time: {receipt_time_val or 'N/A'}"
            )
        if display_image_bytes_source_base64:
            try:
                img_disp = PILImage.open(
                    io.BytesIO(base64.b64decode(display_image_bytes_source_base64))
                )
                st.image(img_disp, caption="Receipt Image", width=400)
            except Exception as e:
                st.caption(f"Could not display image: {e}")


def render_current_step(gemini_items_list, is_view_mode):
    """Renders the current step of the app."""
    if st.session_state.current_step == 0:
        render_upload_step()
    elif st.session_state.current_step == 1 and not is_view_mode:
        render_people_step()
    elif st.session_state.current_step == 2 and not is_view_mode:
        render_assign_items_step(gemini_items_list)
    elif st.session_state.current_step == 3 and not is_view_mode:
        render_tax_tip_step()
    elif st.session_state.current_step == 4:
        render_results_step(is_view_mode)
