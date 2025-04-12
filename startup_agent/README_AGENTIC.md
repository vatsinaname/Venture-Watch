# Agentic Startup Assistant

This document provides information about the agentic features added to the Venture-Watch system.

## What's New: Agentic Features

The system has been enhanced with several agentic capabilities to make it more intelligent, flexible, and autonomous:

1. **Dynamic Planning**: The agent can create a step-by-step plan tailored to the user's profile and current database state
2. **Tool Selection**: The agent can choose which tools to use based on context rather than following a fixed sequence
3. **Memory System**: The agent maintains memory of past interactions and discovered startups
4. **Chain-of-Thought Analysis**: Enhanced startup analysis with step-by-step reasoning
5. **Self-Reflection**: The agent evaluates its own performance and suggests improvements

## Components

### VentureAgent

The main agent that orchestrates the system using the ReAct framework (Reasoning + Acting). It has access to various tools and can decide which to use based on the user's needs.

### StartupAgentMemory

A memory system that maintains:
- Conversation history
- Discovered startups database
- Relevance tracking

### VentureAgentPlanner

Creates dynamic plans based on:
- User skills and preferences
- Current system state
- Historical performance

### EnhancedAnalyzer

Provides in-depth analysis of startups using chain-of-thought reasoning to:
- Identify likely tech stacks with better accuracy
- Predict hiring needs based on funding stage and amount
- Evaluate fit for specific user skills

### ReflectiveVentureAgent

Adds self-improvement capabilities:
- Evaluates the quality of agent decisions
- Identifies areas for improvement
- Maintains an improvement log

## Using the Agentic System

You can use the agentic system in several ways:

### Command Line Options

```bash
# Run with the fully agentic approach
python -m startup_agent.main --agentic

# Run with enhanced analysis only
python -m startup_agent.main --enhanced

# Schedule the agentic system
python -m startup_agent.main --schedule --agentic
```

### Programmatic Usage

```python
from startup_agent.agents.venture_agent import run_agentic_pipeline

# Run the agentic pipeline
results = run_agentic_pipeline()

# Access the plan, results, and reflection
plan = results["plan"]
execution_results = results["results"]
reflection = results["reflection"]
```

### Web Interface

The dashboard includes a new "Agentic Mode" toggle that activates the full agentic system when enabled.

## Benefits of the Agentic Approach

1. **More Targeted Results**: The system better matches startups to your specific skills
2. **Improved Reasoning**: Chain-of-thought analysis provides more accurate evaluations
3. **Adaptability**: The system adjusts its approach based on the available data
4. **Self-Improvement**: Gets better over time through reflection
5. **Transparency**: Explains its reasoning and decision-making process

## Configuration

The agentic behavior can be customized through environment variables in your `.env` file:

```
# User Profile (used by the agent to personalize results)
USER_SKILLS="python,javascript,react,machine learning,data analysis"
USER_EXPERIENCE=3
USER_INDUSTRY_PREFERENCES="AI,Cloud,Fintech,Healthcare"

# Agent Configuration
AGENT_VERBOSITY=high  # Options: low, medium, high
AGENT_REFLECTION_ENABLED=true
``` 