import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import sqlite3
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate SQL query from user input
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()  # Strip unnecessary whitespace

# Function to retrieve query from the database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]  # Get column names
        conn.close()
        return rows, columns
    except sqlite3.Error as e:
        return str(e), []  # Return error message

# Function to get available tables from the database
def get_tables(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cur.fetchall()]
    conn.close()
    return tables

def run_sql_generator():
    st.title("💻 Text-🔄-SQL Query Generator")

    # User input area
    st.subheader("📝 Enter Your Query")
    
    # Get available tables
    tables = get_tables("dynamic.db")
    
    # Select table
    selected_table = st.selectbox("Select Table", tables, key="table_select")
    
    question = st.text_input("Write your question here:", key="input")

    submit = st.button("🚀 Generate SQL & Fetch Data")

    # Expanded prompt with 30+ diverse SQL examples
    prompt = [f"""
    You are an expert in converting English questions into SQL queries.
    The SQL database contains a table named {selected_table}.

    Your task is to generate **only** the SQL query **without any explanations**.

    ### **Rules:**
    1️⃣ Do **not** include 
    in the beginning or end of the output.  
    2️⃣ Do **not** include the word **SQL** in the output.  
    3️⃣ Output only the **pure SQL query**.

    ### **Example Queries:**  

    Q: How many rows are in the table?  
    A: SELECT COUNT(*) FROM {selected_table};  

    Q: List all columns in the table.  
    A: SELECT * FROM {selected_table};  

    Now, given the following question, generate an SQL query **without explanations, without 
    at the beginning or end, and without the word SQL in the output**.
    """]
    
    # If submit button is clicked
    if submit:
        with st.spinner("Generating SQL query... 💡"):
            sql_query = get_gemini_response(question, prompt)

        # Display the generated SQL query
        st.subheader("📝 Generated SQL Query:")
        st.code(sql_query, language="sql")

        # Execute SQL query and fetch data
        with st.spinner("Fetching data from the database... 🗄️"):
            response, columns = read_sql_query(sql_query, "dynamic.db")

        # Display the results
        st.subheader("📊 Query Results:")

        if isinstance(response, str):  # Error handling
            st.error(f"❌ SQL Error: {response}")
        elif response:
            df = pd.DataFrame(response, columns=columns)
            st.dataframe(df)  # Display results in an interactive table
        else:
            st.warning("⚠️ No data found for the given query.")
