import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import sqlite3
import pandas as pd
import requests
import json

# Load environment variables
load_dotenv()

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini API URL
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Function to generate SQL query from user input

def get_gemini_response(question, prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": f"{prompt}\n{question}"}]}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        return f"API Error: {response.status_code}, {response.text}"

    try:
        response_json = response.json()
        candidates = response_json.get("candidates", [])
        if not candidates:
            return "No response generated"

        content = candidates[0].get("content", {}).get("parts", [])
        if not content:
            return "No content generated"

        return content[0].get("text", "No text found").strip()
    except json.JSONDecodeError:
        return "Invalid JSON response from API"

# Function to execute SQL

def read_sql_query(sql, db, params=None):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql) if not params else cur.execute(sql, params)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        conn.close()
        return rows, columns
    except sqlite3.Error as e:
        return str(e), []

# Get all tables in the DB

def get_tables(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cur.fetchall()]
    conn.close()
    return tables

# Main Streamlit App

def run_sql_generator():
    st.title("\U0001F4BB Text-to-SQL Query Generator")
    st.subheader("\U0001F4DD Enter Your Query")

    tables = get_tables("dynamic.db")
    selected_table = st.selectbox("Select Table (optional)", ["All Tables"] + tables, key="table_select")
    question = st.text_input("Write your question here:", key="input")
    submit = st.button("\U0001F680 Generate SQL & Fetch Data")

    table_context = f"The SQL database contains tables: {', '.join(tables)}." if tables else ""

    base_prompt = f"""
You are an expert in converting English questions into SQL queries.
{table_context}

Your task is to generate only the SQL query without any explanations.

### Rules:
1️⃣ Do not include ``` in the beginning or end of the output.  
2️⃣ Do not include the word SQL in the output.  
3️⃣ Output only the pure SQL query.  
4️⃣ Ensure all string comparisons are case-insensitive by converting both the table values and input to lowercase.
"""

    example_queries = """...your list of examples here..."""

    full_prompt = [base_prompt + example_queries + "\n\nNow, given the following question, generate an SQL query:\n"]

    if submit:
        if not question:
            st.warning("Please enter a question.")
            return

        with st.spinner("Generating SQL query..."):
            sql_query = get_gemini_response(question, full_prompt[0])

        st.subheader("\U0001F4DD Generated SQL Query:")
        st.code(sql_query, language="sql")

        with st.spinner("Fetching data from the database..."):
            response, columns = read_sql_query(sql_query, "dynamic.db")

        st.subheader("\U0001F4CA Query Results:")
        if isinstance(response, str):
            st.error(f"❌ SQL Error: {response}")
        elif response:
            df = pd.DataFrame(response, columns=columns)
            st.dataframe(df)
        else:
            st.warning("⚠️ No data found for the given query.")

if __name__ == "__main__":
    run_sql_generator()
