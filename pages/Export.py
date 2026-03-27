import streamlit as st
import json

from pages.functionality.state import init_state
from pages.functionality.export import exporter, report, recipe

st.set_page_config(layout="wide")

init_state()

st.title("Export & Report")

if st.session_state.df_working is None:
    st.warning("Upload dataset first")
    st.stop()

df = st.session_state.df_working
log = st.session_state.transformation_log

# =====================================
# DATA PREVIEW
# =====================================

st.subheader("Final Dataset")

col1, col2 = st.columns(2)

col1.metric("Rows", df.shape[0])
col2.metric("Columns", df.shape[1])

st.dataframe(df.head(15))

# =====================================
# EXPORT DATA
# =====================================

st.divider()
st.subheader("Download Dataset")

csv_bytes = exporter.to_csv_bytes(df)
excel_bytes = exporter.to_excel_bytes(df)

st.download_button("Download CSV", csv_bytes, "data.csv")

st.download_button("Download Excel", excel_bytes, "data.xlsx")

# =====================================
# REPORT
# =====================================

st.divider()
st.subheader("Transformation Report")

report_data = report.generate_report(df, log)

st.json(report_data)

st.download_button(
    "Download Report",
    json.dumps(report_data, indent=4),
    "report.json"
)

# =====================================
# RECIPE
# =====================================

st.divider()
st.subheader("Transformation Recipe")

recipe_data = recipe.generate_recipe(log)

st.code(json.dumps(recipe_data, indent=4), language="json")

st.download_button(
    "Download Recipe",
    json.dumps(recipe_data, indent=4),
    "recipe.json"
)

# =====================================
# RESET
# =====================================

st.divider()

if st.button("Reset Dataset"):

    st.session_state.df_working = st.session_state.df_original.copy()
    st.session_state.transformation_log = []

    st.success("Reset done")
    st.rerun()