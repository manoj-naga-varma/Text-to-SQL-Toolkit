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

# Function to get database schema
def get_db_schema(db_path):
    """Extract complete database schema including tables and their columns"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        # Get column information for each table
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        
        # Store column details (name, type, nullable, default, pk)
        schema[table] = [
            {
                "name": col[1],
                "type": col[2],
                "notnull": col[3],
                "pk": col[5]
            } for col in columns
        ]
    
    conn.close()
    return schema

# Format schema as human-readable text
def format_schema_for_prompt(schema):
    schema_text = "DATABASE SCHEMA:\n"
    
    for table, columns in schema.items():
        schema_text += f"Table: {table}\n"
        schema_text += "Columns:\n"
        
        for col in columns:
            pk_indicator = " (Primary Key)" if col["pk"] == 1 else ""
            nullable = "NOT NULL" if col["notnull"] == 1 else "NULL"
            schema_text += f"  - {col['name']} ({col['type']}) {nullable}{pk_indicator}\n"
        
        schema_text += "\n"
    
    return schema_text

# Function to generate SQL query using Gemini
def get_gemini_response(schema_text, question, prompt):
    headers = {"Content-Type": "application/json"}
    
    # Include schema in the prompt
    full_prompt = f"{prompt}\n\n{schema_text}\n\nQuestion: {question}\nSQL Query:"
    
    data = {
        "contents": [{"parts": [{"text": full_prompt}]}]
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
        columns = [desc[0] for desc in cur.description] if cur.description else []
        conn.close()
        return rows, columns
    except sqlite3.Error as e:
        return str(e), []

# Main Streamlit App
def run_sql_generator():
    st.title("🧠 Enhanced Text-to-SQL Query Generator")
    st.subheader("📝 Enter Your Question")
    
    # Database path
    db_path = "dynamic.db"
    
    # Get database schema
    schema = get_db_schema(db_path)
    formatted_schema = format_schema_for_prompt(schema)
    
    # Display schema in an expandable section
    with st.expander("View Database Schema"):
        st.code(formatted_schema)
    
    # User input
    question = st.text_input("Write your question here:", key="input")
    submit = st.button("🚀 Generate SQL & Fetch Data")
    
    # Base prompt for Gemini
    base_prompt = """
You are an expert SQL query generator. Your task is to generate accurate SQL queries based on natural language questions and the provided database schema.

### Rules:
1️⃣ Generate only the raw SQL query - no explanations, no backticks, no "SQL" keyword
2️⃣ Use ONLY the exact table and column names from the provided schema
3️⃣ Ensure all string comparisons are case-insensitive using LOWER()
4️⃣ Be precise and specific - don't include columns that don't exist in the schema
5️⃣ Use appropriate joins when querying across multiple tables
6️⃣ If the question is ambiguous, make reasonable assumptions based on the schema
7️⃣ Include only the SQL query in your response - nothing else
"""
    
    if submit:
        if not question:
            st.warning("Please enter a question.")
            return
        
        with st.spinner("Analyzing database and generating SQL query..."):
            sql_query = get_gemini_response(formatted_schema, question, base_prompt)
            # Clean up any code formatting that might have been added
            sql_query = sql_query.strip().replace("```sql", "").replace("```", "").strip()
        
        st.subheader("📝 Generated SQL Query:")
        st.code(sql_query, language="sql")
        
        with st.spinner("Fetching data from the database..."):
            response, columns = read_sql_query(sql_query, db_path)
        
        st.subheader("📊 Query Results:")
        if isinstance(response, str):
            st.error(f"❌ SQL Error: {response}")
        elif response:
            df = pd.DataFrame(response, columns=columns)
            st.dataframe(df)
        else:
            st.info("ℹ️ Query executed successfully, but no data was returned.")

# Cache the schema to avoid repeated database reads
@st.cache_data(ttl=600)  # Cache for 10 minutes
def cached_schema(db_path):
    return get_db_schema(db_path)

if __name__ == "__main__":
    run_sql_generator()
