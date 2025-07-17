#!/usr/bin/env python3
"""
Script to run the Streamlit frontend application.
"""

import streamlit.web.cli as stcli
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🎨 Starting CV Maker Frontend (Streamlit)...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("🔄 Auto-reload enabled for development")
    print("⚠️  Make sure the backend is running on http://localhost:8000")
    print("-" * 50)
    
    # Set Streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        "frontend/streamlit/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ]
    
    # Run Streamlit
    stcli.main()
