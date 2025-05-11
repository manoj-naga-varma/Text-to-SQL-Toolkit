import streamlit as st
import pandas as pd
import sqlite3
import io
import os

def run_data_importer():
    st.title("📥 Data Import Tool")
    st.write("Import data from CSV or Excel files into your database.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Show file details
        file_details = {
            "Filename": uploaded_file.name,
            "FileType": uploaded_file.type,
            "Size": f"{uploaded_file.size/1024:.2f} KB"
        }
        st.write("### File Details:")
        st.json(file_details)
        
        try:
            # Detect file type and read data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("### Data Preview:")
            st.dataframe(df.head(5))
            
            # Import configuration
            with st.form("import_config"):
                st.subheader("Import Configuration")
                table_name = st.text_input("Table Name", value=os.path.splitext(uploaded_file.name)[0].replace(" ", "_"))
                
                st.write("### Column Data Types:")
                col_types = {}
                for column in df.columns:
                    suggested_type = "TEXT"
                    if pd.api.types.is_numeric_dtype(df[column]):
                        if pd.api.types.is_integer_dtype(df[column]):
                            suggested_type = "INTEGER"
                        else:
                            suggested_type = "REAL"
                    
                    col_types[column] = st.selectbox(
                        f"Data type for '{column}'",
                        ["TEXT", "INTEGER", "REAL", "BLOB"],
                        index=["TEXT", "INTEGER", "REAL", "BLOB"].index(suggested_type)
                    )

                # Automatically set replace behavior
                if_exists = "Replace"
                
                submit_button = st.form_submit_button("Import Data")
            
            if submit_button:
                try:
                    conn = sqlite3.connect("dynamic.db")
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                    table_exists = cursor.fetchone()
                    
                    if table_exists:
                        cursor.execute(f"DROP TABLE {table_name};")
                        conn.commit()
                    
                    columns_sql = ", ".join([f'"{col}" {dtype}' for col, dtype in col_types.items()])
                    create_table_sql = f'CREATE TABLE "{table_name}" ({columns_sql});'
                    cursor.execute(create_table_sql)
                    conn.commit()
                    
                    df = df.replace({pd.NA: None})
                    data = list(df.itertuples(index=False, name=None))
                    
                    placeholders = ", ".join(["?" for _ in col_types])
                    columns = ", ".join([f'"{col}"' for col in col_types.keys()])
                    insert_sql = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders});'
                    
                    cursor.executemany(insert_sql, data)
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Successfully imported {len(df)} rows into table '{table_name}'!")
                
                except Exception as e:
                    st.error(f"❌ Error during import: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    else:
        st.info("📁 Please upload a CSV or Excel file to import data.")
        
        with st.expander("📝 Need a template?"):
            st.write("Download these example templates to get started:")
            
            example_df = pd.DataFrame({
                'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
                'Age': [28, 35, 42],
                'Salary': [75000.50, 82000.75, 95000.00],
                'Department': ['Marketing', 'Engineering', 'Management']
            })
            
            csv_buffer = io.BytesIO()
            example_df.to_csv(csv_buffer, index=False)
            
            excel_buffer = io.BytesIO()
            example_df.to_excel(excel_buffer, index=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download CSV Template",
                    data=csv_buffer.getvalue(),
                    file_name="template.csv",
                    mime="text/csv"
                )
            
            with col2:
                st.download_button(
                    label="Download Excel Template",
                    data=excel_buffer.getvalue(),
                    file_name="template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )