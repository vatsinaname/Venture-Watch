#!/usr/bin/env python
"""
Main entry point for Venture-Watch

This script provides a command-line interface to run different components
of the Venture-Watch system.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_collector():
    """Run the startup collector agent"""
    print("Running startup collector agent...")
    from startup_agent.agents.startup_collector import StartupCollector
    collector = StartupCollector()
    results = collector.run()
    print(f"Collected {len(results)} startup funding entries")
    return results

def update_database():
    """Update the persistent startup database with new search results"""
    print("Updating startup database with new search results...")
    from startup_agent.agents.startup_collector import StartupCollector
    collector = StartupCollector()
    
    # Run the collector to get new results
    results = collector.run()
    
    # Update the database with the new results
    updated_db = collector.update_startup_database(results)
    
    print(f"Database updated with {len(updated_db)} total startups ({len(results)} new entries)")
    return updated_db

def run_researcher():
    """Run the company researcher agent"""
    print("Running company researcher agent...")
    from startup_agent.agents.company_researcher import CompanyResearcher
    researcher = CompanyResearcher()
    results = researcher.run()
    print(f"Analyzed {len(results)} startups")
    return results

def run_dashboard():
    """Run the Streamlit dashboard"""
    print("Starting Streamlit dashboard...")
    try:
        # Using a subprocess to run the dashboard
        subprocess.Popen([
            "streamlit", "run", 
            "simple_dashboard.py", 
            "--server.port=8501"
        ], shell=True)
        print("Dashboard is now running at http://localhost:8501")
    except Exception as e:
        print(f"Error starting dashboard: {e}")

def run_report_generator():
    """Run the report generator"""
    print("Generating reports...")
    from startup_agent.agents.report_generator import ReportGenerator
    generator = ReportGenerator()
    report_path = generator.generate_report()
    print(f"Report generated at {report_path}")
    return report_path

def run_all():
    """Run the complete pipeline"""
    print("Running complete Venture-Watch pipeline...")
    # Update the database with new search results
    updated_db = update_database()
    
    if updated_db:
        # Analyze the startups
        analyzed_data = run_researcher()
        if analyzed_data:
            report_path = run_report_generator()
    
    # Start the dashboard
    run_dashboard()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Venture-Watch - Startup Funding Intelligence")
    
    parser.add_argument("--collect", action="store_true", help="Run the startup collector agent")
    parser.add_argument("--analyze", action="store_true", help="Run the company researcher agent")
    parser.add_argument("--report", action="store_true", help="Generate reports")
    parser.add_argument("--dashboard", action="store_true", help="Start the dashboard")
    parser.add_argument("--update-db", action="store_true", help="Update the startup database with new search results")
    parser.add_argument("--all", action="store_true", help="Run the complete pipeline")
    
    args = parser.parse_args()
    
    # If no args provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Run the requested components
    if args.all:
        run_all()
    else:
        if args.collect:
            run_collector()
        if args.update_db:
            update_database()
        if args.analyze:
            run_researcher()
        if args.report:
            run_report_generator()
        if args.dashboard:
            run_dashboard()

if __name__ == "__main__":
    main() 