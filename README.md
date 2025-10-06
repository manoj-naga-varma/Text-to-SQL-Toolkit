# 🧠 Text-to-SQL Toolkit

A powerful and user-friendly Streamlit application to **transform natural language into SQL queries** and manage your database visually.

> 🌐 Live App: [Click to Launch](https://t2sql-draft-2-by-mnv.streamlit.app/)

---

## 🚀 Features

✅ **Natural Language SQL Generator** using Google Gemini API  
✅ **Schema Creator** – visually design database tables  
✅ **Data Importer** – upload CSV/Excel to populate tables  
✅ **Table Viewer** – view, export, and delete database tables  
✅ **End-to-End Workflow** – from data structure to querying in one place  

---

## 🧩 App Modules

| Tool | Description |
|------|-------------|
| 🏠 **Home Page** | Overview dashboard, stats, feature highlights |
| 📐 **Schema Creator** | Define and create SQLite tables dynamically |
| 📥 **Data Importer** | Upload CSV/XLSX files and import data with type inference |
| 📊 **Table Viewer** | View, filter, export, and delete existing tables |
| 📝 **SQL Query Generator** | Ask plain-English questions and get SQL instantly |

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-repo/sql-query-generator.git
cd sql-query-generator
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Add your Gemini API key  
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

---

## ▶️ Run the App

```bash
streamlit run app2.py
```

---

## 📁 Folder Structure

```
.
├── app2.py                # Main Streamlit multipage app
├── creator.py             # Schema creation logic
├── data_importer.py       # File uploader and data importer
├── viewer.py              # Table viewer and delete module
├── sql_generator.py       # Gemini-powered SQL generation
├── home.py                # Homepage dashboard and UI
├── dynamic.db             # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Light theme and UI config
└── README.md              # You are here!
```

---

## 📎 Requirements

See `requirements.txt`, but main packages include:
- `streamlit`
- `pandas`
- `openpyxl`, `xlrd` (Excel support)
- `google-generativeai`
- `dotenv`

---

## 💡 Example Questions

Try these in the SQL Generator:
- *Show me all employees in the Engineering department*
- *What is the average salary of managers?*
- *List products with inventory less than 20*
- *Find the total sales by region for Q1*

---

## 👥 Credits

Developers:

- Chekuri Manoj Naga Varma
- Jeremiah Varghese Reji (Teammate 1)
- Abishek M (Teammate 2) 
- Nagirimadugu Vamsi Reddy (Teammate 3)

---

## 📄 License

This project is for educational and personal use. For commercial use, please contact the developers.

---

## If the SQL Query Generation is not being performed, it might be due to the API Key token limit expiration. Please inform to the developer, or leave a comment here


