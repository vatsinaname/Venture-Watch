#!/usr/bin/env python
"""
Command line interface for the Startup AI Agent
"""

import argparse
import sys
import logging

from startup_agent.main import run_agent_pipeline, schedule_pipeline

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Startup AI Agent - Find funded startups that match your skills"
    )
    
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the full pipeline once"
    )
    
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Schedule the pipeline to run according to configuration"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the command line interface"""
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("startup_agent.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    if args.run:
        logger.info("Running pipeline once")
        success = run_agent_pipeline()
        sys.exit(0 if success else 1)
    elif args.schedule:
        logger.info("Starting scheduled pipeline")
        schedule_pipeline()
    else:
        # If no arguments provided, run the pipeline once
        logger.info("No arguments provided, running pipeline once")
        success = run_agent_pipeline()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 