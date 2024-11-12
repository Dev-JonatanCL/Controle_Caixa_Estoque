import streamlit as st

col1, col2, col3 = st.columns([3, 3, 3])

with col2:
    st.image ('./Icons/Logo.png', use_column_width=False, width=200)