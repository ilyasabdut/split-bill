import streamlit as st
import ocr_utils
from PIL import Image

def main():
    st.title("Receipt OCR")

    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Receipt", use_column_width=True)

        text = ocr_utils.extract_text_from_image(uploaded_file)
        st.subheader("Extracted Text:")
        st.text(text)

        items = ocr_utils.parse_receipt_text(text)

        st.subheader("Parsed Items:")
        if items:
            st.write(items)
        else:
            st.write("No items found.  Please ensure the receipt is clear and the format is supported.")

if __name__ == "__main__":
    main()
