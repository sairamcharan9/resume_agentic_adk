from google.adk.agents import Agent, LlmAgent, SequentialAgent
from google.adk.tools import agent_tool, google_search

from .instructions import (
    MANAGER_INSTRUCTIONS, 
    GREET_INSTRUCTIONS, 
    LATEX_INSTRUCTIONS, 
    JOB_ANALYZER_INSTRUCTIONS, 
    RESUME_ANALYZER_INSTRUCTIONS,
    RESUME_OPTIMIZER_INSTRUCTIONS,
    SIMPLE_INSTRUCTIONS
)

# Use standard model name as string
# ADK 0.5.0 doesn't support GeminiModel class, so we use string model identifier
GEMINI_MODEL = "gemini-1.5-flash"  # Model name as string

# Create the greeting agent with no tools
greet_agent = LlmAgent(
    name="greet_agent",
    model=GEMINI_MODEL,
    description="Provides friendly greetings and welcomes users to the Resume Optimizer.",
    instruction=GREET_INSTRUCTIONS
)

# Create the LaTeX processing agent
latex_agent = LlmAgent(
    name="latex_agent",
    model=GEMINI_MODEL,
    description="Specialized agent for processing LaTeX resumes and extracting structured information.",
    instruction=LATEX_INSTRUCTIONS
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
resume_analyzer_agent = LlmAgent(
    name="resume_analyzer_agent",
    model=GEMINI_MODEL,
    description="Analyzes resume content against job requirements to identify improvement opportunities.",
    instruction=RESUME_ANALYZER_INSTRUCTIONS
)

# Create the resume optimizer agent
resume_optimizer_agent = LlmAgent(
    name="resume_optimizer_agent",
    model=GEMINI_MODEL,
    description="Enhances specific resume bullet points while preserving structure.",
    instruction=RESUME_OPTIMIZER_INSTRUCTIONS
)

# Wrap the agents as tools for the root agent
greet_agent_tool = agent_tool.AgentTool(agent=greet_agent)
latex_agent_tool = agent_tool.AgentTool(agent=latex_agent)
job_analyzer_tool = agent_tool.AgentTool(agent=job_analyzer_agent)
resume_analyzer_tool = agent_tool.AgentTool(agent=resume_analyzer_agent)
resume_optimizer_tool = agent_tool.AgentTool(agent=resume_optimizer_agent)



# Create an optimization workflow using SequentialAgent
optimization_workflow = SequentialAgent(
    name="optimization_workflow",
    sub_agents=[
        # First analyze the job description
        LlmAgent(
            name="job_requirement_analyzer",
            model=GEMINI_MODEL,
            instruction="Analyze the job description and extract key requirements. Save insights to 'job_requirements'.",
            tools=[job_analyzer_tool],
            output_key="job_requirements"  # Save output to session state for next agent
        ),
        
        # Then analyze the resume against job requirements
        LlmAgent(
            name="resume_analyzer",
            model=GEMINI_MODEL,
            instruction="Using the job requirements in 'job_requirements', analyze the resume and identify specific bullet points to improve. Preserve structure completely. Save analysis to 'resume_analysis'.",
            tools=[resume_analyzer_tool],
            output_key="resume_analysis"  # Save output to session state for next agent
        ),
        
        # Finally optimize the resume while preserving structure
        LlmAgent(
            name="resume_enhancer",
            model=GEMINI_MODEL,
            instruction="Using the analysis in 'resume_analysis' and job requirements in 'job_requirements', enhance the specific bullet points identified. NEVER change resume structure or number of bullets. Save optimized content to 'optimized_resume'.",
            tools=[resume_optimizer_tool],
            output_key="optimized_resume"  # Final output with optimized content
        )
    ]
)

# Create the root agent with all agent tools
root_agent = Agent(
    name="resume_optimizer",
    model=GEMINI_MODEL,  # Use string model identifier
    description="Resume Optimizer that uses AI to analyze resumes and suggest improvements to better match job descriptions while preserving structure.",
    instruction=MANAGER_INSTRUCTIONS,
    tools=[
        # Resume optimizer core tools
        greet_agent_tool,
        latex_agent_tool,
        job_analyzer_tool,
        resume_analyzer_tool,
        resume_optimizer_tool,
        agent_tool.AgentTool(agent=optimization_workflow),
    ]
)

# ---------- Session and Runner Setup ----------

# Import necessary components for session and runner
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import google.generativeai.types as types

# Constants for session management
APP_NAME = "resume_optimizer"  # Application name for session management
USER_ID = "default_user"  # Default user ID
SESSION_ID = "default_session"  # Default session ID

# Create session service and session
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

# Initialize the runner with our root agent
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# Helper function to interact with the agent
def call_agent(query):
    """
    Helper function to call the agent with a query.
    
    Args:
        query: The text query to send to the agent
        
    Returns:
        The agent's final response
    """
    # Create content object with the query
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # Run the agent with the query
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    # Process events and extract the final response
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
            return final_response
    
    return "No response from the agent."