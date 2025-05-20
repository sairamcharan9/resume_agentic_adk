from google.adk.agents import Agent, LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import agent_tool, google_search
from google.genai import types
from .instructions import (
    MANAGER_INSTRUCTIONS, 
    GREET_INSTRUCTIONS,
    JOB_ANALYZER_INSTRUCTIONS, 
    ATS_ANALYZER_INSTRUCTIONS,
    RESUME_OPTIMIZER_INSTRUCTIONS,
    OPTIMIZATION_LOOP_INSTRUCTIONS,
    QUANTIFICATION_ANALYSIS_INSTRUCTIONS,
    TONE_CLARITY_ANALYSIS_INSTRUCTIONS
)
from resumeoptimizer import instructions

# Use standard model name as string
# ADK 0.5.0 doesn't support GeminiModel class, so we use string model identifier
GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"  # Model name as string

# Create the greeting agent with no tools
greet_agent = LlmAgent(
    name="greet_agent",
    model=GEMINI_MODEL,
    description="Provides friendly greetings and welcomes users to the Resume Optimizer.",
    instruction=GREET_INSTRUCTIONS
)


# Create the job analyzer agent with Google search
job_analyzer_agent = LlmAgent(
    name="job_analyzer_agent",
    model=GEMINI_MODEL,
    description="Analyzes job descriptions and researches latest industry and ATS trends.",
    instruction=JOB_ANALYZER_INSTRUCTIONS,
    tools=[google_search]
)

# Create the resume analyzer agent
ATS_analyzer_agent = LlmAgent(
    name="ATS_analyzer_agent",
    model=GEMINI_MODEL,
    description="Analyzes resume content against job requirements to identify improvement opportunities.",
    instruction= ATS_ANALYZER_INSTRUCTIONS,
)

# Create the resume optimizer agent
resume_optimizer_agent = LlmAgent(
    name="resume_optimizer_agent",
    model=GEMINI_MODEL,
    description="Enhances specific resume bullet points while preserving structure.",
    instruction=RESUME_OPTIMIZER_INSTRUCTIONS
)

# Create the quantification analysis agent
quantification_analysis_agent = LlmAgent(
    name="quantification_analysis_agent",
    model=GEMINI_MODEL,
    description="Analyzes resume content for opportunities to add metrics and quantifiable achievements.",
    instruction=QUANTIFICATION_ANALYSIS_INSTRUCTIONS
)

# Create the tone and clarity analysis agent
tone_clarity_analysis_agent = LlmAgent(
    name="tone_clarity_analysis_agent",
    model=GEMINI_MODEL,
    description="Analyzes and improves the tone, clarity, and readability of resume content.",
    instruction=TONE_CLARITY_ANALYSIS_INSTRUCTIONS
)

# Wrap the agents as tools for the root agent
greet_agent_tool = agent_tool.AgentTool(agent=greet_agent)
job_analyzer_tool = agent_tool.AgentTool(agent=job_analyzer_agent)
ATS_analyzer_tool = agent_tool.AgentTool(agent=ATS_analyzer_agent)
resume_optimizer_tool = agent_tool.AgentTool(agent=resume_optimizer_agent)
quantification_analysis_tool = agent_tool.AgentTool(agent=quantification_analysis_agent)
tone_clarity_analysis_tool = agent_tool.AgentTool(agent=tone_clarity_analysis_agent)



# Create a loop agent that runs all analysis and optimization agents in sequence
optimization_loop_agent = LoopAgent(
    name="optimization_loop_agent",
    max_iterations=3,  # Set a reasonable max iterations to prevent infinite loops
    sub_agents=[
        ATS_analyzer_agent, 
        quantification_analysis_agent,
        tone_clarity_analysis_agent,
        resume_optimizer_agent
    ],
    description="Repeatedly runs analysis and optimization agents to iteratively improve the resume."
)

# Wrap the loop agent as a tool
optimization_loop_tool = agent_tool.AgentTool(agent=optimization_loop_agent)

# Create the root agent with all agent tools
root_agent = Agent(
    name="resume_optimizer",
    model=GEMINI_MODEL,  # Use string model identifier
    description="Resume Optimizer that uses AI to analyze resumes and suggest improvements to better match job descriptions while preserving structure.",
    instruction=MANAGER_INSTRUCTIONS,
    tools=[
        # Resume optimizer core tools
        greet_agent_tool,
        job_analyzer_tool,
        ATS_analyzer_tool,
        resume_optimizer_tool,
        quantification_analysis_tool,
        tone_clarity_analysis_tool,
        # Loop agent that iteratively improves the resume
        optimization_loop_tool,
    ]
)
