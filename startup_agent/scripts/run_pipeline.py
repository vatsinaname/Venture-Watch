#!/usr/bin/env python
"""
Run the Startup AI Agent pipeline directly
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the startup_agent package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from startup_agent.main import run_agent_pipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the agent pipeline"""
    logger.info("Starting the Startup AI Agent pipeline...")
    
    success = run_agent_pipeline()
    
    if success:
        logger.info("Pipeline completed successfully!")
    else:
        logger.error("Pipeline failed to complete")
        sys.exit(1)

if __name__ == "__main__":
    main() 