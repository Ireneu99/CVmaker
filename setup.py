#!/usr/bin/env python3
"""
Setup script for CV Maker Inteligente project.
This script installs dependencies and sets up the development environment.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up CV Maker Inteligente...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Try to install spaCy Portuguese model
    print("\n🔄 Installing spaCy Portuguese model...")
    spacy_success = run_command("python -m spacy download pt_core_news_sm", "Installing Portuguese NLP model")
    
    if not spacy_success:
        print("⚠️  Portuguese model installation failed. Trying English model as fallback...")
        en_success = run_command("python -m spacy download en_core_web_sm", "Installing English NLP model")
        if not en_success:
            print("⚠️  NLP model installation failed. The system will work with basic analysis.")
    
    # Create necessary directories
    directories = [
        "storage/pdfs",
        "storage/logs",
        "database"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Initialize database (will be created on first run)
    print("\n📊 Database will be initialized on first backend startup.")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the backend: python run_backend.py")
    print("2. Start the frontend: python run_frontend.py")
    print("3. Open your browser to: http://localhost:8501")
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("💡 Check the README.md for more information!")

if __name__ == "__main__":
    main()
