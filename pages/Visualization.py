import streamlit as st

from  pages.functionality.visualization import charts, filters
from  pages.functionality.state import init_state

st.set_page_config(layout="wide")

init_state()

st.title("Visualization Builder")

if st.session_state.df_working is None:
    st.warning("Upload dataset first")
    st.stop()

df = st.session_state.df_working.copy()

# ======================================
# FILTERS
# ======================================

with st.expander("Filters", expanded=True):

    # categorical
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()

    if cat_cols:

        col = st.selectbox("Category filter", ["None"] + cat_cols)

        if col != "None":

            values = df[col].dropna().unique()

            selected = st.multiselect("Values", values, default=values)

            df = filters.filter_category(df, col, selected)

    # numeric
    num_cols = df.select_dtypes(include="number").columns.tolist()

    if num_cols:

        col = st.selectbox("Numeric filter", ["None"] + num_cols)

        if col != "None":

            min_val = float(df[col].min())
            max_val = float(df[col].max())

            selected = st.slider("Range", min_val, max_val, (min_val, max_val))

            df = filters.filter_numeric(df, col, selected[0], selected[1])

st.write("Filtered rows:", len(df))

# ======================================
# CHART BUILDER
# ======================================

with st.expander("Chart Builder", expanded=True):

    chart_type = st.selectbox(
        "Chart type",
        ["Histogram","Boxplot","Scatter","Line","Bar","Heatmap"]
    )

    fig = None

    # HIST
    if chart_type == "Histogram":

        col = st.selectbox("Column", df.select_dtypes(include="number").columns)

        bins = st.slider("Bins", 5, 100, 20)

        if st.button("Generate"):
            fig = charts.histogram(df, col, bins)

    # BOX
    elif chart_type == "Boxplot":

        col = st.selectbox("Column", df.select_dtypes(include="number").columns)

        if st.button("Generate"):
            fig = charts.boxplot(df, col)

    # SCATTER
    elif chart_type == "Scatter":

        num_cols = df.select_dtypes(include="number").columns

        x = st.selectbox("X", num_cols)
        y = st.selectbox("Y", num_cols)

        if st.button("Generate"):
            fig = charts.scatter(df, x, y)

    # LINE
    elif chart_type == "Line":

        x = st.selectbox("X", df.columns)
        y = st.selectbox("Y", df.select_dtypes(include="number").columns)

        if st.button("Generate"):
            fig = charts.line(df, x, y)

    # BAR
    elif chart_type == "Bar":

        cat_cols = df.select_dtypes(include=["object","category"]).columns
        num_cols = df.select_dtypes(include="number").columns

        cat = st.selectbox("Category", cat_cols)
        val = st.selectbox("Value", num_cols)

        agg = st.selectbox("Aggregation", ["mean","sum","count","median"])

        top_n = st.slider("Top N", 3, 20, 10)

        if st.button("Generate"):
            fig = charts.bar(df, cat, val, agg, top_n)

    # HEATMAP
    elif chart_type == "Heatmap":

        if st.button("Generate"):
            fig = charts.heatmap(df)

    if fig:
        st.pyplot(fig)