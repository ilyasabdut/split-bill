import streamlit as st
import ocr_utils
from PIL import Image
import split_logic # Import the new split logic file
import easyocr # Moved import back to the top
import pandas as pd # Import pandas for dataframe display

# Cache the EasyOCR reader to avoid re-initializing it every time
@st.cache_resource
def get_easyocr_reader():
    """Caches the EasyOCR reader initialization."""
    # This will download models the first time it's run
    return easyocr.Reader(['en'])

def main():
    st.title("Receipt OCR and Bill Splitter")

    # Initialize session state for parsed data and file info
    st.session_state.setdefault('parsed_data', None)
    st.session_state.setdefault('last_uploaded_file_info', None) # Store (name, size) tuple

    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

    items = [] # Initialize items list
    detected_tax = 0.0 # Initialize detected_tax
    detected_tip = 0.0 # Initialize detected_tip

    # Check if a file is uploaded AND if it's a new file or no data is parsed yet
    if uploaded_file is not None:
        current_file_info = (uploaded_file.name, uploaded_file.size)

        # Only run OCR and parsing if it's a new file or no data is cached
        if st.session_state.parsed_data is None or st.session_state.last_uploaded_file_info != current_file_info:
            st.session_state.last_uploaded_file_info = current_file_info # Store current file info

            image = Image.open(uploaded_file)
            # Display the image immediately when a new file is uploaded
            st.image(image, caption="Uploaded Receipt", use_container_width=True)

            with st.spinner('Extracting text from receipt...'):
                text = ocr_utils.extract_text_from_image(uploaded_file)

            with st.spinner('Parsing extracted text...'):
                 parsed_data = ocr_utils.parse_receipt_text(text)

            # Store parsed data in session state
            st.session_state.parsed_data = parsed_data

        # Retrieve data from session state for display and interaction
        # This block runs on every rerun after a file is uploaded
        parsed_data_from_state = st.session_state.parsed_data
        items = parsed_data_from_state.get("items", [])
        detected_tax = parsed_data_from_state.get("total_tax", 0.0)
        detected_tip = parsed_data_from_state.get("total_tip", 0.0)

        # Display the image again if data is loaded from state (needed on reruns)
        # This ensures the image stays visible after interactions
        image = Image.open(uploaded_file) # Re-open the file object (Streamlit handles this efficiently)
        st.image(image, caption="Uploaded Receipt", use_container_width=True)


        # --- Start of Bill Splitting UI (always shown if file is uploaded and parsed_data exists) ---
        if st.session_state.parsed_data is not None:

            st.subheader("Bill Splitting")

            # Input for person names
            person_names_input = st.text_input(
                "Enter names of people splitting (comma-separated)",
                value="Person 1, Person 2", # Default value
                key="person_names_input"
            )

            # Generate person names list from input
            if person_names_input.strip():
                person_names = [name.strip() for name in person_names_input.split(',') if name.strip()]
            else:
                # Fallback to a default if input is empty
                person_names = ["Person 1"]

            # Ensure at least one person exists
            if not person_names:
                 person_names = ["Person 1"]

            # Update num_people based on the number of names entered
            num_people = len(person_names)
            st.write(f"Splitting among: {', '.join(person_names)}")


            st.subheader("Assign Items")

            # List to store item assignments
            item_assignments = []

            if not items:
                 st.info("No items were automatically parsed from the receipt. You can manually add items below (feature not yet implemented) or try a different receipt.")
                 # Placeholder for manual item entry (future feature)
                 # st.button("Add Item Manually") # Example

            # Iterate through parsed items and add assignment widgets
            for i, item in enumerate(items):
                col1, col2, col3 = st.columns([3, 1, 2]) # Adjust column widths as needed
                with col1:
                    st.write(f"**{item['item']}**")
                with col2:
                     # Changed currency symbol from $ to IDR
                     st.write(f"{item['qty']} x IDR {item['price']:.2f}")
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
            # Input for tax and tip (manual for now, default to detected)
            tax_amount = st.number_input("Tax Amount (IDR)", min_value=0.0, value=detected_tax, step=0.01, key="tax_input")
            tip_amount = st.number_input("Tip Amount (IDR)", min_value=0.0, value=detected_tip, step=0.01, key="tip_input")


            # Button to calculate split
            if st.button("Calculate Split"):
                # Call the split logic function with assignments
                # The split_logic function will need to be updated to handle item_assignments
                # Pass item_assignments, tax, tip, and the list of person_names
                split_results = split_logic.calculate_split(item_assignments, tax_amount, tip_amount, person_names)

                st.subheader("Split Results:")
                # Display the results in a more readable format
                if isinstance(split_results, dict) and "Error" in split_results:
                     st.error(split_results["Error"])
                else:
                    # Create a list of dictionaries for the summary table
                    summary_data = []
                    for person, data in split_results.items():
                        summary_data.append({
                            "Person": person,
                            "Subtotal": data["subtotal"],
                            "Tax": data["tax"],
                            "Tip": data["tip"],
                            "Total": data["total"]
                        })

                    # Use pandas DataFrame for a nice table display
                    summary_df = pd.DataFrame(summary_data)
                    # Format currency columns - Changed currency symbol from $ to IDR
                    for col in ["Subtotal", "Tax", "Tip", "Total"]:
                         summary_df[col] = summary_df[col].apply(lambda x: f"IDR {x:.2f}")

                    st.dataframe(summary_df.set_index("Person")) # Set Person as index

                    # Optional: Display item details per person using expanders
                    st.subheader("Item Breakdown per Person")
                    for person, data in split_results.items():
                        if data["items"]:
                            with st.expander(f"{person}'s Items"):
                                item_breakdown_data = []
                                for item_share in data["items"]:
                                    item_breakdown_data.append({
                                        "Item": item_share["item"],
                                        "Qty": item_share["qty"],
                                        # Changed currency symbol from $ to IDR
                                        "Original Price": f"IDR {item_share['price']:.2f}",
                                        # Changed currency symbol from $ to IDR
                                        "Your Share Cost": f"IDR {item_share['share_cost']:.2f}"
                                    })
                                item_breakdown_df = pd.DataFrame(item_breakdown_data)
                                st.dataframe(item_breakdown_df)
                        else:
                             st.write(f"{person} has no assigned items.")

        # --- End of Bill Splitting UI ---


    # Added an else block for the initial state before file upload
    else:
        st.info("Please upload a receipt image to begin.")


if __name__ == "__main__":
    main()
