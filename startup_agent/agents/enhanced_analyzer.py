import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Import from the existing researcher
from startup_agent.agents.company_researcher import StartupAnalysis
from startup_agent.config import (
    DATA_DIR, 
    LLM_PROVIDER, 
    OPENAI_API_KEY, 
    GROQ_API_KEY, 
    GROQ_MODEL,
    DEFAULT_LLM_MODEL
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAnalyzer:
    """
    Enhanced startup analyzer that uses chain-of-thought reasoning
    to provide more detailed and accurate startup analysis.
    """
    
    def __init__(self):
        """Initialize the enhanced analyzer"""
        self.data_dir = DATA_DIR
        self.input_file = self.data_dir / "funding_data.json"
        self.output_file = self.data_dir / "enhanced_analysis.json"
        
        # Get the appropriate LLM based on configuration
        self.llm = self._get_llm()
        logger.info(f"EnhancedAnalyzer initialized with {LLM_PROVIDER} LLM")
    
    def _get_llm(self):
        """
        Get the appropriate LLM based on configuration.
        
        Returns:
            LLM: The configured language model
        """
        if LLM_PROVIDER == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model_name=GROQ_MODEL
            )
        else:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                openai_api_key=OPENAI_API_KEY,
                model=DEFAULT_LLM_MODEL
            )
    
    def _load_startup_data(self):
        """
        Load startup data from the input file.
        
        Returns:
            list: List of startup data dictionaries
        """
        if not os.path.exists(self.input_file):
            logger.warning(f"Input file not found: {self.input_file}")
            return []
        
        try:
            with open(self.input_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} startups from {self.input_file}")
            return data
        except Exception as e:
            logger.error(f"Error loading startup data: {str(e)}")
            return []
    
    def _save_analysis(self, analysis_data):
        """
        Save analysis data to the output file.
        
        Args:
            analysis_data (list): List of analysis data dictionaries
        """
        try:
            with open(self.output_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            logger.info(f"Saved enhanced analysis for {len(analysis_data)} startups to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving analysis data: {str(e)}")
    
    def analyze_startup(self, startup_data, user_profile=None):
        """
        Analyze a single startup using chain-of-thought reasoning.
        
        Args:
            startup_data (dict): Startup data dictionary
            user_profile (dict, optional): User profile for personalized matching
            
        Returns:
            dict: Enhanced analysis of the startup
        """
        # Extract relevant information for analysis
        company_name = startup_data.get("company_name", "Unknown")
        description = startup_data.get("description", "")
        industry = startup_data.get("industry", "")
        funding_round = startup_data.get("funding_round", "")
        funding_amount = startup_data.get("funding_amount", 0)
        
        # Get user profile details
        user_role = "software engineer"
        user_skills = "python,javascript,react,data analysis"
        
        if user_profile:
            user_role = user_profile.get("role", user_role)
            if "skills" in user_profile:
                if isinstance(user_profile["skills"], list):
                    user_skills = ",".join(user_profile["skills"])
                else:
                    user_skills = user_profile["skills"]
        
        logger.info(f"Analyzing startup with chain-of-thought: {company_name}")
        
        # Set up the output parser
        parser = PydanticOutputParser(pydantic_object=StartupAnalysis)
        
        # Create the prompt template with step-by-step reasoning
        template = """
        You're analyzing a startup to determine its potential fit for a job seeker.
        
        Startup information:
        Company: {company_name}
        Description: {description}
        Industry: {industry}
        Funding Round: {funding_round}
        Funding Amount: ${funding_amount} million
        
        Let's approach this step-by-step:
        
        1) First, identify the main product or service this company offers.
        2) Based on the product, what technologies would they likely be using?
        3) Given their funding stage and amount, what roles would they be hiring for?
        4) How likely are they to grow rapidly in the next 12 months?
        5) How well does this match the profile of a {user_role} with skills in {user_skills}?
        
        For each step, explain your reasoning before giving your final answer.
        
        {format_instructions}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["company_name", "description", "industry", "funding_round", 
                            "funding_amount", "user_role", "user_skills"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create the LLM chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            # Run the chain
            result = chain.run(
                company_name=company_name,
                description=description,
                industry=industry,
                funding_round=funding_round,
                funding_amount=funding_amount,
                user_role=user_role,
                user_skills=user_skills
            )
            
            # Parse the result
            parsed_result = parser.parse(result)
            
            # Convert to dictionary
            analysis = parsed_result.dict()
            
            # Add original data and raw reasoning
            analysis.update({
                "original_data": startup_data,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "raw_reasoning": result
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing startup {company_name}: {str(e)}")
            # Return basic info to avoid breaking the pipeline
            return {
                "company_name": company_name,
                "tech_stack": [],
                "hiring_needs": [],
                "product_focus": "Unable to analyze",
                "fit_score": 0,
                "growth_potential": "Unknown",
                "original_data": startup_data,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "raw_reasoning": f"Error: {str(e)}"
            }
    
    def run(self, user_profile=None):
        """
        Run the enhanced analysis on all startups.
        
        Args:
            user_profile (dict, optional): User profile for personalized matching
            
        Returns:
            list: List of analyzed startups
        """
        # Load startup data
        startup_data = self._load_startup_data()
        
        if not startup_data:
            logger.warning("No startup data found for analysis")
            return []
        
        # Analyze each startup
        analysis_results = []
        for startup in startup_data:
            analysis = self.analyze_startup(startup, user_profile)
            analysis_results.append(analysis)
        
        # Save the enhanced analysis
        self._save_analysis(analysis_results)
        
        return analysis_results

if __name__ == "__main__":
    # Run standalone for testing
    from startup_agent.config import USER_SKILLS, USER_EXPERIENCE
    
    # Create a simple user profile
    user_profile = {
        "role": "software engineer",
        "skills": USER_SKILLS.split(","),
        "experience": USER_EXPERIENCE
    }
    
    # Run the analyzer
    analyzer = EnhancedAnalyzer()
    results = analyzer.run(user_profile)
    print(f"Analyzed {len(results)} startups with enhanced reasoning") 