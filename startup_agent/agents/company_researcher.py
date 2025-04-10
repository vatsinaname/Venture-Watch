import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Import necessary modules based on configuration
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

class StartupAnalysis(BaseModel):
    """Schema for startup analysis output"""
    company_name: str = Field(description="Name of the startup")
    tech_stack: List[str] = Field(description="Technologies likely used by the startup")
    hiring_needs: List[str] = Field(description="Potential roles the startup is hiring for")
    product_focus: str = Field(description="Description of the startup's main product or service")
    fit_score: int = Field(description="A score from 0-100 indicating match with user profile")
    growth_potential: str = Field(description="Assessment of the startup's growth potential")

class CompanyResearcher:
    """
    Agent responsible for researching companies and providing insights
    about their tech stack, hiring needs, and fit for the user's profile.
    """
    
    def __init__(self):
        """Initialize the CompanyResearcher"""
        self.data_dir = DATA_DIR
        self.input_file = self.data_dir / "funding_data.json"
        self.output_file = self.data_dir / "analysis_data.json"
        
        # Get the appropriate LLM based on configuration
        self.llm = self._get_llm()
        logger.info(f"CompanyResearcher initialized with {LLM_PROVIDER} LLM")
    
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
            logger.info(f"Saved analysis for {len(analysis_data)} startups to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving analysis data: {str(e)}")
    
    def _analyze_startup(self, startup_data):
        """
        Analyze a single startup using the LLM.
        
        Args:
            startup_data (dict): Startup data dictionary
            
        Returns:
            dict: Analysis of the startup
        """
        # Extract relevant information for analysis
        company_name = startup_data.get("company_name", "Unknown")
        description = startup_data.get("description", "")
        industry = startup_data.get("industry", "")
        funding_round = startup_data.get("funding_round", "")
        funding_amount = startup_data.get("funding_amount", 0)
        
        logger.info(f"Analyzing startup: {company_name}")
        
        # Set up the output parser
        parser = PydanticOutputParser(pydantic_object=StartupAnalysis)
        
        # Create the prompt template
        template = """
        You are an expert startup analyst with deep knowledge of technology stacks 
        and hiring patterns. Analyze this startup based on the information provided:
        
        Company: {company_name}
        Description: {description}
        Industry: {industry}
        Funding Round: {funding_round}
        Funding Amount: ${funding_amount} million
        
        Based on this information:
        1. Determine the likely tech stack they're using
        2. Predict roles they might be hiring for
        3. Summarize their main product focus
        4. Assess their growth potential (High/Medium/Low)
        5. Assign a fit score (0-100) for this startup based on a generic software engineer profile
        
        {format_instructions}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["company_name", "description", "industry", "funding_round", "funding_amount"],
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
                funding_amount=funding_amount
            )
            
            # Parse the result
            parsed_result = parser.parse(result)
            
            # Convert to dictionary
            analysis = parsed_result.dict()
            
            # Add original data
            analysis.update({
                "original_data": startup_data,
                "analysis_date": datetime.now().strftime("%Y-%m-%d")
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
                "analysis_date": datetime.now().strftime("%Y-%m-%d")
            }
    
    def run(self):
        """
        Run the analysis on all startups.
        
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
            analysis = self._analyze_startup(startup)
            analysis_results.append(analysis)
        
        # Save the analysis
        self._save_analysis(analysis_results)
        
        return analysis_results

if __name__ == "__main__":
    # Run standalone for testing
    researcher = CompanyResearcher()
    results = researcher.run()
    print(f"Analyzed {len(results)} startups") 