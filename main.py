import streamlit as st
import ocr_utils
from PIL import Image
import split_logic # Import the new split logic file
# Removed: import easyocr # Moved inside the cached function

# Cache the EasyOCR reader to avoid re-initializing it every time
@st.cache_resource
def get_easyocr_reader():
    """Caches the EasyOCR reader initialization."""
    # Import easyocr here so it's available within the cached function's scope
    import easyocr
    # This will download models the first time it's run
    return easyocr.Reader(['en'])

def main():
    st.title("Receipt OCR and Bill Splitter")

    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Updated deprecated parameter
        st.image(image, caption="Uploaded Receipt", use_container_width=True)

        # Use a unique key for the uploader to allow re-uploading the same file
        # This is not strictly necessary for this change but good practice
        # st.session_state['uploaded_file'] = uploaded_file

        # Add a spinner while processing
        with st.spinner('Extracting text from receipt...'):
            # Get the cached reader
            # Note: The extract_text_from_image function currently initializes its own reader.
            # For performance, it should ideally accept the cached reader from here.
            # However, to fix the linter error and add the spinner as requested previously,
            # we'll keep the reader initialization inside extract_text_from_image for now,
            # but acknowledge this is a potential optimization.
            # The get_easyocr_reader function is still useful if we refactor ocr_utils later.
            text = ocr_utils.extract_text_from_image(uploaded_file)

        st.subheader("Extracted Text:")
        st.text(text)

        with st.spinner('Parsing extracted text...'):
             items = ocr_utils.parse_receipt_text(text)


        st.subheader("Parsed Items:")
        if items:
            # Display items in a more structured way, maybe preparing for assignment later
            st.dataframe(items) # Using dataframe for better display

            st.subheader("Bill Splitting")

            # Input for number of people
            num_people = st.number_input("Number of people splitting the bill", min_value=1, value=1, step=1)

            # Input for tax and tip (manual for now)
            tax_amount = st.number_input("Tax Amount", min_value=0.0, value=0.0, step=0.01)
            tip_amount = st.number_input("Tip Amount", min_value=0.0, value=0.0, step=0.01)

            # Placeholder for item assignment UI (will be added later)
            st.info("Item assignment UI will go here.")

            # Button to calculate split
            if st.button("Calculate Split"):
                # Call the split logic function (placeholder for now)
                split_results = split_logic.calculate_split(items, tax_amount, tip_amount, num_people)

                st.subheader("Split Results:")
                # Display the results (placeholder for now)
                st.write(split_results)

        else:
            st.write("No items found. Please ensure the receipt is clear and the format is supported.")

if __name__ == "__main__":
    main()
