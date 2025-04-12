import os
import time
import schedule
import logging
import argparse
from pathlib import Path

from startup_agent.agents.startup_collector import StartupCollector
from startup_agent.agents.company_researcher import CompanyResearcher
from startup_agent.agents.report_generator import ReportGenerator
from startup_agent.agents.venture_agent import run_agentic_pipeline
from startup_agent.agents.enhanced_analyzer import EnhancedAnalyzer
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

def run_agent_pipeline(use_enhanced=False, use_agentic=False):
    """
    Run the full agent pipeline:
    1. Collect startup funding data
    2. Analyze the data with LLMs
    3. Generate and send a report
    
    Args:
        use_enhanced (bool): Whether to use the enhanced analyzer
        use_agentic (bool): Whether to use the fully agentic pipeline
        
    Returns:
        bool: Success status
    """
    # If using the agentic approach, delegate to that function
    if use_agentic:
        logger.info("Running fully agentic pipeline")
        try:
            result = run_agentic_pipeline()
            logger.info(f"Agentic pipeline completed with {len(result['plan'])} steps")
            return True
        except Exception as e:
            logger.error(f"Error in agentic pipeline: {e}", exc_info=True)
            return False
    
    # Otherwise, run the traditional pipeline
    logger.info("Starting traditional agent pipeline")
    
    try:
        # Step 1: Collect startup funding data
        logger.info("Running Startup Collector agent")
        collector = StartupCollector()
        startup_data = collector.run()
        
        if not startup_data:
            logger.warning("No startup data collected, aborting pipeline")
            return False
            
        # Step 2: Analyze the data
        logger.info("Running analysis step")
        
        if use_enhanced:
            # Use the enhanced analyzer with chain-of-thought reasoning
            analyzer = EnhancedAnalyzer()
            analyzed_data = analyzer.run()
        else:
            # Use the regular company researcher
            researcher = CompanyResearcher()
            analyzed_data = researcher.run()
        
        if not analyzed_data:
            logger.warning("No analyzed data generated, aborting pipeline")
            return False
            
        # Step 3: Generate and send the report
        logger.info("Running Report Generator agent")
        generator = ReportGenerator()
        result = generator.run()
        
        if result:
            logger.info("Pipeline completed successfully")
        else:
            logger.warning("Failed to generate or send report")
            
        return result
        
    except Exception as e:
        logger.error(f"Error in agent pipeline: {e}", exc_info=True)
        return False

def schedule_pipeline(use_enhanced=False, use_agentic=False):
    """
    Schedule the pipeline to run according to configuration
    
    Args:
        use_enhanced (bool): Whether to use the enhanced analyzer
        use_agentic (bool): Whether to use the fully agentic pipeline
    """
    if REPORT_FREQUENCY.lower() == 'daily':
        schedule.every().day.at("08:00").do(run_agent_pipeline, use_enhanced, use_agentic)
        logger.info(f"Pipeline scheduled to run daily at 08:00 (Enhanced: {use_enhanced}, Agentic: {use_agentic})")
    elif REPORT_FREQUENCY.lower() == 'weekly':
        schedule.every().monday.at("08:00").do(run_agent_pipeline, use_enhanced, use_agentic)
        logger.info(f"Pipeline scheduled to run weekly on Monday at 08:00 (Enhanced: {use_enhanced}, Agentic: {use_agentic})")
    else:
        logger.error(f"Invalid REPORT_FREQUENCY: {REPORT_FREQUENCY}")
        return
        
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Startup Agent pipeline")
    parser.add_argument("--schedule", action="store_true", help="Schedule the pipeline instead of running immediately")
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced analysis with chain-of-thought reasoning")
    parser.add_argument("--agentic", action="store_true", help="Use the fully agentic pipeline with planning and reflection")
    args = parser.parse_args()
    
    if args.schedule:
        # Schedule the pipeline
        schedule_pipeline(args.enhanced, args.agentic)
    else:
        # Run the pipeline once
        run_agent_pipeline(args.enhanced, args.agentic) 