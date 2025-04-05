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

    example_queries = """
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
Q: Retrieve all students along with their teacher names (assuming a teachers table exists).
A: SELECT s.name, t.teacher_name FROM {selected_table} s JOIN teachers t ON LOWER(s.teacher_id) = LOWER(t.id);

Q: Get the list of students along with the subjects they are studying (assuming a subjects table exists).
A: SELECT s.name, sub.subject_name FROM {selected_table} s JOIN subjects sub ON LOWER(s.subject_id) = LOWER(sub.id);

Q: Find students who have not received marks and their class names (assuming a classes table exists).
A: SELECT s.name, c.class_name FROM {selected_table} s LEFT JOIN classes c ON LOWER(s.class_id) = LOWER(c.id) WHERE s.marks IS NULL;

Q: What is the salary of the teacher with the designation HoD?
A: SELECT s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE LOWER(t.designation) = LOWER('HoD');

Q: List the names and salaries of all teachers.
A: SELECT t.name, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name);

Q: Get the subject and salary of teachers with a rating above 4.
A: SELECT t.subject, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE t.rating > 4;

Q: Find teachers earning more than 50,000.
A: SELECT t.name, t.designation FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE s.salary > 50000;

Q: Get the names of HoDs who earn less than 60,000.
A: SELECT t.name FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE LOWER(t.designation) = LOWER('HoD') AND s.salary < 60000;

Q: Show the designation and salary of each teacher sorted by salary descending.
A: SELECT t.designation, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) ORDER BY s.salary DESC;

Q: Who are the teachers without a recorded salary?
A: SELECT t.name FROM teacher t LEFT JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE s.salary IS NULL;

Q: Get the total salary paid to all teachers.
A: SELECT SUM(s.salary) FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name);

Q: What is the average salary for each designation?
A: SELECT t.designation, AVG(s.salary) AS avg_salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) GROUP BY t.designation;

Q: Show the top 3 highest-paid teachers with their subjects.
A: SELECT t.name, t.subject, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) ORDER BY s.salary DESC LIMIT 3;

Q: List all teachers and their salary if available.
A: SELECT t.name, s.salary FROM teacher t LEFT JOIN salary s ON LOWER(t.name) = LOWER(s.name);

Q: Who are the teachers for whom salary details are not available?
A: SELECT t.name FROM teacher t LEFT JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE s.salary IS NULL;

Q: Show all salary records even if a teacher entry doesn't exist.
A: SELECT s.name, s.salary FROM salary s LEFT JOIN teacher t ON LOWER(t.name) = LOWER(s.name);

Q: Show all records from both teacher and salary tables, even if there’s no match.
A: SELECT t.name, t.designation, s.salary FROM teacher t LEFT JOIN salary s ON LOWER(t.name) = LOWER(s.name) UNION SELECT s.name, NULL AS designation, s.salary FROM salary s LEFT JOIN teacher t ON LOWER(t.name) = LOWER(s.name) WHERE t.name IS NULL;

Q: Show details of teachers who are listed in the salary table.
A: SELECT * FROM teacher WHERE LOWER(name) IN (SELECT LOWER(name) FROM salary);

Q: List teachers who are not in the salary table.
A: SELECT * FROM teacher WHERE LOWER(name) NOT IN (SELECT LOWER(name) FROM salary);

Q: Find all teachers with known salary amounts.
A: SELECT t.name, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE s.salary IS NOT NULL;

Q: Show teachers whose salary is more than the average salary.
A: SELECT t.name, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE s.salary > (SELECT AVG(salary) FROM salary);

Q: List teachers with designation ‘Professor’ and salary above 70,000.
A: SELECT t.name, s.salary FROM teacher t JOIN salary s ON LOWER(t.name) = LOWER(s.name) WHERE LOWER(t.designation) = LOWER('Professor') AND s.salary > 70000;

Q: Show teachers and their salary, or 0 if salary is not recorded.
A: SELECT t.name, COALESCE(s.salary, 0) AS salary FROM teacher t LEFT JOIN salary s ON LOWER(t.name) = LOWER(s.name);

Q: Show all teachers whose salary is missing (no match in salary table).
A: SELECT t.* FROM teacher t  LEFT JOIN salary s ON LOWER(t.name) = LOWER(s.name)  WHERE s.salary IS NULL;

Q: Which teacher (without all available details) has the highest salary?
A: SELECT t.*, s.salary FROM salary s LEFT JOIN teacher t ON LOWER(t.name) = LOWER(s.name) WHERE s.salary = (SELECT MAX(salary) FROM salary);


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

    """

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
