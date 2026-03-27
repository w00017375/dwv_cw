import streamlit as st

def init_state():

    if "df_original" not in st.session_state:
        st.session_state.df_original = None

    if "df_working" not in st.session_state:
        st.session_state.df_working = None

    if "transformation_log" not in st.session_state:
        st.session_state.transformation_log = []

    if "last_message" not in st.session_state:
        st.session_state.last_message = None

    if "last_preview" not in st.session_state:
        st.session_state.last_preview = None

    if "df_history" not in st.session_state:
        st.session_state.df_history = []