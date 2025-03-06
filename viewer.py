import streamlit as st
import sqlite3
import pandas as pd

# Function to fetch available tables
def get_tables():
    conn = sqlite3.connect("dynamic.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cur.fetchall()]
    conn.close()
    return tables

# Function to fetch data from a selected table
def fetch_records(table_name):
    conn = sqlite3.connect("dynamic.db")
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# Function to delete a table
def delete_table(table_name):
    conn = sqlite3.connect("dynamic.db")
    cur = conn.cursor()
    try:
        cur.execute(f"DROP TABLE {table_name};")
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Failed to delete table: {e}")
        conn.close()
        return False

def run_table_viewer():
    st.title("📊 Table Viewer")

    tables = get_tables()

    if tables:
        st.write("### Available Tables:")
        table_name = st.selectbox("Select Table to View", tables)
        
        if st.button("🔍 Load Data"):
            data = fetch_records(table_name)
            if not data.empty:
                st.dataframe(data)
            else:
                st.warning("⚠️ No records found in this table.")
        
        with st.expander("Delete Table"):
            confirm_delete = st.checkbox(f"Confirm deletion of '{table_name}'")
            if confirm_delete and st.button("🚮 Delete"):
                if delete_table(table_name):
                    st.success(f"Table '{table_name}' deleted successfully.")
                    tables = get_tables()  # Refresh table list
                    st.experimental_rerun()  # Rerun the app to update the UI
    else:
        st.warning("⚠️ No tables found. Create tables first in 'Schema Creator'.")
