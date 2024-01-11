import streamlit as st

# container = st.beta_container()
all1 = st.checkbox("Select all")

if all1:
    selected_options = st.multiselect(
        "Select one or more options:",
        ['A', 'B', 'C'], ['A', 'B', 'C'], label_visibility="collapsed")
else:
    selected_options = st.multiselect("Select one or more options:",
                                      ['A', 'B', 'C'], label_visibility="collapsed")
