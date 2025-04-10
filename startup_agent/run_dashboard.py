#!/usr/bin/env python
"""
Run the Streamlit dashboard for Venture Watch
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

def main():
    """Run the Streamlit dashboard"""
    dashboard_path = current_dir / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"Error: Dashboard file not found at {dashboard_path}")
        sys.exit(1)
    
    print(f"Starting Streamlit dashboard from {dashboard_path}")
    
    # Run Streamlit - using shell=True for Windows compatibility
    try:
        subprocess.run([
            "streamlit", "run", str(dashboard_path), 
            "--server.port=8501", 
            "--server.address=localhost"
        ], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit not found. Please make sure it's installed.")
        print("You can install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 