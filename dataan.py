import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="Pandas File Analyzer", layout="wide")
st.title("📊 Universal Pandas File Analyzer & Visualizer")

# --- PDF-based command list ---
pandas_commands = {
       'df.head(n)': 'Display first n rows.',
    'df.tail(n)': 'Display last n rows.',
    'df.shape': 'Shape of DataFrame.',
    'df.columns': 'Column names.',
    'df.index': 'Index labels.',
    'df.info()': 'Info summary of DataFrame.',
    'df.describe()': 'Summary statistics.',
    'df.dtypes': 'Data types of columns.',
    'df.memory_usage()': 'Memory usage of DataFrame.',
    "df['column']": 'Select single column.',
    "df[['col1', 'col2']]": 'Select multiple columns.',
    'df.loc[row_label, col_label]': 'Label-based indexing.',
    'df.iloc[row_idx, col_idx]': 'Position-based indexing.',
    'df.at[row_label, col_label]': 'Fast access by label.',
    'df.iat[row_idx, col_idx]': 'Fast access by position.',
    "df[df['col'] > 10]": 'Filter rows by condition.',
    "df.query('col > 10')": 'Filter using query method.',
    'df.isnull()': 'Detect missing values.',
    'df.notnull()': 'Detect non-missing values.',
    'df.dropna()': 'Drop missing values.',
    'df.fillna(value)': 'Fill missing values.',
    "df['col'] = value": 'Assign values to column.',
    'df.rename(columns={})': 'Rename columns.',
    "df.drop('col', axis=1)": 'Drop a column.',
    'df.drop(index, axis=0)': 'Drop a row.',
    'df.insert(loc, col, value)': 'Insert new column.',
    'df.replace({old: new})': 'Replace values.',
    "df.astype({'col': dtype})": 'Change data type.',
    "df['col'].str.lower()": 'Lowercase string column.',
    "df['col'].str.upper()": 'Uppercase string column.',
    "df['col'].str.contains('text')": 'String contains filter.',
    "df['col'].str.replace('old', 'new')": 'Replace text.',
    "df['col'].str.strip()": 'Trim whitespace.',
    "df['col'].sum()": 'Sum of column.',
    "df['col'].mean()": 'Mean of column.',
    "df['col'].median()": 'Median of column.',
    "df['col'].min()": 'Minimum value.',
    "df['col'].max()": 'Maximum value.',
    "df['col'].std()": 'Standard deviation.',
    "df['col'].round(2)": 'Round values.',
    "df.groupby('col').mean()": 'Group by and mean.',
    "df.groupby(['col1', 'col2']).agg({'col3': 'sum'})": 'Multi-group aggregation.',
    "df.agg(['sum', 'mean'])": 'Aggregate all columns.',
    "df.sort_values('col')": 'Sort by column.',
    "df.sort_values(['col1', 'col2'], ascending=[True, False])": 'Sort by multiple columns.',
    'df.sort_index()': 'Sort by index.',
    'pd.concat([df1, df2])': 'Concatenate DataFrames.',
    "pd.merge(df1, df2, on='key')": 'Merge DataFrames.',
    "df.join(df2, on='key')": 'Join DataFrames.',
    'df.pivot(index, columns, values)': 'Pivot table.',
    "df.pivot_table(index, columns, values, aggfunc='mean')": 'Pivot table with aggregation.',
    'df.melt(id_vars, value_vars)': 'Unpivot wide to long.',
    'df.stack()': 'Stack columns to rows.',
    'df.unstack()': 'Unstack rows to columns.',
    "df.set_index('col')": 'Set index.',
    'df.reset_index()': 'Reset index.',
    "df.set_index(['col1', 'col2'])": 'Set multi-index.',
    "pd.to_datetime(df['col'])": 'Convert to datetime.',
    "df['col'].dt.year": 'Extract year.',
    "df['col'].dt.month": 'Extract month.',
    "df['col'].dt.day": 'Extract day.',
    "df['col'].dt.strftime('%Y-%m-%d')": 'Format datetime.',
    'df.duplicated()': 'Find duplicates.',
    'df.drop_duplicates()': 'Drop duplicates.',
    'df.apply(func)': 'Apply function to rows or columns.',
    'df.map(func)': 'Map values in Series.',
    'df.applymap(func)': 'Apply function to entire DataFrame.'
}

# --- File Upload ---
file = st.file_uploader("Upload a data file", type=["csv", "tsv", "xlsx", "xls", "json", "html", "xml"])

# --- Load Data ---
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".tsv"):
        return pd.read_csv(file, sep="\t")
    elif file.name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    elif file.name.endswith(".json"):
        return pd.read_json(file)
    elif file.name.endswith(".html"):
        return pd.read_html(file)[0]
    elif file.name.endswith(".xml"):
        return pd.read_xml(file)
    else:
        return None

if file:
    try:
        raw_df = load_data(file)
        if raw_df is None:
            st.error("Unsupported file format.")
            st.stop()

        df = raw_df.copy()

        st.subheader("🗏️ Data Preview")
        st.dataframe(df.head())

        st.subheader("📌 Data Info")
        st.write(df.dtypes)
        st.write(f"**Rows:** {df.shape[0]}, **Columns:** {df.shape[1]}")

        # --- Filtering ---
        st.subheader("🔎 Filter Your Data")
        filtered_df = df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val, max_val = float(df[col].min()), float(df[col].max())
                selected_range = st.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
                filtered_df = filtered_df[filtered_df[col].between(*selected_range)]
            elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                unique_vals = df[col].dropna().unique().tolist()
                if len(unique_vals) < 100:
                    selected_vals = st.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
                    filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

        # --- Command Dropdown Help ---
        st.subheader("📘 Pandas Command Help")
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_command = st.selectbox("Choose a command to insert & run", list(pandas_commands.keys()))
            st.caption(pandas_commands[selected_command])

        with col2:
            formula_code = st.text_area("🧮 Write or modify code using 'df'", value=selected_command, height=180)
            run_formula = st.button("▶️ Run Command")

        if run_formula:
            try:
                local_vars = {"df": filtered_df.copy(), "pd": pd}
                exec(f"result = {formula_code}", {}, local_vars)
                result = local_vars.get("result", None)
                df = local_vars["df"]
                st.success("✅ Command executed!")
                if result is not None:
                    if isinstance(result, pd.DataFrame) or isinstance(result, pd.Series):
                        st.dataframe(result)
                    else:
                        st.write("Output:", result)
                else:
                    st.dataframe(df.head())
            except Exception as e:
                st.error(f"❌ Error in command: {e}")
        else:
            df = filtered_df

        # --- Row/Column Selection ---
        st.subheader("📁 Row & Column Selection")
        row_count = st.slider("Select number of rows", 1, len(df), min(10, len(df)))
        selected_columns = st.multiselect("Select columns", df.columns.tolist(), default=df.columns.tolist()[:2])
        if selected_columns:
            st.dataframe(df[selected_columns].head(row_count))
        else:
            st.warning("Please select at least one column.")

        # --- Plotting ---
        st.subheader("📈 Graph Plotting")
        if selected_columns:
            x_axis = st.selectbox("Select X-axis", selected_columns)
            y_axis_options = [col for col in selected_columns if pd.api.types.is_numeric_dtype(df[col])]
            if y_axis_options:
                y_axis = st.selectbox("Select Y-axis", y_axis_options)
                chart_type = st.selectbox("Chart type", ["Line", "Bar", "Scatter"])

                fig, ax = plt.subplots()
                try:
                    if chart_type == "Line":
                        sns.lineplot(data=df, x=x_axis, y=y_axis, ax=ax)
                    elif chart_type == "Bar":
                        sns.barplot(data=df, x=x_axis, y=y_axis, ax=ax)
                    elif chart_type == "Scatter":
                        sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error creating graph: {e}")
            else:
                st.warning("No numeric column available for Y-axis.")

        # --- Export ---
        st.subheader("📅 Export Filtered/Modified Data")
        export_format = st.radio("Export as", ["CSV", "Excel"])
        if export_format == "CSV":
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "processed_data.csv", "text/csv")
        else:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.save()
            st.download_button("Download Excel", out.getvalue(), "processed_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
