import streamlit as st
from state import reset_to_step


def render_assign_items_step(gemini_items_list):
    """Renders the UI for step 2: assigning items to people."""
    st.header("Step 3: How to Split Items?")
    st.session_state.split_evenly = st.checkbox(
        "Split the entire bill (after discounts, before tax/tip) evenly among everyone?",
        value=st.session_state.split_evenly,
        key="split_evenly_checkbox",
    )
    st.markdown("---")
    items_to_assign_ui = gemini_items_list
    current_ui_assignments = []
    all_individual_items_assigned_flag = True if items_to_assign_ui else False
    if st.session_state.split_evenly:
        st.info(
            "The bill subtotal will be split evenly. Individual item assignment below is disabled."
        )
        all_individual_items_assigned_flag = True
    elif not items_to_assign_ui:
        st.warning("No items extracted. If not splitting evenly, please go back.")
        all_individual_items_assigned_flag = False
    else:
        st.write("For each item, select who shared it:")
        for i, item_data_ui in enumerate(items_to_assign_ui):
            item_key_suffix = item_data_ui.get("item", f"unknown_item_{i}")
            col_item_detail, col_assign_person = st.columns([0.6, 0.4])
            with col_item_detail:
                st.markdown(f"**{item_data_ui.get('item', 'Unknown Item')}**")
                try:
                    qty_float = float(item_data_ui.get("qty", "1"))
                    qty_display = (
                        int(qty_float) if qty_float == int(qty_float) else qty_float
                    )
                    price_float = float(item_data_ui.get("price", "0.0"))
                except ValueError:  # Fallback if conversion fails
                    qty_display = item_data_ui.get("qty", "1")
                    price_float = 0.0
                st.caption(f"{qty_display} x IDR {price_float:,.2f}")
            with col_assign_person:
                # Find previous assignment for this item
                default_sel = []
                if st.session_state.item_assignments:
                    for assignment in st.session_state.item_assignments:
                        if assignment["item_details"] == item_data_ui:
                            default_sel = assignment["assigned_to"]
                            break

                assigned_to = st.multiselect(
                    "Shared by:",
                    st.session_state.person_names_list,
                    default=default_sel,
                    key=f"assign_{i}_{item_key_suffix.replace(' ', '_').replace('.', '_').replace('/', '_')}",
                    label_visibility="collapsed",
                )
            current_ui_assignments.append(
                {"item_details": item_data_ui, "assigned_to": assigned_to}
            )
            if not assigned_to:
                all_individual_items_assigned_flag = False
            if i < len(items_to_assign_ui) - 1:
                st.markdown("---")
    st.markdown("---")
    col_back2, col_next2 = st.columns(2)
    with col_back2:
        if st.button("Back to People", use_container_width=True):
            if not st.session_state.split_evenly:
                st.session_state.item_assignments = current_ui_assignments
            reset_to_step(1)
            st.rerun()
    with col_next2:
        next_button_disabled_step2 = (not st.session_state.split_evenly) and (
            (not items_to_assign_ui) or (not all_individual_items_assigned_flag)
        )
        if st.button(
            "Next: Tax & Tip",
            type="primary",
            use_container_width=True,
            disabled=next_button_disabled_step2,
        ):
            if not st.session_state.split_evenly:
                st.session_state.item_assignments = current_ui_assignments
            else:
                st.session_state.item_assignments = []
            st.session_state.current_step = 3
            st.rerun()
        if (
            not st.session_state.split_evenly
            and not all_individual_items_assigned_flag
            and items_to_assign_ui
        ):
            st.caption("Please assign all items if not splitting evenly.")
