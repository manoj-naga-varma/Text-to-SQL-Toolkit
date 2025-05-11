import streamlit as st
from creator import run_schema_creator
from viewer import run_table_viewer
from sql_generator import run_sql_generator
from data_importer import run_data_importer
from home import run_home_page

# Page Configuration
st.set_page_config(
    page_title="Text-to-SQL Toolkit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Title and Header
st.markdown("""
    <style>
        .main-title {
            text-align: center; 
            color: #2e7d32; 
            font-size: 48px; 
            font-weight: 700;
        }
        .subtitle {
            text-align: center; 
            font-size: 20px; 
            color: #555;
            margin-top: -15px;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
        }
        
        /* Enhanced sidebar styling */
        .css-1d391kg {
            padding-top: 1rem;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Cards and containers */
        div.block-container {
            padding-top: 2rem;
        }
        
        /* Footer styling */
        footer {
            text-align: center;
            padding-top: 2rem;
            color: #666;
            font-size: 0.8rem;
        }
        
        /* Streamlit progress bars */
        div.stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        
        /* Custom metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: bold;
            color: #2e7d32;
        }
        
        /* Global Anchor styling */
        a {
            color: #2e7d32 !important;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# Enhanced sidebar navigation with icons and descriptions
st.sidebar.title("🧭 Navigation")

# Add logo or branding to sidebar
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #2e7d32;">🧠 Text-to-SQL</h2>
        <p style="font-size: 0.9rem; margin-top: -15px;">Intelligent Database Tools</p>
    </div>
""", unsafe_allow_html=True)

# Improved radio buttons
page = st.sidebar.radio(
    "Select a Tool", 
    [
        "🏠 Home",
        "📐 Schema Creator",
        "📥 Data Importer",
        "📊 Table Viewer",
        "📝 SQL Query Generator"
    ],
    index=0
)

# Main Page Rendering with titles hidden when not in home page
if page == "🏠 Home":
    run_home_page()
    
elif page == "📐 Schema Creator":
    st.markdown("<div class='main-title'>🧠 Text-to-SQL Toolkit</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Create schemas, view data, and generate SQL using plain English</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #bbb; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
    st.subheader("📐 Schema Creator")
    st.write("Define new tables or upload existing schema files for your database.")
    
    # Progress animation
    with st.spinner("Loading schema tools..."):
        run_schema_creator()

elif page == "📥 Data Importer":
    st.markdown("<div class='main-title'>🧠 Text-to-SQL Toolkit</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Create schemas, view data, and generate SQL using plain English</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #bbb; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
   
    
    with st.spinner("Loading import tools..."):
        run_data_importer()

elif page == "📊 Table Viewer":
    st.markdown("<div class='main-title'>🧠 Text-to-SQL Toolkit</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Create schemas, view data, and generate SQL using plain English</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #bbb; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
    st.subheader("📊 Table Viewer")
    st.write("Explore the contents of your tables easily and understand your data.")
    
    with st.spinner("Fetching table data..."):
        run_table_viewer()

elif page == "📝 SQL Query Generator":
    st.markdown("<div class='main-title'>🧠 Text-to-SQL Toolkit</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Create schemas, view data, and generate SQL using plain English</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #bbb; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    
    st.subheader("📝 SQL Query Generator")
    st.write("Type a question in plain English and get the corresponding SQL query.")
    
    with st.spinner("Activating AI..."):
        run_sql_generator()

