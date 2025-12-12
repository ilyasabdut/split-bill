import requests
import streamlit as st
from constants import BANK_NAMES, E_WALLET_PROVIDERS
from state import reset_to_step
from utils.api import APP_BASE_URL, FASTAPI_API_URL, get_api_headers
from utils.ui import update_tax_amount, update_tip_amount


def render_tax_tip_step():
    """Renders the UI for step 3: adding tax and tip, and calculating the split."""
    st.header("Step 4: Tax, Tip & Calculate")
    if st.session_state.extracted_total_discount > 0:
        st.info(
            f"An overall discount of IDR {st.session_state.extracted_total_discount:,.2f} will be applied."
        )

    initial_tax = (
        float(
            st.session_state.parsed_data.get("tax_details", [{}])[0].get("tax_amount")
            or 0.0
        )
        if st.session_state.parsed_data
        and st.session_state.parsed_data.get("tax_details")
        else 0.0
    )
    initial_tip = (
        float(st.session_state.parsed_data.get("tip_amount") or 0.0)
        if st.session_state.parsed_data
        else 0.0
    )

    st.session_state.tax_amount_input = st.number_input(
        "Tax (IDR)",
        min_value=0.0,
        value=initial_tax,
        step=100.0,
        key="tax_input_s3",
        format="%.2f",
        on_change=update_tax_amount,
    )
    st.session_state.tip_amount_input = st.number_input(
        "Tip (IDR)",
        min_value=0.0,
        value=initial_tip,
        step=100.0,
        key="tip_input_s3",
        format="%.2f",
        on_change=update_tip_amount,
    )

    st.session_state.notes_input = st.text_area(
        "Notes", value=st.session_state.notes_input, key="notes_input_s3"
    )
    payment_method = st.selectbox(
        "Payment Method",
        options=["Cash", "Bank", "E-Wallet", "Other"],
        index=0,
        key="payment_method_selectbox",
    )
    st.session_state.payment_details["method"] = payment_method

    if payment_method == "Bank":
        st.session_state.payment_details["bank_name"] = st.selectbox(
            "Bank Name",
            options=BANK_NAMES,
            index=(
                BANK_NAMES.index(
                    st.session_state.payment_details.get("bank_name") or BANK_NAMES[0]
                )
                if st.session_state.payment_details.get("bank_name") in BANK_NAMES
                else 0
            ),
            key="bank_name_input",
        )
        st.session_state.payment_details["account_id"] = st.text_input(
            "Account Number",
            value=st.session_state.payment_details.get("account_id") or "",
            key="account_id_input",
        )
        st.session_state.payment_details["account_holder"] = st.text_input(
            "Account Holder Name",
            value=st.session_state.payment_details.get("account_holder") or "",
            key="account_holder_input",
        )
    elif payment_method == "E-Wallet":
        st.session_state.payment_details["e_wallet_provider"] = st.selectbox(
            "E-Wallet Provider",
            options=E_WALLET_PROVIDERS,
            index=(
                E_WALLET_PROVIDERS.index(
                    st.session_state.payment_details.get("e_wallet_provider")
                    or E_WALLET_PROVIDERS[0]
                )
                if st.session_state.payment_details.get("e_wallet_provider")
                in E_WALLET_PROVIDERS
                else 0
            ),
            key="e_wallet_provider_input",
        )
        st.session_state.payment_details["account_id"] = st.text_input(
            "E-Wallet Account ID",
            value=st.session_state.payment_details.get("account_id") or "",
            key="e_wallet_account_id_input",
        )
        st.session_state.payment_details["account_holder"] = st.text_input(
            "Account Holder Name",
            value=st.session_state.payment_details.get("account_holder") or "",
            key="e_wallet_account_holder_input",
        )
    st.markdown("---")
    col_back3, col_calc = st.columns(2)
    with col_back3:
        if st.button("Back to Assign Items", use_container_width=True):
            reset_to_step(2)
            st.rerun()
    with col_calc:
        if st.button(
            "Calculate Split & Get Link",
            type="primary",
            use_container_width=True,
        ):
            final_assignments_for_calc = st.session_state.item_assignments
            if (
                not st.session_state.split_evenly
                and not final_assignments_for_calc
                and (
                    st.session_state.tax_amount_input == 0
                    and st.session_state.tip_amount_input == 0
                )
            ):
                st.warning("Please assign items or enter tax/tip.")
            else:
                calculate_payload = {
                    "person_names": st.session_state.person_names_list,
                    "item_assignments": final_assignments_for_calc,
                    "tax_amount_input": st.session_state.tax_amount_input,
                    "tip_amount_input": st.session_state.tip_amount_input,
                    "split_evenly": st.session_state.split_evenly,
                    "extracted_subtotal_from_gemini": st.session_state.extracted_subtotal_from_gemini,
                    "extracted_total_discount": st.session_state.extracted_total_discount,
                    "processed_image_bytes_for_minio_base64": st.session_state.processed_image_bytes_for_minio_base64,
                    "original_parsed_data": st.session_state.parsed_data,
                    "notes_text": st.session_state.notes_input,
                    "payment_details": st.session_state.payment_details,
                }
                with st.spinner("Calculating split and generating link..."):
                    response = None
                    try:
                        headers = get_api_headers()
                        response = requests.post(
                            f"{FASTAPI_API_URL}/splits/calculate",
                            json=calculate_payload,
                            headers=headers,
                        )
                        response.raise_for_status()
                        api_response = response.json()

                        st.session_state.split_results = api_response["split_results"]
                        st.session_state.share_link = (
                            f"{APP_BASE_URL}?split_id={api_response['split_id']}"
                        )
                        st.success(
                            f"Split saved! Share link: ID: {api_response['split_id']}"
                        )
                        st.session_state.current_step = 4
                        st.rerun()

                    except requests.exceptions.RequestException as e:
                        st.error(f"API Error during split calculation: {e}")
                        if response is not None and response.status_code:
                            st.error(f"Status Code: {response.status_code}")
                            try:
                                error_detail = response.json().get(
                                    "detail", "No additional detail."
                                )
                                st.error(f"Detail: {error_detail}")
                            except ValueError:
                                st.error(f"Response: {response.text}")
                        st.stop()
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
                        st.stop()
