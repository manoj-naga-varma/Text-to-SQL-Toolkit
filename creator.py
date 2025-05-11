import streamlit as st
import sqlite3
import pandas as pd
import os

# Database path constant
DB_PATH = "dynamic.db"

# Function to create a database and user-defined table
def create_database(table_name, columns):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Construct CREATE TABLE SQL statement
    column_definitions = ", ".join([f'"{col_name}" {col_type}' for col_name, col_type in columns.items()])
    # Use double quotes for table name to preserve case
    sql_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({column_definitions})'

    cur.execute(sql_query)
    conn.commit()
    conn.close()
    st.success(f"✅ Table '{table_name}' created successfully!")

# Function to check if a table exists
def table_exists(table_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Query sqlite_master to check if table exists (case sensitive)
    cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?', (table_name,))
    result = cur.fetchone()
    
    conn.close()
    return result is not None

# Function to list all tables in the database
def list_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [row[0] for row in cur.fetchall()]
    
    conn.close()
    return tables

# Function to insert records dynamically
def insert_record(table_name, column_names, values):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Use double quotes for table and column names to preserve case
        quoted_columns = [f'"{col}"' for col in column_names]
        placeholders = ", ".join(["?" for _ in values])
        sql_query = f'INSERT INTO "{table_name}" ({", ".join(quoted_columns)}) VALUES ({placeholders})'

        cur.execute(sql_query, values)
        conn.commit()
        conn.close()
        st.success("✅ Record inserted successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Function to fetch records from a table
def fetch_records(table_name):
    try:
        # First check if table exists
        if not table_exists(table_name):
            st.warning(f"⚠️ Table '{table_name}' does not exist.")
            return pd.DataFrame()
            
        conn = sqlite3.connect(DB_PATH)
        # Use double quotes for table name to preserve case
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Could not fetch records: {e}")
        return pd.DataFrame()

# Function to get table schema
def get_table_schema(table_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Use double quotes for table name
        cur.execute(f'PRAGMA table_info("{table_name}")')
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        conn.close()
        return columns
    except Exception as e:
        st.error(f"❌ Could not get table schema: {e}")
        return {}

def run_schema_creator():
    st.title("🗂️ Database Schema Creator")
    
    # Display database status
    db_exists = os.path.exists(DB_PATH)
    st.info(f"Database status: {'✅ Connected' if db_exists else '❌ Not created yet'}")

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
    
    # Display list of existing tables
    st.subheader("📊 Existing Tables")
    tables = list_tables()
    
    if tables:
        selected_table = st.selectbox("Select a table", tables)
        table_to_use = selected_table
    else:
        st.info("No tables found in the database.")
        table_to_use = table_name if table_name else ""

    # Step 2: Insert Records
    st.subheader("➕ Insert Records into Table")

    if table_to_use:
        if table_exists(table_to_use):
            # Get column schema from the database
            table_columns = get_table_schema(table_to_use)
            
            if table_columns:
                with st.form("insert_form"):
                    values = []
                    for col, col_type in table_columns.items():
                        if col_type == "TEXT":
                            value = st.text_input(f"Enter {col}")
                        elif col_type in ["INTEGER", "REAL"]:
                            value = st.number_input(f"Enter {col}", step=1 if col_type == "INTEGER" else 0.1)
                        else:
                            value = st.text_input(f"Enter {col}")
                        values.append(value)
                    
                    submit = st.form_submit_button("📥 Insert Record")
                
                if submit:
                    insert_record(table_to_use, list(table_columns.keys()), values)
            else:
                st.warning(f"⚠️ Could not retrieve schema for table '{table_to_use}'.")
        else:
            st.warning(f"⚠️ Table '{table_to_use}' does not exist. Create it first.")

   
