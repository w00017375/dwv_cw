import streamlit as st
import pandas as pd
import numpy as np


from pages.functionality.cleaning import missing, duplicates, dtypes, scaling
from pages.functionality.logger import log_step
from pages.functionality.state import init_state

st.set_page_config(layout="wide")

init_state()

st.title("Cleaning Studio")

# ===============================
# GLOBAL FEEDBACK (IMPROVED)
# ===============================

st.divider()

if st.session_state.last_message:
    st.success(st.session_state.last_message)

if st.session_state.last_preview is not None:
    with st.expander("Preview updated dataset", expanded=True):
        st.dataframe(st.session_state.last_preview)

st.divider()

# ===============================

if st.session_state.df_working is None:
    st.warning("Upload dataset first")
    st.stop()

# =================================================
# TRANSFORMATION LOG + UNDO
# =================================================

with st.expander("Transformation Log"):

    log = st.session_state.transformation_log

    if log:

        for i, step in enumerate(reversed(log), 1):
            st.write(
                f"{step.get('operation')} | "
                f"Column: {step.get('column')} | "
                f"Details: {step.get('details')}"
            )

    else:
        st.info("No transformations yet")

    # ---------- UNDO ----------
    if st.button("Undo last step"):

        if st.session_state.df_history:

            st.session_state.df_working = st.session_state.df_history.pop()

            if st.session_state.transformation_log:
                st.session_state.transformation_log.pop()

            st.session_state.last_message = "Last step undone"
            st.session_state.last_preview = st.session_state.df_working.head(10)

        else:
            st.warning("No steps to undo")


# =================================================
# REPLAY PIPELINE
# =================================================

with st.expander("Replay Pipeline"):

    st.write("Reapply transformation steps to original dataset")

    if st.button("Replay transformations"):

        if st.session_state.df_original is None:
            st.warning("No original dataset available")
            st.stop()

        df = st.session_state.df_original.copy()
        log = st.session_state.transformation_log

        warnings = []

        for step in log:

            try:
                op = step.get("operation")
                col = step.get("column")
                details = step.get("details")

                # =========================
                # MISSING
                # =========================
                if op == "missing":

                    if col not in df.columns:
                        warnings.append(f"Column '{col}' not found")
                        continue

                    if details == "Fill with mean":
                        df[col] = df[col].fillna(df[col].mean())

                    elif details == "Fill with median":
                        df[col] = df[col].fillna(df[col].median())

                    elif details == "Fill with mode":
                        df[col] = df[col].fillna(df[col].mode()[0])

                    elif details == "Fill using previous value":
                        df[col] = df[col].ffill()

                    elif details == "Fill using next value":
                        df[col] = df[col].bfill()

                    elif details == "Remove rows with missing values":
                        df = df.dropna(subset=[col])

                # =========================
                # DUPLICATES
                # =========================
                elif op == "duplicates":

                    keep = details.get("keep", "first") if details else "first"
                    subset = details.get("columns") if details else None

                    df = df.drop_duplicates(subset=subset, keep=keep)

                # =========================
                # DTYPE
                # =========================
                elif op == "dtype":

                    if col not in df.columns:
                        warnings.append(f"Column '{col}' not found")
                        continue

                    if details == "numeric":
                        df[col] = pd.to_numeric(df[col], errors="ignore")

                    elif details == "datetime":
                        df[col] = pd.to_datetime(df[col], errors="ignore")

                    elif details == "category":
                        df[col] = df[col].astype("category")

                    elif details == "string":
                        df[col] = df[col].astype(str)

                # =========================
                # SCALING
                # =========================
                elif op == "scaling":

                    if col not in df.columns:
                        warnings.append(f"Column '{col}' not found")
                        continue

                    if details == "minmax":
                        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

                    elif details == "zscore":
                        df[col] = (df[col] - df[col].mean()) / df[col].std()

                # =========================
                # OUTLIERS
                # =========================
                elif op == "outliers":

                    if col not in df.columns:
                        warnings.append(f"Column '{col}' not found")
                        continue

                    # если есть percentiles
                    if isinstance(details, dict):
                        lower = details.get("lower_pct", 5)
                        upper = details.get("upper_pct", 95)

                        low_val = df[col].quantile(lower / 100)
                        high_val = df[col].quantile(upper / 100)

                        df = df[(df[col] >= low_val) & (df[col] <= high_val)]

                # =========================
                # UNKNOWN
                # =========================
                else:
                    warnings.append(f"Unknown operation: {op}")

            except Exception as e:
                warnings.append(f"{op} failed: {str(e)}")

        # ---------- RESULT ----------
        st.session_state.df_working = df
        st.session_state.last_message = "Pipeline replay completed"
        st.session_state.last_preview = df.head(10)

        # ---------- WARNINGS ----------
        if warnings:
            st.warning("Some steps could not be fully applied:")
            for w in warnings:
                st.write(f"- {w}")


# =================================================
# MISSING VALUES
# =================================================


with st.expander("Missing Values", expanded=True):

    df_current = st.session_state.df_working

    # ---------- SUMMARY ----------
    missing_count = df_current.isnull().sum()
    missing_percent = (missing_count / len(df_current)) * 100

    summary_df = pd.DataFrame({
        "column": df_current.columns,
        "missing_count": missing_count.values,
        "missing_%": missing_percent.round(2).values
    })

    st.subheader("Missing Values Summary")
    st.dataframe(summary_df)

    cols = df_current.columns[df_current.isnull().any()].tolist()

    if cols:

        col_missing = st.selectbox("Column", cols, key="missing_col")

        method_missing = st.selectbox(
            "Method",
            [
                "Fill with mean",
                "Fill with median",
                "Fill with mode",
                "Fill using previous value",
                "Fill using next value",
                "Fill with custom value",
                "Remove rows with missing values",
                "Drop columns above missing % threshold"
            ],
            key="missing_method"
        )

        # ---------- CUSTOM VALUE ----------
        if method_missing == "Fill with custom value":
            custom_value = st.text_input("Enter value", key="custom_val")

        # ---------- THRESHOLD ----------
        if method_missing == "Drop columns above missing % threshold":
            threshold = st.slider("Missing % threshold", 0, 100, 50)

        # ---------- BUTTON ----------
        if st.button("Apply Missing Fix", key="missing_btn"):

            try:
                st.session_state.df_history.append(df_current.copy())
                df = df_current.copy()

                before_rows = len(df)
                before_missing = df[col_missing].isnull().sum()

                # ---------- APPLY ----------
                if method_missing == "Fill with mean":
                    df = missing.fill_mean(df, col_missing)

                elif method_missing == "Fill with median":
                    df = missing.fill_median(df, col_missing)

                elif method_missing == "Fill with mode":
                    df = missing.fill_mode(df, col_missing)

                elif method_missing == "Fill using previous value":
                    df = missing.forward_fill(df, col_missing)

                elif method_missing == "Fill using next value":
                    df = missing.backward_fill(df, col_missing)

                elif method_missing == "Fill with custom value":

                    if custom_value == "":
                        raise ValueError("Value cannot be empty")

                    if df[col_missing].dtype.kind in "biufc":
                        custom_value = float(custom_value)

                    df[col_missing] = df[col_missing].fillna(custom_value)

                elif method_missing == "Remove rows with missing values":
                    df = missing.drop_rows(df, col_missing)

                elif method_missing == "Drop columns above missing % threshold":

                    drop_cols = missing_percent[missing_percent > threshold].index.tolist()

                    df = df.drop(columns=drop_cols)

                # ---------- AFTER ----------
                after_rows = len(df)

                if col_missing in df.columns:
                    after_missing = df[col_missing].isnull().sum()
                else:
                    after_missing = 0

                filled = before_missing - after_missing
                dropped_rows = before_rows - after_rows

                # ---------- % CALC ----------
                total_rows = before_rows if before_rows > 0 else 1

                percent_rows = (dropped_rows / total_rows) * 100
                percent_col = (filled / total_rows) * 100

                # ---------- MESSAGE ----------
                if method_missing == "Remove rows with missing values":
                    msg = f"Removed {dropped_rows} rows ({percent_rows:.2f}%)"

                elif method_missing == "Drop columns above missing % threshold":
                    msg = f"Dropped {len(drop_cols)} columns above {threshold}% missing"

                else:
                    msg = f"Handled {filled} values in '{col_missing}' ({percent_col:.2f}%)"

                st.session_state.df_working = df
                st.session_state.last_message = msg
                st.session_state.last_preview = df.head(10)

                log_step("missing", column=col_missing, details=method_missing)

            except Exception as e:
                st.error(f"Missing values error: {str(e)}")

    else:
        st.info("No missing values in dataset")


# =================================================
# DUPLICATES
# =================================================

with st.expander("Duplicates"):

    df_current = st.session_state.df_working

    # ---------- METHOD ----------
    dup_method = st.selectbox(
        "Duplicate detection method",
        ["Full row duplicates", "Subset of columns"],
        key="dup_method"
    )

    if dup_method == "Subset of columns":
        subset_cols = st.multiselect(
            "Select columns",
            df_current.columns,
            key="dup_cols"
        )
    else:
        subset_cols = None

    # ---------- KEEP STRATEGY ----------
    keep_option = st.selectbox(
        "Keep",
        ["Keep first", "Keep last"],
        key="dup_keep"
    )

    keep_map = {
        "Keep first": "first",
        "Keep last": "last"
    }

    keep_value = keep_map[keep_option]

    # ---------- SHOW DUPLICATES ----------
    if st.checkbox("Show duplicate rows", key="show_dups"):

        try:
            if subset_cols:
                dup_df = df_current[df_current.duplicated(subset=subset_cols, keep=False)]
            else:
                dup_df = df_current[df_current.duplicated(keep=False)]

            st.write(f"Duplicate rows found: {len(dup_df)}")

            st.dataframe(dup_df.head(50))

        except Exception as e:
            st.error(f"Error showing duplicates: {str(e)}")

    # ---------- REMOVE ----------
    if st.button("Remove duplicates", key="dup_btn"):

        try:
            st.session_state.df_history.append(df_current.copy())
            df = df_current.copy()

            before = len(df)

            if subset_cols:
                df = df.drop_duplicates(subset=subset_cols, keep=keep_value)
            else:
                df = df.drop_duplicates(keep=keep_value)

            removed = before - len(df)

            st.session_state.df_working = df

            st.session_state.last_message = (
                f"Removed {removed} duplicates ({keep_option.lower()})"
                if removed > 0 else
                "No duplicates found"
            )

            st.session_state.last_preview = df.head(10)

            log_step("duplicates", details={
                "method": dup_method,
                "columns": subset_cols,
                "keep": keep_value
            })

        except Exception as e:
            st.error(f"Duplicate removal failed: {str(e)}")


# =================================================
# DATA TYPES (SAFE CONVERSION)
# =================================================

with st.expander("Data Types"):

    df_current = st.session_state.df_working
    col_dtype = st.selectbox("Column", df_current.columns, key="dtype_col")
    dtype = st.selectbox("Convert to", ["numeric","datetime","category","string"], key="dtype_type")

    if st.button("Convert", key="dtype_btn"):

        try:
            st.session_state.df_history.append(df_current.copy())
            df = df_current.copy()

            old_series = df[col_dtype].copy()

            # ---------- TRY CONVERSION ----------
            if dtype == "numeric":
                converted = pd.to_numeric(old_series, errors="coerce")

            elif dtype == "datetime":
                converted = pd.to_datetime(old_series, errors="coerce")

            elif dtype == "category":
                converted = old_series.astype("category")

            elif dtype == "string":
                converted = old_series.astype(str)

            # ---------- VALIDATION ----------
            invalid_count = converted.isnull().sum() - old_series.isnull().sum()

            if invalid_count > 0:
                st.error(
                    f"Conversion failed: {invalid_count} values cannot be converted to {dtype}"
                )
                st.warning("No changes were applied")
                st.stop()

            # ---------- APPLY ----------
            df[col_dtype] = converted

            st.session_state.df_working = df
            st.session_state.last_message = f"{col_dtype} successfully converted to {dtype}"
            st.session_state.last_preview = df.head(10)

            log_step("dtype", column=col_dtype, details=dtype)

        except Exception as e:
            st.error(f"Conversion error: {str(e)}")


# =================================================
# CATEGORICAL TOOLS
# =================================================

with st.expander("Categorical Data Tools"):

    df_current = st.session_state.df_working

    cat_cols = df_current.select_dtypes(include=["object","category"]).columns.tolist()

    if cat_cols:

        col_cat = st.selectbox("Select column", cat_cols, key="cat_col")

        tool = st.selectbox(
            "Operation",
            [
                "Standardize values",
                "Mapping / Replacement",
                "Group rare categories",
                "One-hot encoding"
            ],
            key="cat_tool"
        )

        # =========================================
        # 1. STANDARDIZATION
        # =========================================

        if tool == "Standardize values":

            option = st.selectbox(
                "Standardization type",
                ["Lowercase", "Uppercase", "Title case", "Trim whitespace"],
                key="cat_standard"
            )

            if st.button("Apply", key="cat_standard_btn"):

                try:
                    st.session_state.df_history.append(df_current.copy())
                    df = df_current.copy()

                    before_unique = df[col_cat].nunique()

                    if option == "Lowercase":
                        df[col_cat] = df[col_cat].astype(str).str.lower()

                    elif option == "Uppercase":
                        df[col_cat] = df[col_cat].astype(str).str.upper()

                    elif option == "Title case":
                        df[col_cat] = df[col_cat].astype(str).str.title()

                    elif option == "Trim whitespace":
                        df[col_cat] = df[col_cat].astype(str).str.strip()

                    after_unique = df[col_cat].nunique()

                    st.session_state.df_working = df
                    st.session_state.last_message = (
                        f"Standardized '{col_cat}' ({before_unique} → {after_unique} unique values)"
                    )
                    st.session_state.last_preview = df.head(10)

                    log_step("categorical_standardize", column=col_cat, details=option)

                except Exception as e:
                    st.error(str(e))

        # =========================================
        # 2. MAPPING
        # =========================================

        elif tool == "Mapping / Replacement":

            st.write("Enter mapping (old → new values)")

            unique_vals = df_current[col_cat].dropna().unique().tolist()

            mapping_input = {}

            for val in unique_vals[:20]:  # ограничим UI
                new_val = st.text_input(f"{val} →", key=f"map_{val}")
                if new_val != "":
                    mapping_input[val] = new_val

            replace_other = st.checkbox("Replace unmatched values with 'Other'")

            if st.button("Apply mapping", key="cat_map_btn"):

                try:
                    st.session_state.df_history.append(df_current.copy())

                    df = df_current.copy()

                    df[col_cat] = df[col_cat].map(mapping_input).fillna(
                        "Other" if replace_other else df[col_cat]
                    )

                    st.session_state.df_working = df
                    st.session_state.last_message = f"Applied mapping on '{col_cat}'"
                    st.session_state.last_preview = df.head(10)

                    log_step("categorical_mapping", column=col_cat, details=mapping_input)

                except Exception as e:
                    st.error(str(e))

        # =========================================
        # 3. RARE CATEGORY GROUPING
        # =========================================

        elif tool == "Group rare categories":

            threshold = st.slider("Min frequency (%)", 0, 20, 5)

            if st.button("Apply grouping", key="cat_group_btn"):

                try:
                    st.session_state.df_history.append(df_current.copy())

                    df = df_current.copy()

                    freq = df[col_cat].value_counts(normalize=True) * 100

                    rare_values = freq[freq < threshold].index

                    df[col_cat] = df[col_cat].replace(rare_values, "Other")

                    st.session_state.df_working = df
                    st.session_state.last_message = (
                        f"Grouped {len(rare_values)} rare categories into 'Other'"
                    )
                    st.session_state.last_preview = df.head(10)

                    log_step("categorical_grouping", column=col_cat, details={"threshold": threshold})

                except Exception as e:
                    st.error(str(e))

        # =========================================
        # 4. ONE-HOT ENCODING
        # =========================================

        elif tool == "One-hot encoding":

            if st.button("Apply encoding", key="cat_ohe_btn"):

                try:
                    st.session_state.df_history.append(df_current.copy())
                    df = df_current.copy()

                    dummies = pd.get_dummies(df[col_cat], prefix=col_cat)

                    df = pd.concat([df.drop(columns=[col_cat]), dummies], axis=1)

                    st.session_state.df_working = df
                    st.session_state.last_message = f"One-hot encoded '{col_cat}'"
                    st.session_state.last_preview = df.head(10)

                    log_step("categorical_ohe", column=col_cat)

                except Exception as e:
                    st.error(str(e))

    else:
        st.info("No categorical columns available")


# =================================================
# COLUMN OPERATIONS
# =================================================

with st.expander("Column Operations"):

    df_current = st.session_state.df_working
    operation = st.selectbox(
        "Operation",
        [
            "Rename column",
            "Drop columns",
            "Create new column (formula)",
            "Binning (categorization)"
        ],
        key="col_ops"
    )

    # =========================================
    # 1. RENAME COLUMN
    # =========================================

    if operation == "Rename column":

        col_old = st.selectbox("Select column", df_current.columns, key="rename_col")
        col_new = st.text_input("New column name")

        if st.button("Apply rename", key="rename_btn"):

            try:
                st.session_state.df_history.append(df_current.copy())
                if col_new.strip() == "":
                    raise ValueError("Column name cannot be empty")

                df = df_current.copy()

                df = df.rename(columns={col_old: col_new})

                st.session_state.df_working = df
                st.session_state.last_message = f"Renamed '{col_old}' → '{col_new}'"
                st.session_state.last_preview = df.head(10)

                log_step("rename_column", column=col_old, details={"new_name": col_new})

            except Exception as e:
                st.error(str(e))

    # =========================================
    # 2. DROP COLUMNS
    # =========================================

    elif operation == "Drop columns":

        cols_drop = st.multiselect("Select columns to drop", df_current.columns)

        if st.button("Drop selected columns", key="drop_cols_btn"):

            try:
                st.session_state.df_history.append(df_current.copy())
                if not cols_drop:
                    st.warning("Select at least one column")
                    st.stop()

                df = df_current.copy()

                df = df.drop(columns=cols_drop)

                st.session_state.df_working = df
                st.session_state.last_message = f"Dropped columns: {cols_drop}"
                st.session_state.last_preview = df.head(10)

                log_step("drop_columns", details={"columns": cols_drop})

            except Exception as e:
                st.error(str(e))

    # =========================================
    # 3. CREATE NEW COLUMN (FORMULA)
    # =========================================

    elif operation == "Create new column (formula)":

        df_current = st.session_state.df_working

        st.write("Build formula manually. Copy column names below.")

        # ---------- NUMERIC COLUMNS ----------
        num_cols = df_current.select_dtypes(include="number").columns.tolist()

        if not num_cols:
            st.info("No numeric columns available")
            st.stop()

        st.subheader("Available columns (click to copy)")

        cols_ui = st.columns(2)

        for i, col in enumerate(num_cols):
            with cols_ui[i % 2]:
                st.code(f"`{col}`")  # копируемый формат

        # ---------- OPERATORS ----------
        st.subheader("Operators")

        op_cols = st.columns(4)

        op_cols[0].code("+")
        op_cols[1].code("-")
        op_cols[2].code("*")
        op_cols[3].code("/")

        # ---------- FORMULA ----------
        formula = st.text_input(
            "Formula (example: `price` / `quantity`)",
            key="formula_input"
        )

        # ---------- NEW COLUMN ----------
        new_col = st.text_input("New column name", key="new_col_name")

        # ---------- APPLY ----------
        if st.button("Create column", key="create_col_btn"):

            try:
                if new_col.strip() == "":
                    raise ValueError("Column name cannot be empty")

                if formula.strip() == "":
                    raise ValueError("Formula cannot be empty")

                df = df_current.copy()

                # ---------- NULL → 0 ----------
                df_safe = df.fillna(0)

                # ---------- TRY CALC ----------
                result = df_safe.eval(formula, engine="python")

                # ---------- CHECK DIVISION BY ZERO ----------
                if not pd.Series(result).replace([float("inf"), float("-inf")], pd.NA).notna().all():
                    st.error("Operation failed: division by zero detected")
                    st.warning("No changes were applied")
                    st.stop()

                # ---------- SAVE SNAPSHOT ----------
                st.session_state.df_history.append(df_current.copy())

                # ---------- APPLY RESULT ----------
                df[new_col] = result

                st.session_state.df_working = df
                st.session_state.last_message = f"Created column '{new_col}'"
                st.session_state.last_preview = df.head(10)

                log_step("create_column", details={
                    "name": new_col,
                    "formula": formula
                })

            except Exception as e:
                st.error(f"Formula error: {str(e)}")

    # =========================================
    # 4. BINNING
    # =========================================

    elif operation == "Binning (categorization)":

        num_cols = df_current.select_dtypes(include="number").columns.tolist()

        if num_cols:

            col_bin = st.selectbox("Select numeric column", num_cols)

            bin_type = st.selectbox("Binning type", ["Equal width", "Quantile"])

            bins = st.slider("Number of bins", 2, 10, 4)

            if st.button("Apply binning", key="bin_btn"):

                try:
                    st.session_state.df_history.append(df_current.copy())

                    df = df_current.copy()

                    new_col = f"{col_bin}_binned"

                    if bin_type == "Equal width":
                        df[new_col] = pd.cut(df[col_bin], bins=bins)

                    else:
                        df[new_col] = pd.qcut(df[col_bin], q=bins, duplicates="drop")

                    st.session_state.df_working = df
                    st.session_state.last_message = f"Binned '{col_bin}' into {bins} groups"
                    st.session_state.last_preview = df.head(10)

                    log_step("binning", column=col_bin, details={
                        "type": bin_type,
                        "bins": bins
                    })

                except Exception as e:
                    st.error(str(e))

        else:
            st.info("No numeric columns available")



# =================================================
# DATA VALIDATION RULES
# =================================================

with st.expander("Data Validation"):

    df_current = st.session_state.df_working
    rule_type = st.selectbox(
        "Validation rule",
        [
            "Numeric range check",
            "Allowed categories",
            "Non-null constraint"
        ],
        key="val_rule"
    )

    violations_df = None

    # =========================================
    # 1. NUMERIC RANGE
    # =========================================

    if rule_type == "Numeric range check":

        num_cols = df_current.select_dtypes(include="number").columns.tolist()

        if num_cols:

            col = st.selectbox("Column", num_cols, key="val_num_col")

            min_val = st.number_input("Min value", value=0.0)
            max_val = st.number_input("Max value", value=100.0)

            if st.button("Check", key="val_num_btn"):

                try:
                    violations_df = df_current[
                        (df_current[col] < min_val) | (df_current[col] > max_val)
                    ]

                    st.write(f"Violations found: {len(violations_df)}")
                    st.dataframe(violations_df.head(50))

                    log_step("validation_numeric", column=col, details={
                        "min": min_val,
                        "max": max_val
                    })

                except Exception as e:
                    st.error(str(e))

        else:
            st.info("No numeric columns")

    # =========================================
    # 2. ALLOWED CATEGORIES
    # =========================================

    elif rule_type == "Allowed categories":

        cat_cols = df_current.select_dtypes(include=["object","category"]).columns.tolist()

        if cat_cols:

            col = st.selectbox("Column", cat_cols, key="val_cat_col")

            allowed = st.text_input(
                "Allowed values (comma separated)",
                placeholder="A,B,C"
            )

            if st.button("Check", key="val_cat_btn"):

                try:
                    allowed_list = [x.strip() for x in allowed.split(",") if x.strip() != ""]

                    violations_df = df_current[~df_current[col].isin(allowed_list)]

                    st.write(f"Violations found: {len(violations_df)}")
                    st.dataframe(violations_df.head(50))

                    log_step("validation_category", column=col, details=allowed_list)

                except Exception as e:
                    st.error(str(e))

        else:
            st.info("No categorical columns")

    # =========================================
    # 3. NON-NULL CONSTRAINT
    # =========================================

    elif rule_type == "Non-null constraint":

        cols = st.multiselect("Select columns", df_current.columns)

        if st.button("Check", key="val_null_btn"):

            try:
                violations_df = df_current[df_current[cols].isnull().any(axis=1)]

                st.write(f"Violations found: {len(violations_df)}")
                st.dataframe(violations_df.head(50))

                log_step("validation_non_null", details={"columns": cols})

            except Exception as e:
                st.error(str(e))

    # =========================================
    # EXPORT VIOLATIONS
    # =========================================

    if violations_df is not None and not violations_df.empty:

        csv = violations_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download violations",
            csv,
            "violations.csv",
            "text/csv"
        )


# =================================================
# OUTLIERS (PERCENTILE)
# =================================================

with st.expander("Outliers"):

    df_current = st.session_state.df_working
    num_cols = df_current.select_dtypes(include="number").columns.tolist()

    if num_cols:

        col_outlier = st.selectbox("Column", num_cols, key="out_col")

        lower, upper = st.slider("Percentile range", 0, 100, (5, 95))

        if st.button("Remove outliers", key="out_btn"):

            try:
                st.session_state.df_history.append(df_current.copy())

                df = df_current.copy()

                before = len(df)

                low_val = df[col_outlier].quantile(lower / 100)
                high_val = df[col_outlier].quantile(upper / 100)

                df = df[(df[col_outlier] >= low_val) & (df[col_outlier] <= high_val)]

                removed = before - len(df)

                st.session_state.df_working = df
                st.session_state.last_message = f"Removed {removed} outliers"
                st.session_state.last_preview = df.head(10)

                log_step("outliers", col_outlier)

            except Exception as e:
                st.error(str(e))

    else:
        st.info("No numeric columns")


# =================================================
# SCALING
# =================================================

with st.expander("Scaling"):

    df_current = st.session_state.df_working
    num_cols = df_current.select_dtypes(include="number").columns.tolist()

    if num_cols:

        col_scale = st.selectbox("Column", num_cols, key="scale_col")
        method = st.selectbox("Method", ["minmax","zscore"], key="scale_method")

        if st.button("Scale", key="scale_btn"):

            try:
                st.session_state.df_history.append(df_current.copy())
                df = df_current.copy()

                if method == "minmax":
                    df = scaling.minmax(df, col_scale)
                else:
                    df = scaling.zscore(df, col_scale)

                st.session_state.df_working = df
                st.session_state.last_message = f"{method} applied"
                st.session_state.last_preview = df.head(10)

                log_step("scaling", column=col_scale, details=method)

            except Exception as e:
                st.error(str(e))

    else:
        st.info("No numeric columns")