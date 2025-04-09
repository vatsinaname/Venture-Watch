#!/usr/bin/env python
"""
Install the startup-agent package in development mode
"""

import os
import sys
import subprocess

def main():
    """Install the package in development mode"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the directory containing setup.py
    os.chdir(script_dir)
    
    # Install in development mode
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-e", "."
    ])
    
    print("Successfully installed startup-agent in development mode")
    print("You can now run the agent with: startup-agent --run")

if __name__ == "__main__":
    main() 