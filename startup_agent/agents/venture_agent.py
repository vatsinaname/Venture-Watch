import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

# Import existing agents
from startup_agent.agents.startup_collector import StartupCollector
from startup_agent.agents.company_researcher import CompanyResearcher
from startup_agent.agents.report_generator import ReportGenerator

# Import config
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

class StartupAgentMemory:
    """Memory system for tracking startups and conversation history"""
    
    def __init__(self):
        """Initialize the memory system"""
        self.memory = ConversationBufferMemory(return_messages=True)
        self.startup_database = {}
        
    def add_startups(self, startups):
        """
        Add new startups to memory
        
        Args:
            startups: List of startup dictionaries
        """
        if not startups:
            return
            
        for startup in startups:
            if isinstance(startup, dict) and "company_name" in startup:
                self.startup_database[startup["company_name"]] = startup
        
        # Create a summary message for the memory
        summary = f"Added {len(startups)} startups to the database."
        self.memory.chat_memory.add_user_message(summary)
        self.memory.chat_memory.add_ai_message(f"Now tracking {len(self.startup_database)} startups total.")
    
    def get_relevant_startups(self, user_skills):
        """
        Retrieve startups relevant to user skills
        
        Args:
            user_skills: List of skill strings
            
        Returns:
            List of relevant startup dictionaries
        """
        if not user_skills:
            return list(self.startup_database.values())
            
        relevant = [s for s in self.startup_database.values() 
                  if any(skill.lower() in str(s).lower() for skill in user_skills)]
        return relevant
    
    def get_chat_history(self):
        """Get the conversation history as a formatted string"""
        return self.memory.load_memory_variables({})["history"]
    
    def add_user_message(self, message):
        """Add a user message to the memory"""
        self.memory.chat_memory.add_user_message(message)
    
    def add_ai_message(self, message):
        """Add an AI message to the memory"""
        self.memory.chat_memory.add_ai_message(message)


class VentureAgentPlanner:
    """Plans the agent's actions based on user goals and current state"""
    
    def __init__(self, llm):
        """
        Initialize the planner with an LLM
        
        Args:
            llm: Language model to use for planning
        """
        self.llm = llm
        self.planning_prompt = PromptTemplate.from_template("""
        You are planning how to help a job seeker find relevant startup opportunities.
        
        User profile:
        - Skills: {skills}
        - Experience level: {experience}
        - Industry preferences: {industry_preferences}
        
        Current state:
        {current_state}
        
        Break this down into a step-by-step plan with 3-5 concrete steps:
        """)
        
        self.planning_chain = LLMChain(llm=self.llm, prompt=self.planning_prompt)
    
    def create_plan(self, user_profile, current_state):
        """
        Generate a plan based on the current state and user profile
        
        Args:
            user_profile: Dictionary with user information
            current_state: String describing the current state
            
        Returns:
            List of plan steps
        """
        plan = self.planning_chain.run(
            skills=user_profile.get("skills", ""),
            experience=user_profile.get("experience", 0),
            industry_preferences=user_profile.get("industry_preferences", ""),
            current_state=current_state
        )
        return [step.strip() for step in plan.split("\n") if step.strip()]


class ReflectiveVentureAgent:
    """Agent that can reflect on its performance and improve"""
    
    def __init__(self, llm):
        """
        Initialize the reflective agent
        
        Args:
            llm: Language model to use for reflection
        """
        self.llm = llm
        self.reflection_prompt = PromptTemplate.from_template("""
        You've just completed a task to help a job seeker find startup opportunities.
        
        Task: {task}
        Actions taken: {actions}
        Result: {result}
        
        Reflect on your performance:
        1. What worked well?
        2. What could be improved?
        3. What should be done differently next time?
        """)
        
        self.reflection_chain = LLMChain(llm=self.llm, prompt=self.reflection_prompt)
        self.improvement_log = []
    
    def reflect(self, task, actions, result):
        """
        Reflect on the agent's performance
        
        Args:
            task: Description of the task attempted
            actions: List of actions taken
            result: The outcome of the task
            
        Returns:
            Reflection text
        """
        reflection = self.reflection_chain.run(
            task=task,
            actions=str(actions),
            result=str(result)
        )
        self.improvement_log.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "reflection": reflection
        })
        return reflection


def search_web_for_startup_info(query):
    """
    Search for additional information about a startup
    
    Args:
        query: Search query string
        
    Returns:
        Search results as a string
    """
    logger.info(f"Searching for additional info: {query}")
    # This is a placeholder. In a real implementation, you would:
    # 1. Call a search API
    # 2. Process the results
    # 3. Return the formatted information
    
    # For now, return a placeholder
    return f"Simulated search results for: {query}"


def get_llm():
    """
    Get the appropriate LLM based on configuration
    
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


def create_venture_agent(llm):
    """
    Create an agent executor with tools for the venture agent
    
    Args:
        llm: Language model to power the agent
        
    Returns:
        AgentExecutor object
    """
    # Define tools for the agent
    tools = [
        Tool(
            name="collect_startup_data",
            func=lambda _: StartupCollector().run(),
            description="Collects data on recently funded startups from various sources"
        ),
        Tool(
            name="analyze_startup",
            func=lambda startup: CompanyResearcher()._analyze_startup(startup),
            description="Analyzes a startup's technology stack and hiring needs"
        ),
        Tool(
            name="generate_report",
            func=lambda _: ReportGenerator().generate_and_send(),
            description="Creates and sends a report with startup information"
        ),
        Tool(
            name="search_additional_info",
            func=lambda query: search_web_for_startup_info(query),
            description="Searches for additional information about a startup"
        )
    ]
    
    prompt = ChatPromptTemplate.from_template("""
    You are VentureAgent, an AI that helps job seekers find promising startup opportunities.
    Your goal is to identify, analyze, and report on startups that match a user's skills.
    
    {chat_history}
    
    User query: {input}
    
    Think about which tools to use to accomplish this task.
    {agent_scratchpad}
    """)
    
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_agentic_pipeline():
    """
    Run a fully agentic pipeline with planning, execution, and reflection
    
    Returns:
        Dictionary with results, reflection, and plan
    """
    # Get the LLM
    llm = get_llm()
    
    # Create components
    memory = StartupAgentMemory()
    planner = VentureAgentPlanner(llm)
    reflector = ReflectiveVentureAgent(llm)
    agent = create_venture_agent(llm)
    
    # Load user profile from environment
    user_profile = {
        "skills": os.getenv("USER_SKILLS", "").split(","),
        "experience": int(os.getenv("USER_EXPERIENCE", 1)),
        "industry_preferences": os.getenv("USER_INDUSTRY_PREFERENCES", "").split(",")
    }
    
    # Get current state
    startup_collector = StartupCollector()
    startup_data = startup_collector._load_startup_data()
    current_state = f"There are {len(startup_data) if startup_data else 0} startups in the database."
    
    # Generate a plan
    steps = planner.create_plan(user_profile, current_state)
    logger.info(f"Generated plan: {steps}")
    
    # Execute each step with the agent
    results = []
    for step in steps:
        logger.info(f"Executing step: {step}")
        step_result = agent.invoke({"input": step, "chat_history": memory.get_chat_history()})
        results.append(step_result)
        
        # Update memory with any new startups
        if "startups" in step_result:
            memory.add_startups(step_result["startups"])
        
        # Add interaction to memory
        memory.add_user_message(step)
        memory.add_ai_message(str(step_result.get("output", "")))
    
    # Reflect on performance
    reflection = reflector.reflect(
        task="Find relevant startup opportunities",
        actions=steps,
        result=results
    )
    logger.info(f"Agent reflection: {reflection}")
    
    return {
        "results": results,
        "reflection": reflection,
        "plan": steps
    }


if __name__ == "__main__":
    # Execute the agentic pipeline if run directly
    results = run_agentic_pipeline()
    print(f"Completed agentic pipeline with {len(results['plan'])} steps") 