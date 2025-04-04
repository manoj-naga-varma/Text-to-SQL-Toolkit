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


# Function to generate SQL query from user input
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
# Function to retrieve query from the database
'''
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
'''
def read_sql_query(sql, db, params=None):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
            
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        conn.close()
        return rows, columns
    except sqlite3.Error as e:
        return str(e), []



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
4️⃣ Ensure that **all string comparisons are case-insensitive** by converting both the table values and input to **lowercase**.


### **Example Queries:**  

#### **Making the input text, values in the table, and generated query in the same case (lowercase)**
Q: Find students whose names are "John" (case-insensitive).  
A: SELECT * FROM {selected_table} WHERE LOWER(name) = LOWER('John');  

Q: Get all users where the role is "admin" (case-insensitive).  
A: SELECT * FROM {selected_table} WHERE LOWER(role) = LOWER('admin');  

Q: Retrieve students whose section is 'A', ignoring case.  
A: SELECT * FROM {selected_table} WHERE LOWER(section) = LOWER('A');  

Q: Find employees with the designation "Manager" (case-insensitive).  
A: SELECT * FROM {selected_table} WHERE LOWER(designation) = LOWER('Manager');  

Q: Get all records where city is 'New York' (case-insensitive).  
A: SELECT * FROM {selected_table} WHERE LOWER(city) = LOWER('New York'); 

#### **Basic Queries**
Q: How many rows are in the table?  
A: SELECT COUNT(*) FROM {selected_table};  

Q: List all columns in the table.  
A: SELECT * FROM {selected_table};  

Q: Get the names of all students who scored more than 80 marks.  
A: SELECT NAME FROM {selected_table} WHERE MARKS > 80;  

Q: Find students whose names start with 'A'.  
A: SELECT * FROM {selected_table} WHERE NAME LIKE 'A%';  

Q: Retrieve students sorted by name alphabetically.  
A: SELECT * FROM {selected_table} ORDER BY NAME ASC;  

#### **Aggregation & Grouping**
Q: Count the number of students in each class.  
A: SELECT CLASS, COUNT(*) FROM {selected_table} GROUP BY CLASS;  

Q: Find the average marks of all students.  
A: SELECT AVG(MARKS) FROM {selected_table};  

Q: Get the total sum of marks obtained by students.  
A: SELECT SUM(MARKS) FROM {selected_table};  

Q: Count students per section.  
A: SELECT SECTION, COUNT(*) FROM {selected_table} GROUP BY SECTION;  

Q: Get the total number of sections.  
A: SELECT COUNT(DISTINCT SECTION) FROM {selected_table};  

#### **Sorting & Filtering**
Q: Get the top 5 highest marks from the table.  
A: SELECT * FROM {selected_table} ORDER BY MARKS DESC LIMIT 5;  

Q: Get the student with the highest marks.  
A: SELECT * FROM {selected_table} ORDER BY MARKS DESC LIMIT 1;  

Q: Get students whose marks are either 50, 75, or 90.  
A: SELECT * FROM {selected_table} WHERE MARKS IN (50, 75, 90);  

Q: Retrieve students who scored between 50 and 80.  
A: SELECT * FROM {selected_table} WHERE MARKS BETWEEN 50 AND 80;  

Q: Find students in class 10 and section B.  
A: SELECT * FROM {selected_table} WHERE CLASS = '10' AND SECTION = 'B';  

#### **Advanced Queries with JOINs**
Q: Retrieve all students along with their teacher names (assuming 'teachers' table exists).  
A: SELECT s.NAME, t.TEACHER_NAME FROM {selected_table} s JOIN teachers t ON s.TEACHER_ID = t.ID;  

Q: Get the list of students along with the subjects they are studying (assuming 'subjects' table exists).  
A: SELECT s.NAME, sub.SUBJECT_NAME FROM {selected_table} s JOIN subjects sub ON s.SUBJECT_ID = sub.ID;  

Q: Find students who have not received marks and their class names (assuming 'classes' table exists).  
A: SELECT s.NAME, c.CLASS_NAME FROM {selected_table} s LEFT JOIN classes c ON s.CLASS_ID = c.ID WHERE s.MARKS IS NULL;  

#### **More Advanced Queries**
Q: Find the section with the highest average marks.  
A: SELECT SECTION, AVG(MARKS) AS AVG_MARKS FROM {selected_table} GROUP BY SECTION ORDER BY AVG_MARKS DESC LIMIT 1;  

Q: Get the total number of students and the total marks per class.  
A: SELECT CLASS, COUNT(*) AS TOTAL_STUDENTS, SUM(MARKS) AS TOTAL_MARKS FROM {selected_table} GROUP BY CLASS;  

Q: Find the top 3 students per section based on marks.  
A: SELECT * FROM (SELECT *, RANK() OVER (PARTITION BY SECTION ORDER BY MARKS DESC) AS rank FROM {selected_table}) WHERE rank <= 3;  

Q: List students who have the same marks as at least one other student.  
A: SELECT NAME, MARKS FROM {selected_table} WHERE MARKS IN (SELECT MARKS FROM {selected_table} GROUP BY MARKS HAVING COUNT(*) > 1);  

Q: Find the most common marks in the table.  
A: SELECT MARKS, COUNT(*) AS COUNT FROM {selected_table} GROUP BY MARKS ORDER BY COUNT DESC LIMIT 1;  

Q: Who have the highest rating?
A: SELECT * FROM {selected_table} WHERE rating = (SELECT MAX(rating) FROM {selected_table});

Q: Who have the lowest rating?
A: SELECT * FROM {selected_table} WHERE rating = (SELECT MIN(rating) FROM {selected_table});

Q: Which subject is the teacher with the role or designation or position HoD teaching?
A: SELECT subject FROM {selected_table} WHERE LOWER(designation) = 'hod';


Q: Get students who are in both section 'A' and section 'B' (assuming a student can be in multiple sections).  
A: SELECT NAME FROM {selected_table} WHERE SECTION = 'A' INTERSECT SELECT NAME FROM {selected_table} WHERE SECTION = 'B';  

Now, given the following question, generate an SQL query **without explanations, without
 at the beginning or end, and without the word SQL in the output**.
"""
    ]

    
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
