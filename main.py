        with st.spinner('Extracting text from receipt...'):
            # ...
            text = ocr_utils.extract_text_from_image(uploaded_file)

        # ...

        with st.spinner('Parsing extracted text...'):
             items = ocr_utils.parse_receipt_text(text)
