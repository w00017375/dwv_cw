from datetime import datetime
import streamlit as st

def log_step(operation, column=None, details=None):

    if "transformation_log" not in st.session_state:
        st.session_state.transformation_log = []

    st.session_state.transformation_log.append({
        "operation": operation,
        "column": column,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })