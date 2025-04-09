import os
import json
from pathlib import Path
from typing import Dict, List, Any

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from startup_agent.config import OPENAI_API_KEY, DATA_DIR

class CompanyResearcher:
    """
    Agent 2: Company Researcher
    Analyzes startup data using LLMs to extract insights about
    tech stack, product roadmap, and culture
    """
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.llm = ChatOpenAI(
            temperature=0.2,
            model_name="gpt-3.5-turbo",
            openai_api_key=self.api_key
        )
    
    def analyze_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single company's data to extract tech stack and other insights
        
        Args:
            company_data: Dictionary containing company information
            
        Returns:
            Dictionary with additional analysis
        """
        if not self.api_key:
            print("Error: OPENAI_API_KEY is not set in the environment variables")
            return company_data
            
        # Create a prompt for the LLM
        prompt_template = PromptTemplate(
            input_variables=["company_name", "description", "categories"],
            template="""
            You are an expert technology analyst who specializes in identifying the technology stack
            and potential hiring needs of startups based on their description and industry.
            
            Company: {company_name}
            Description: {description}
            Categories: {categories}
            
            Based solely on this information, please provide:
            1. The likely technology stack this company uses (programming languages, frameworks, databases, cloud services)
            2. Potential technical roles they might be hiring for
            3. The company's main product focus
            
            Format your response as a JSON with these keys: "tech_stack" (list), "hiring_needs" (list), "product_focus" (string)
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        # Prepare input for the LLM
        categories_str = ", ".join(company_data.get("categories", []))
        
        # Run the LLM
        try:
            result = chain.run({
                "company_name": company_data.get("company_name", ""),
                "description": company_data.get("description", ""),
                "categories": categories_str
            })
            
            # Parse the JSON result
            try:
                analysis = json.loads(result)
                # Add the analysis to the company data
                company_data.update({
                    "tech_stack": analysis.get("tech_stack", []),
                    "hiring_needs": analysis.get("hiring_needs", []),
                    "product_focus": analysis.get("product_focus", "")
                })
            except json.JSONDecodeError:
                print(f"Error parsing LLM response as JSON for {company_data.get('company_name')}")
                # Try to extract information in a more forgiving way
                company_data.update(self._extract_from_text(result))
                
        except Exception as e:
            print(f"Error running LLM analysis: {e}")
            
        return company_data
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract information from text when JSON parsing fails"""
        analysis = {
            "tech_stack": [],
            "hiring_needs": [],
            "product_focus": ""
        }
        
        # Simple extraction based on section headers
        lines = text.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "tech stack" in line.lower() or "technology stack" in line.lower():
                current_section = "tech_stack"
                continue
            elif "hiring" in line.lower() or "roles" in line.lower():
                current_section = "hiring_needs"
                continue
            elif "product" in line.lower() or "focus" in line.lower():
                current_section = "product_focus"
                continue
                
            if current_section == "tech_stack" and line and ":" not in line:
                # Split by commas or other separators and clean up
                techs = [t.strip() for t in line.split(",")]
                analysis["tech_stack"].extend([t for t in techs if t])
            elif current_section == "hiring_needs" and line and ":" not in line:
                roles = [r.strip() for r in line.split(",")]
                analysis["hiring_needs"].extend([r for r in roles if r])
            elif current_section == "product_focus" and line and ":" not in line:
                if analysis["product_focus"]:
                    analysis["product_focus"] += " " + line
                else:
                    analysis["product_focus"] = line
                    
        return analysis
    
    def analyze_recent_startups(self) -> List[Dict[str, Any]]:
        """
        Analyze the most recent startup data file
        
        Returns:
            List of startups with analysis data
        """
        # Find the most recent data file
        data_files = list(DATA_DIR.glob("funding_data_*.json"))
        if not data_files:
            print("No funding data files found")
            return []
            
        # Sort by modification time (most recent first)
        most_recent_file = max(data_files, key=os.path.getmtime)
        
        print(f"Analyzing startups from {most_recent_file}...")
        
        # Load the data
        try:
            with open(most_recent_file, 'r', encoding='utf-8') as f:
                startup_data = json.load(f)
        except Exception as e:
            print(f"Error loading startup data: {e}")
            return []
            
        # Analyze each company
        analyzed_startups = []
        for company in startup_data:
            print(f"Analyzing {company.get('company_name', 'Unknown')}...")
            analyzed_company = self.analyze_company(company)
            analyzed_startups.append(analyzed_company)
            
        # Save the analyzed data
        output_filename = most_recent_file.stem + "_analyzed.json"
        output_path = DATA_DIR / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analyzed_startups, f, indent=2)
            
        print(f"Saved {len(analyzed_startups)} analyzed startup records to {output_path}")
        return analyzed_startups


if __name__ == "__main__":
    # Test the agent
    researcher = CompanyResearcher()
    researcher.analyze_recent_startups() 