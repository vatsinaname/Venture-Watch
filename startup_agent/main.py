import os
import time
import schedule
import logging
from pathlib import Path

from startup_agent.agents.startup_collector import StartupCollector
from startup_agent.agents.company_researcher import CompanyResearcher
from startup_agent.agents.report_generator import ReportGenerator
from startup_agent.config import REPORT_FREQUENCY

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("startup_agent.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_agent_pipeline():
    """
    Run the full agent pipeline:
    1. Collect startup funding data
    2. Analyze the data with LLMs
    3. Generate and send a report
    """
    logger.info("Starting agent pipeline")
    
    try:
        # Step 1: Collect startup funding data
        logger.info("Running Startup Collector agent")
        collector = StartupCollector()
        startup_data = collector.collect_and_save()
        
        if not startup_data:
            logger.warning("No startup data collected, aborting pipeline")
            return False
            
        # Step 2: Analyze the data
        logger.info("Running Company Researcher agent")
        researcher = CompanyResearcher()
        analyzed_data = researcher.analyze_recent_startups()
        
        if not analyzed_data:
            logger.warning("No analyzed data generated, aborting pipeline")
            return False
            
        # Step 3: Generate and send the report
        logger.info("Running Report Generator agent")
        generator = ReportGenerator()
        result = generator.generate_and_send()
        
        if result:
            logger.info("Pipeline completed successfully")
        else:
            logger.warning("Failed to generate or send report")
            
        return result
        
    except Exception as e:
        logger.error(f"Error in agent pipeline: {e}", exc_info=True)
        return False

def schedule_pipeline():
    """
    Schedule the pipeline to run according to configuration
    """
    if REPORT_FREQUENCY.lower() == 'daily':
        schedule.every().day.at("08:00").do(run_agent_pipeline)
        logger.info("Pipeline scheduled to run daily at 08:00")
    elif REPORT_FREQUENCY.lower() == 'weekly':
        schedule.every().monday.at("08:00").do(run_agent_pipeline)
        logger.info("Pipeline scheduled to run weekly on Monday at 08:00")
    else:
        logger.error(f"Invalid REPORT_FREQUENCY: {REPORT_FREQUENCY}")
        return
        
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # If run directly, execute the pipeline once
    run_agent_pipeline() 