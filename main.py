import streamlit as st
import ocr_utils
from PIL import Image
import split_logic # Import the new split logic file
import easyocr # Moved import back to the top

# Cache the EasyOCR reader to avoid re-initializing it every time
@st.cache_resource
def get_easyocr_reader():
    """Caches the EasyOCR reader initialization."""
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
            # However, we'll keep the reader initialization inside extract_text_from_image for now,
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
            # st.dataframe(items) # Using dataframe for better display - replaced by assignment UI

            st.subheader("Bill Splitting")

            # Input for number of people
            num_people = st.number_input("Number of people splitting the bill", min_value=1, value=1, step=1, key="num_people_input")

            # Generate default person names
            person_names = [f"Person {i+1}" for i in range(num_people)]

            st.subheader("Assign Items")

            # List to store item assignments
            item_assignments = []

            # Iterate through parsed items and add assignment widgets
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns([3, 1, 2]) # Adjust column widths as needed
                with col1:
                    st.write(f"**{item['item']}**")
                with col2:
                     st.write(f"{item['qty']} x ${item['price']:.2f}")
                with col3:
                    # Multiselect for assigning people to this item
                    assigned_to = st.multiselect(
                        "Assigned to:",
                        person_names,
                        default=person_names if num_people == 1 else [], # Default to all if only 1 person
                        key=f"assign_{i}" # Unique key for each widget
                    )
                # Store the item details and who it's assigned to
                item_assignments.append({"item_details": item, "assigned_to": assigned_to})

            st.subheader("Tax & Tip")
            # Input for tax and tip (manual for now)
            tax_amount = st.number_input("Tax Amount", min_value=0.0, value=0.0, step=0.01, key="tax_input")
            tip_amount = st.number_input("Tip Amount", min_value=0.0, value=0.0, step=0.01, key="tip_input")


            # Button to calculate split
            if st.button("Calculate Split"):
                # Call the split logic function with assignments
                # The split_logic function will need to be updated to handle item_assignments
                split_results = split_logic.calculate_split(item_assignments, tax_amount, tip_amount, person_names)

                st.subheader("Split Results:")
                # Display the results
                if isinstance(split_results, dict) and "Error" in split_results:
                     st.error(split_results["Error"])
                else:
                    # Display results in a more readable format (e.g., table)
                    st.json(split_results) # Using json for now, can format better later

        else:
            st.write("No items found. Please ensure the receipt is clear and the format is supported.")

if __name__ == "__main__":
    main()
