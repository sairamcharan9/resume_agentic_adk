#!/usr/bin/env python
"""
Launch script for the Resume Optimizer using ADK's web interface and runner

This script provides two options:
1. Launch the ADK web interface using the CLI for interactive use
2. Programmatically interact with the agent using the runner directly
"""

import os
import sys
import importlib.util
import subprocess
import asyncio
from google.genai import types

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.append(project_path)

# Import the runner from the agent module
from resumeoptimizer.agent import runner, root_agent

# Constants for runner use
USER_ID = "user-1"
SESSION_ID = "session-1"

def run_adk_web_cli():
    """Run the ADK web interface using the CLI command."""
    print("Starting Resume Optimizer Web Interface via CLI...")
    print("Access the interface at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    # The directory that contains the agent
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Use subprocess to run the ADK CLI web command
    cmd = [
        "python", "-m", "google.adk.cli", "web",
        "--port", "8000",
        current_dir
    ]
    
    # Run the command
    subprocess.run(cmd)

async def process_input_async(query):
    """Process user input using the runner's async interface."""
    # Create a content object with user role and message
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # Run the agent with the content
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        # Check if this is the final response
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
            return final_response

def process_input(query):
    """Process user input using the runner's synchronous interface."""
    # Create a content object with user role and message
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # Process the content with the runner
    for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        # Check if this is the final response
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
            return final_response

def run_cli_demo():
    """Run a simple CLI demo of the resume optimizer using the runner directly."""
    print("Resume Optimizer CLI Demo")
    print("Type 'exit' to quit")
    
    while True:
        query = input("\nYour input: ")
        if query.lower() == 'exit':
            break
        
        print("\nProcessing...")
        response = process_input(query)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Resume Optimizer ADK Runner")
    parser.add_argument("--mode", choices=["web", "cli"], default="web", 
                      help="Run mode: 'web' for web interface, 'cli' for command line")
    
    args = parser.parse_args()
    
    if args.mode == "web":
        run_adk_web_cli()
    else:
        run_cli_demo()
