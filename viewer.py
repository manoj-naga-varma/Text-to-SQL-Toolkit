import streamlit as st
import sqlite3
import pandas as pd
import io

# Database path constant
DB_PATH = "dynamic.db"

# Function to fetch available tables
def get_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # No special quoting needed for this system table query
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cur.fetchall()]
    conn.close()
    return tables

# Function to fetch data from a selected table
def fetch_records(table_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use double quotes for table name to preserve case
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Could not fetch records: {e}")
        return pd.DataFrame()

# Function to delete a table
def delete_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Use double quotes for table name to preserve case
        cur.execute(f'DROP TABLE "{table_name}";')
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Failed to delete table: {e}")
        conn.close()
        return False

# Function to fetch table schema
def get_table_schema(table_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Use double quotes for table name to preserve case
        cur.execute(f'PRAGMA table_info("{table_name}");')
        schema = cur.fetchall()
        conn.close()
        return pd.DataFrame(schema, columns=["cid", "name", "type", "notnull", "default_value", "pk"])
    except Exception as e:
        st.error(f"❌ Could not fetch schema: {e}")
        conn.close()
        return pd.DataFrame()

# Function to check if a table exists
def table_exists(table_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Query sqlite_master to check if table exists (case sensitive)
    cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?', (table_name,))
    result = cur.fetchone()
    
    conn.close()
    return result is not None

# Main app function
def run_table_viewer():
    st.title("📊 Table Viewer")

    tables = get_tables()

    if tables:
        st.write("### Available Tables:")
        table_name = st.selectbox("Select Table to View", tables)
        
        # Check if the selected table exists
        if not table_exists(table_name):
            st.warning(f"⚠️ Table '{table_name}' does not exist or cannot be accessed.")
            return
            
        data = None  # Initialize in outer scope

        if st.button("🔍 Load Data"):
            data = fetch_records(table_name)
            if not data.empty:
                st.dataframe(data)
                
                # Add export options
                csv = data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"{table_name}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No records found in this table.")

        # Schema viewer
        with st.expander("🧬 View Table Schema"):
            schema = get_table_schema(table_name)
            if not schema.empty:
                st.dataframe(schema)
            else:
                st.warning("⚠️ Could not retrieve schema information.")
       
        with st.expander("🚮 Delete Table"):
            st.warning("⚠️ WARNING: This action cannot be undone!")
            confirm_delete = st.checkbox(f"I understand the risks and want to delete '{table_name}'")
            if confirm_delete and st.button("Delete Table"):
                if delete_table(table_name):
                    st.success(f"Table '{table_name}' deleted successfully.")
                    st.rerun()
    else:
        st.warning("⚠️ No tables found. Create tables first in 'Schema Creator'.")

