import streamlit as st
import pandas as pd
import sqlite3
import os
from PIL import Image

def run_home_page():
    # Custom styling for the home page
    st.markdown("""
    <style>
        .home-header {
            text-align: center;
            padding: 1rem 0;
        }
        
        .feature-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .feature-title {
            color: #2e7d32;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
            color: white;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .cta-button {
            text-align: center;
            margin: 2rem 0;
        }
        
        .testimonial {
            font-style: italic;
            padding: 1rem;
            border-left: 4px solid #4CAF50;
            background-color: #f1f8e9;
            margin: 1rem 0;
        }
        
        .section-divider {
            margin: 2rem 0;
            border-top: 1px solid #e0e0e0;
        }
        
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #666;
            font-size: 0.9rem;
        }
        
        .team-section {
            text-align: center;
            margin: 2rem 0;
        }
        
        .team-member {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            margin: 0.5rem;
            background-color: #e8f5e9;
            border-radius: 20px;
            font-weight: 500;
            color: #2e7d32;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .team-member:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .team-title {
            margin-bottom: 1rem;
            font-size: 1.3rem;
            color: #444;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown("""
    <div class="home-header">
        <h1 style="color: #2e7d32; font-size: 3rem;">Text-to-SQL Toolkit</h1>
        <p style="font-size: 1.2rem; color: #555;">
            Transform natural language into database operations with our AI-powered toolkit
        </p>
    </div>
    """, unsafe_allow_html=True)
    
   
    
    # Quick stats based on database information
    conn = sqlite3.connect("dynamic.db")
    cursor = conn.cursor()
    
    # Get number of tables
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table';")
    table_count = cursor.fetchone()[0]
    
    # Estimate total records across all tables (approximate)
    total_records = 0
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM '{table[0]}'")
            total_records += cursor.fetchone()[0]
        except:
            pass
    
    conn.close()
    
    # Dashboard stats
    st.markdown("<h2 style='text-align: center; margin-top: 2rem;'>Database Dashboard</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Tables</div>
        </div>
        """.format(table_count), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Total Records</div>
        </div>
        """.format(total_records), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">4</div>
            <div class="stat-label">Powerful Tools</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main features section with developer attribution
    st.markdown("<h2 style='text-align: center; margin: 2rem 0 1rem;'>Our Toolkit Features</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📐</div>
            <div class="feature-title">Schema Creator</div>
            <p>Design database tables with custom columns and data types. Easily define your data structure without writing SQL.</p>
         
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Table Viewer</div>
            <p>Explore your database tables with an intuitive interface. View schemas, preview data, and manage tables with ease.</p>
    
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📥</div>
            <div class="feature-title">Data Importer</div>
            <p>Import data from CSV or Excel files with intelligent type detection. Quickly populate your database with external data.</p>
          
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">SQL Query Generator</div>
            <p>Transform natural language questions into SQL queries using advanced AI. Get database insights without SQL knowledge.</p>
       
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div class="cta-button">
        <p style="font-size: 1.2rem; margin-bottom: 1rem;">Ready to get started? Navigate to any tool using the sidebar!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("<h2 style='text-align: center; margin: 2rem 0 1rem;'>How It Works</h2>", unsafe_allow_html=True)
    
    with st.expander("See the workflow", expanded=True):
        st.markdown("""
        1. **Create your schema** - Define tables and columns to structure your data
        2. **Import your data** - Upload CSV/Excel files or manually input records
        3. **View and analyze** - Explore your data with the table viewer
        4. **Ask questions in plain English** - Let AI generate the SQL for you
        """)
    
    # Example queries section
    st.markdown("<h2 style='text-align: center; margin: 2rem 0 1rem;'>Example Queries You Can Ask</h2>", unsafe_allow_html=True)
    
    example_queries = [
        "Show me all customers from California",
        "What's the average order value by month?",
        "Find products with less than 10 items in stock",
        "Which employees have the highest sales in Q1?"
    ]
    
    for query in example_queries:
        st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 0.8rem; border-radius: 5px; margin-bottom: 0.5rem;">
            <span style="color: #2e7d32; font-weight: 500;">→</span> {query}
        </div>
        """, unsafe_allow_html=True)
    
   
    
    # Tips & resources section
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin: 1rem 0;'>Tips & Resources</h2>", unsafe_allow_html=True)
    
    with st.expander("Best Practices"):
        st.markdown("""
        - Start by creating a clear schema that represents your data model
        - Use consistent naming conventions for tables and columns
        - For text-to-SQL, be specific in your questions for better results
        - Import clean, well-formatted data for best results
        """)
    
    with st.expander("Common Issues & Solutions"):
        st.markdown("""
        - **Issue**: SQL generation not working
          **Solution**: Make sure your API key is properly set in the .env file
          
        - **Issue**: Data import errors
          **Solution**: Check your CSV/Excel file for inconsistent data types or special characters
          
        - **Issue**: Table not appearing in viewer
          **Solution**: Refresh the page or check if the table was created successfully
        """)
    
    # Footer section with team credits
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <p>© 2025 Text-to-SQL Toolkit | Built with ❤️ using Streamlit</p>
        <p>Developed by Jeremiah Varghese Reji, Abishek M, Chekuri Manoj Naga Varma, and Nagirimadugu Vamsi Reddy </p>
        
    </div>
    """, unsafe_allow_html=True)