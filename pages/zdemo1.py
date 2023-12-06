import numpy as np
import pandas as pd
import streamlit as st
from streamlit_tree_select import tree_select

st.title("🐙 Streamlit-tree-select")
st.subheader("A simple and elegant checkbox tree for Streamlit.")

# Create nodes to display
nodes = [
    {"label": "Folder A", "value": "folder_a"},
    {
        "label": "Folder B",
        "value": "folder_b",
        "children": [
            {"label": "Sub-folder A", "value": "sub_a"},
            {"label": "Sub-folder B", "value": "sub_b"},
            {"label": "Sub-folder C", "value": "sub_c"},
        ],
    },
    {
        "label": "Folder C",
        "value": "folder_c",
        "children": [
            {"label": "Sub-folder D", "value": "sub_d"},
            {
                "label": "Sub-folder E",
                "value": "sub_e",
                "children": [
                    {"label": "Sub-sub-folder A", "value": "sub_sub_a"},
                    {"label": "Sub-sub-folder B", "value": "sub_sub_b"},
                ],
            },
            {"label": "Sub-folder F", "value": "sub_f"},
        ],
    },
]
st.markdown('---')
col1, col2 = st.columns(2)
with col1:
    tree_select(nodes)
with col2:
    temperature = np.random.randint(low=0, high=40, size=1000)

    df = pd.DataFrame({'temperature': temperature})
    st.dataframe(df)
# st.sidebar(return_select)

import streamlit as st
from streamlit_modal import Modal

import streamlit.components.v1 as components

modal = Modal(
    "Demo Modal",
    key="demo-modal",

    # Optional
    padding=20,  # default value
    max_width=744  # default value
)
open_modal = st.button("Open")
if open_modal:
    modal.open()

if modal.is_open():
    with modal.container():
        temperature = np.random.randint(low=0, high=40, size=1000)

        df = pd.DataFrame({'temperature': temperature})
        st.dataframe(df)
