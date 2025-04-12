#!/usr/bin/env python3
"""
Simple entry point script to run the Venture Watch dashboard
"""

import sys
import os
from pathlib import Path
import importlib.util

# Add startup_agent to the path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    # First try to import from startup_agent
    from startup_agent.dashboard.app import app
    print("Successfully imported dashboard app from startup_agent directory")
    
    # Run the app
    if __name__ == "__main__":
        print("Starting Venture Watch dashboard...")
        app.run_server(debug=True, host="0.0.0.0")
except ImportError as e:
    print(f"Import error: {e}")
    print("Checking alternative paths...")
    
    # If that fails, try to import from the nested Venture-Watch directory
    nested_dir = current_dir / "Venture-Watch"
    if nested_dir.exists():
        sys.path.append(str(nested_dir))
        try:
            from startup_agent.dashboard.app import app
            print("Successfully imported dashboard app from nested Venture-Watch directory")
            
            # Run the app
            if __name__ == "__main__":
                print("Starting Venture Watch dashboard...")
                app.run_server(debug=True, host="0.0.0.0")
        except ImportError as e2:
            print(f"Second import error: {e2}")
            print("Could not find the dashboard app module. Please check the directory structure.")
    else:
        print("Nested Venture-Watch directory not found.")
        print("Could not find the dashboard app module. Please check the directory structure.") 