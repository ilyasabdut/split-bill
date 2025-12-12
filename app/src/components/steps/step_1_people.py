import streamlit as st
from state import reset_to_step


def render_people_step():
    """Renders the UI for step 1: adding people to the split."""
    st.header("Step 2: Who's Splitting?")
    st.text_input(
        "Enter a person's name to add:",
        key="current_name_input_field",
        value=st.session_state.current_name_input,
        on_change=lambda: setattr(
            st.session_state,
            "current_name_input",
            st.session_state.current_name_input_field,
        ),
    )
    if st.button("Add Person", use_container_width=True):
        typed_name = st.session_state.current_name_input.strip()
        if typed_name and typed_name not in st.session_state.person_names_list:
            st.session_state.person_names_list.append(typed_name)
            st.session_state.current_name_input = ""
            st.rerun()
        elif not typed_name:
            st.warning("Please enter a name.")
        elif typed_name in st.session_state.person_names_list:
            st.warning(f"'{typed_name}' is already in the list.")
    st.write("People added:")
    if not st.session_state.person_names_list:
        st.caption("No people added yet.")
    else:
        for i, name in enumerate(st.session_state.person_names_list):
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.markdown(
                    f"<div style='background-color:#2E323A;color:white;padding:6px 12px;border-radius:5px;margin-bottom:5px;'>{name}</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button(
                    "-",
                    key=f"remove_person_{i}_{name.replace(' ','_')}",
                    help=f"Remove {name}",
                    use_container_width=True,
                ):
                    st.session_state.person_names_list.pop(i)
                    st.rerun()
        st.markdown(f"Total: **{len(st.session_state.person_names_list)}** people")
    st.markdown("---")
    col_back1, col_next1 = st.columns(2)
    with col_back1:
        if st.button("Back to Upload", use_container_width=True):
            reset_to_step(0)
            st.rerun()
    with col_next1:
        if st.button(
            "Next: Assign Items",
            type="primary",
            use_container_width=True,
            disabled=(not st.session_state.person_names_list),
        ):
            st.session_state.current_step = 2
            st.rerun()
