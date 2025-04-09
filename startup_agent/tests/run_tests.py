#!/usr/bin/env python
"""
Run all tests for the Startup AI Agent
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the startup_agent package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def run_tests():
    """Discover and run all tests"""
    # Start from the current directory
    start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover all tests in the current directory
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 