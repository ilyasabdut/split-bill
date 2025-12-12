import pandas as pd
import streamlit as st
from state import reset_app_state_full, reset_to_step


def render_results_step(is_view_mode):
    """Renders the UI for step 4: displaying the split results."""
    st.header("Split Results")
    if st.session_state.share_link and not is_view_mode:
        st.success("Share this link:")
        st.code(st.session_state.share_link)
    results_for_display = (
        st.session_state.split_results
        if not is_view_mode
        else (
            st.session_state.loaded_share_data.get("calculated_split_results")
            if st.session_state.loaded_share_data
            else None
        )
    )
    discount_applied_in_view = 0.0
    if is_view_mode and st.session_state.loaded_share_data:
        discount_applied_in_view = st.session_state.loaded_share_data.get(
            "total_discount_applied", 0.0
        )
    elif not is_view_mode:
        discount_applied_in_view = st.session_state.extracted_total_discount
    if discount_applied_in_view > 0:
        st.info(
            f"An overall discount of IDR {discount_applied_in_view:,.2f} was applied."
        )
    if results_for_display:
        if isinstance(results_for_display, dict) and "Error" in results_for_display:
            st.error(results_for_display["Error"])
        else:
            summary_data = []
            for person, data in results_for_display.items():
                summary_data.append(
                    {
                        "Person": person,
                        "Subtotal": data.get("subtotal", 0.0),
                        "Tax": data.get("tax", 0.0),
                        "Tip": data.get("tip", 0.0),
                        "Total": data.get("total", 0.0),
                    }
                )
            summary_df = pd.DataFrame(summary_data)
            cols_to_format = [
                col
                for col in ["Subtotal", "Tax", "Tip", "Total"]
                if col in summary_df.columns
            ]
            for col_format in cols_to_format:
                summary_df[col_format] = summary_df[col_format].apply(
                    lambda x: f"IDR {x:,.2f}"
                )
            st.dataframe(summary_df.set_index("Person"), use_container_width=True)
            st.subheader("Item Breakdown per Person")
            people_for_breakdown = st.session_state.person_names_list
            if is_view_mode and st.session_state.loaded_share_data:
                people_for_breakdown = st.session_state.loaded_share_data.get(
                    "person_names", []
                )
            for person_name_iter in people_for_breakdown:
                data = results_for_display.get(person_name_iter)
                if data and data.get("items"):
                    with st.expander(
                        f"{person_name_iter}'s Items ({len(data['items'])} items) - Subtotal: IDR {data.get('subtotal', 0):,.2f}"
                    ):
                        item_breakdown_data_list = []
                        for item_share in data["items"]:
                            item_breakdown_data_list.append(
                                {
                                    "Item": item_share.get("item", "N/A"),
                                    "Qty Shared": f"{item_share.get('qty_share', 0):.3f}",
                                    "Unit Price": f"IDR {item_share.get('price_per_unit', 0):,.2f}",
                                    "Your Cost": f"IDR {item_share.get('share_cost', 0):,.2f}",
                                }
                            )
                        item_breakdown_df = pd.DataFrame(item_breakdown_data_list)
                        item_breakdown_df.index = pd.RangeIndex(
                            start=1, stop=len(item_breakdown_df) + 1, step=1
                        )
                        item_breakdown_df.index.name = "No."
                        st.dataframe(item_breakdown_df, use_container_width=True)
    else:
        st.warning("No results to display.")
    st.markdown("---")

    if st.session_state.notes_input or st.session_state.payment_details:
        with st.expander("Payment Details & Notes", expanded=True):
            payment_details = st.session_state.payment_details
            method = payment_details.get("method")
            if method:
                st.write(f"**Payment Method:** {method}")
                if method == "Bank":
                    if bank_name := payment_details.get("bank_name"):
                        st.write(f"Bank Name: {bank_name}")
                    if account_id := payment_details.get("account_id"):
                        st.write(f"Account Number: {account_id}")
                    if account_holder := payment_details.get("account_holder"):
                        st.write(f"Account Holder: {account_holder}")
                elif method == "E-Wallet":
                    if provider := payment_details.get("e_wallet_provider"):
                        st.write(f"Provider: {provider}")
                    if account_id := payment_details.get("account_id"):
                        st.write(f"Account ID: {account_id}")
                    if account_holder := payment_details.get("account_holder"):
                        st.write(f"Holder: {account_holder}")

            if st.session_state.notes_input:
                st.write(f"**Notes:** {st.session_state.notes_input}")

    if st.button("Start New Split", type="primary", use_container_width=True):
        st.write("Starting a new split from step 0...")
        reset_app_state_full()
        st.query_params.clear()
        st.rerun()

    if not is_view_mode:
        if st.button("Adjust Split Details", use_container_width=True):
            st.session_state.share_link = None
            if st.session_state.item_assignments or not st.session_state.split_evenly:
                reset_to_step(2)
            else:
                reset_to_step(3)
            st.rerun()
