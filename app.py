import streamlit as st
import pandas as pd

from pages.functionality.state import init_state
from pages.functionality.data_loader import load_file
from pages.functionality.profiler import get_profile

st.set_page_config(layout="wide")

init_state()

st.title("Upload & Overview")

# =================================================
# UPLOAD
# =================================================

file = st.file_uploader("Upload dataset", type=["csv","xlsx","json"])

if file:
    try:
        df = load_file(file)

        st.session_state.df_original = df
        st.session_state.df_working = df.copy()

        st.success("File uploaded successfully")

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")


# =================================================
# RESET
# =================================================

if st.session_state.df_working is not None:

    if st.button("Reset session"):

        st.session_state.df_original = None
        st.session_state.df_working = None
        st.session_state.transformation_log = []
        st.session_state.last_message = None
        st.session_state.last_preview = None

        st.success("Session reset")


# =================================================
# OVERVIEW
# =================================================

if st.session_state.df_working is not None:

    df = st.session_state.df_working

    profile = get_profile(df)

    # ===============================
    # MAIN METRICS
    # ===============================

    st.subheader("Dataset Info")

    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Duplicates: {df.duplicated().sum()}")

    # ===============================
    # DTYPES
    # ===============================

    st.subheader("Column Types")
    dtypes_df = profile["dtypes"].reset_index()
    dtypes_df.columns = ["Name", "Data Type"]

    st.dataframe(dtypes_df, use_container_width=True, hide_index=True)

    # ===============================
    # MISSING VALUES
    # ===============================

    st.subheader("Missing Values")

    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df)) * 100

    missing_df = pd.DataFrame({
        "column": df.columns,
        "missing_count": missing_count.values,
        "missing_%": missing_percent.round(2).values
    })

    st.dataframe(missing_df, hide_index=True)

    # ===============================
    # NUMERIC SUMMARY
    # ===============================

    st.subheader("Numeric Summary")

    num_df = df.select_dtypes(include="number")

    if not num_df.empty:
        st.dataframe(num_df.describe().T)
    else:
        st.info("No numeric columns")

    # ===============================
    # CATEGORICAL SUMMARY
    # ===============================

    st.subheader("Categorical Summary")

    cat_df = df.select_dtypes(include=["object","category"])

    if not cat_df.empty:

        cat_summary = pd.DataFrame({
            "column": cat_df.columns,
            "unique_values": cat_df.nunique().values,
            "top_value": cat_df.mode().iloc[0].values,
            "top_freq": cat_df.apply(
                lambda x: x.value_counts().iloc[0] if not x.value_counts().empty else 0
            ).values
        })

        st.dataframe(cat_summary, hide_index=True)

    else:
        st.info("No categorical columns")

    # ===============================
    # PREVIEW
    # ===============================

    st.subheader("Data Preview")
    st.dataframe(df.head(20))