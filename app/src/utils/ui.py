import streamlit as st
import streamlit.components.v1 as components


def apply_theme():
    dark_theme_css = """
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
    """
    st.markdown(dark_theme_css, unsafe_allow_html=True)


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


def update_tax_amount():
    st.session_state.tax_amount_input = st.session_state.tax_input_s3
    st.rerun()


def update_tip_amount():
    st.session_state.tip_amount_input = st.session_state.tip_input_s3
    st.rerun()
