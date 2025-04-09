#!/usr/bin/env python
"""
Run the Startup AI Agent without installing
"""

import sys
import argparse
from startup_agent.main import run_agent_pipeline, schedule_pipeline

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Startup AI Agent - Find funded startups that match your skills"
    )
    
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Schedule the pipeline to run according to configuration"
    )
    
    return parser.parse_args()

def main():
    """Run the Startup AI Agent"""
    args = parse_args()
    
    if args.schedule:
        print("Starting scheduled pipeline...")
        schedule_pipeline()
    else:
        print("Running pipeline once...")
        result = run_agent_pipeline()
        sys.exit(0 if result else 1)

if __name__ == "__main__":
    main() 