import streamlit as st
from creator import run_schema_creator
from viewer import run_table_viewer
from sql_generator import run_sql_generator

# Streamlit App Configuration
st.set_page_config(page_title="Dynamic Database App", layout="wide")

# Create tabs
tab_schema_creator, tab_table_viewer, tab_sql_generator = st.tabs(["Schema Creator", "Table Viewer", "SQL Query Generator"])

# Run components based on selected tab
with tab_schema_creator:
    run_schema_creator()

with tab_table_viewer:
    run_table_viewer()

with tab_sql_generator:
    run_sql_generator()
