from google.adk.agents import Agent, LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools import agent_tool, google_search
from google.adk.tools.tool_context import ToolContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService  # For development
# from google.adk.artifacts import GcsArtifactService  # For production with Google Cloud Storage
from google.genai import types
import os
import time
import mimetypes
import re
import tempfile
import base64
import json

# Import our file processing utilities
from .instructions import (
    MANAGER_INSTRUCTIONS, 
    GREET_INSTRUCTIONS,
    JOB_ANALYZER_INSTRUCTIONS, 
    ATS_ANALYZER_INSTRUCTIONS,
    RESUME_OPTIMIZER_INSTRUCTIONS,
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

# Define artifact handling functions
async def save_resume(tool_context: ToolContext, resume_content: str, filename: str = "resume.txt") -> str:
    """Tool to save a resume as an artifact."""
    try:
        # Save with user: prefix to make it available across sessions
        artifact_filename = f"user:{filename}"
        # Create a Part object with the text content
        text_part = types.Part(text=resume_content)
        await tool_context.save_artifact(artifact_filename, text_part)
        return f"Resume saved successfully as '{filename}'."
    except Exception as e:
        print(f"Error saving resume: {e}")
        return f"Error: Could not save resume. {str(e)}"

async def save_optimized_resume(tool_context: ToolContext, optimized_content: str, 
                           original_filename: str = "resume.txt") -> str:
    """Tool to save an optimized version of a resume."""
    try:
        # Generate a filename for the optimized version
        name_parts = original_filename.rsplit('.', 1)
        base_name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else "txt"
        optimized_filename = f"user:{base_name}_optimized.{extension}"
        
        # Create a Part object with the text content
        text_part = types.Part(text=optimized_content)
        await tool_context.save_artifact(optimized_filename, text_part)
        return f"Optimized resume saved as '{base_name}_optimized.{extension}'."
    except Exception as e:
        print(f"Error saving optimized resume: {e}")
        return f"Error: Could not save optimized resume. {str(e)}"

async def list_user_files(tool_context: ToolContext) -> str:
    """Tool to list available artifacts for the user."""
    try:
        available_files = await tool_context.list_artifacts()
        if not available_files:
            return "You have no saved artifacts."
        else:
            # Format the list for the user/LLM
            file_list_str = "\n".join([f"- {fname}" for fname in available_files])
            return f"Here are your available artifacts:\n{file_list_str}"
    except Exception as e:
        print(f"Error listing artifacts: {e}")
        return f"Error: Could not list artifacts. {str(e)}"

async def load_resume(tool_context: ToolContext, filename: str) -> str:
    """Tool to load a resume artifact."""
    try:
        # Handle user: prefix automatically
        if not filename.startswith("user:"):
            full_filename = f"user:{filename}"
        else:
            full_filename = filename
            
        resume_artifact = await tool_context.load_artifact(full_filename)
        if resume_artifact:
            # Get the text content from the Part object
            if hasattr(resume_artifact, 'text') and resume_artifact.text:
                return resume_artifact.text
            else:
                return f"Error: Resume artifact does not contain text data."
        else:
            return f"Error: Could not find resume with filename '{filename}'."
    except Exception as e:
        print(f"Error loading resume: {e}")
        return f"Error: Could not load resume. {str(e)}"


# Create artifact service instance
artifact_service = InMemoryArtifactService()  # Simple in-memory implementation for development

# Direct text processing for the ADK web interface

async def process_resume(tool_context: ToolContext, resume_content: str) -> str:
    """
    Process resume content provided directly as text.
    
    Args:
        tool_context: The tool context.
        resume_content: The text content of the resume.
    
    Returns:
        A confirmation message.
    """
    try:
        # Generate unique ID
        timestamp = int(time.time())
        resume_id = f"resume_{timestamp}"
        file_name = f"{resume_id}.txt"
        
        # Save as plain text
        await tool_context.save_artifact(
            "resume:" + resume_id,
            types.Part(text=resume_content)
        )
        
        # Check if it's LaTeX
        if resume_content.startswith('\\documentclass'):
            return await process_latex_resume(tool_context, resume_content, file_name)
        
        # Regular text resume
        return f"Thank you for providing your resume. I've saved it ({len(resume_content)} characters). Would you like me to optimize it for a job description?"
    except Exception as e:
        return f"Error processing resume: {str(e)}"

async def process_job_description(tool_context: ToolContext, job_description: str) -> str:
    """
    Process a job description provided directly as text.
    
    Args:
        tool_context: The tool context.
        job_description: The text content of the job description.
    
    Returns:
        A confirmation message.
    """
    try:
        # Generate unique ID
        job_id = f"job_{int(time.time())}"
        
        # Save as plain text
        await tool_context.save_artifact(
            "job:" + job_id,
            types.Part(text=job_description)
        )
        
        return f"Thank you for providing the job description. I've saved it ({len(job_description)} characters). Do you want me to use this to optimize your resume?"
    except Exception as e:
        return f"Error processing job description: {str(e)}"

# Add a specialized tool for handling LaTeX resumes
async def process_latex_resume(tool_context: ToolContext, resume_content: str, filename: str = "resume.tex") -> str:
    """
    Process a LaTeX resume, extracting its structure and content for optimization.
    
    Args:
        tool_context: The tool context.
        resume_content: The LaTeX resume content.
        filename: Name to save the resume file as.
    
    Returns:
        Analysis of the LaTeX resume structure.
    """
    try:
        # Save the original LaTeX content
        artifact_filename = f"user:{filename}"
        latex_part = types.Part(text=resume_content)
        await tool_context.save_artifact(artifact_filename, latex_part)
        
        # Extract clean text from LaTeX
        from .file_utils import extract_text_from_latex
        extracted_text = extract_text_from_latex(resume_content)
        
        # Save the extracted text as a separate artifact
        extracted_filename = f"user:{os.path.splitext(filename)[0]}_extracted.txt"
        text_part = types.Part(text=extracted_text)
        await tool_context.save_artifact(extracted_filename, text_part)
        
        # Analyze LaTeX structure
        section_count = resume_content.count('\\section')
        subsection_count = resume_content.count('\\subsection')
        itemize_count = resume_content.count('\\begin{itemize}')
        enumerate_count = resume_content.count('\\begin{enumerate}')
        
        return f"""
        Successfully processed LaTeX resume: {filename}
        
        LaTeX Structure Analysis:
        - {section_count} main sections
        - {subsection_count} subsections
        - {itemize_count} bullet point lists
        - {enumerate_count} numbered lists
        
        The original LaTeX content has been saved, and the extracted plain text is available as '{os.path.splitext(filename)[0]}_extracted.txt'.
        
        This resume can now be optimized while preserving its LaTeX structure.
        """
    except Exception as e:
        print(f"Error processing LaTeX resume: {e}")
        return f"Error: Could not process LaTeX resume. {str(e)}"

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
        # Artifact tools
        save_resume,
        save_optimized_resume,
        list_user_files,
        load_resume,
        # File handling tools
        process_resume,
        process_job_description,
        process_latex_resume,
    ]
)

# Create a runner with session and artifact services
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="resume_optimizer_app",
    session_service=session_service,
    artifact_service=artifact_service  # Add the artifact service here
)
