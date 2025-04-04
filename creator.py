import streamlit as st
import sqlite3
import pandas as pd

# Function to create a database and user-defined table
def create_database(table_name, columns):
    conn = sqlite3.connect("dynamic.db")
    cur = conn.cursor()

    # Construct CREATE TABLE SQL statement
    column_definitions = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
    sql_query = f"CREATE TABLE IF NOT EXISTS '{table_name}' ({column_definitions})"

    cur.execute(sql_query)
    conn.commit()
    conn.close()
    st.success(f"✅ Table '{table_name}' created successfully!")

# Function to insert records dynamically
def insert_record(table_name, column_names, values):
    try:
        conn = sqlite3.connect("dynamic.db")
        cur = conn.cursor()

        placeholders = ", ".join(["?" for _ in values])
        sql_query = f"INSERT INTO '{table_name}' ({', '.join(column_names)}) VALUES ({placeholders})"

        cur.execute(sql_query, values)
        conn.commit()
        conn.close()
        st.success("✅ Record inserted successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Function to fetch records from a table
def fetch_records(table_name):
    try:
        conn = sqlite3.connect("dynamic.db")
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Could not fetch records: {e}")
        return pd.DataFrame()

def run_schema_creator():
    st.title("🗂️ Dynamic Database Schema Creator")

    # Step 1: User defines schema
    st.subheader("🛠️ Define Table Schema")

    table_name = st.text_input("Enter Table Name")

    num_columns = st.number_input("Number of Columns", min_value=1, step=1)

    columns = {}
    for i in range(num_columns):
        col_name = st.text_input(f"Column {i+1} Name")
        col_type = st.selectbox(f"Column {i+1} Type", ["TEXT", "INTEGER", "REAL"], key=f"type_{i}")
        if col_name:
            columns[col_name] = col_type

    # Button to create table
    if st.button("🚀 Create Table"):
        if table_name and columns:
            create_database(table_name, columns)
        else:
            st.warning("⚠️ Please enter a table name and define at least one column.")

    # Step 2: Insert Records
    st.subheader("➕ Insert Records into Table")

    if table_name and columns:
        with st.form("insert_form"):
            values = [
                st.text_input(f"Enter {col}") if col_type == "TEXT" else 
                st.number_input(f"Enter {col}", step=1 if col_type == "INTEGER" else 0.1)
                for col, col_type in columns.items()
            ]

            submit = st.form_submit_button("📥 Insert Record")

        if submit:
            insert_record(table_name, list(columns.keys()), values)

    # Step 3: Display Table Records
    st.subheader("📋 View Table Data")

    if table_name:
        data = fetch_records(table_name)
        if not data.empty:
            st.dataframe(data)
        else:
            st.warning("⚠️ No records found. Insert some records first!")
