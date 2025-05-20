import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from resumeoptimizer.agent import root_agent

# Load environment variables from .env file
load_dotenv()

# Configure Google AI authentication
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    # Configure with safety settings for optimal model behavior
    genai.configure(
        api_key=api_key,
        transport='rest',  # Using REST API
        # Add safety settings to avoid filtering issues
        safety_settings={
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        }
    )
    print("Google AI API configured for Resume Optimizer.")
    
    # Test connection to verify the API key works
    try:
        # Simple test of the connection
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, world!")
        print("✅ API connection test successful.")
    except Exception as e:
        print(f"❌ API connection test failed: {str(e)}")
        print("Please check your API key and try again.")
        # Continue since the ADK might have its own authentication
        
else:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    print("Please create a .env file with your API key or set it as an environment variable.")
    sys.exit(1)

# This file makes the root_agent available to the ADK web interface
# The root_agent has been simplified to use just two tools:
# 1. greet_agent - Welcomes users to the service
# 2. resume_parser - Parses LaTeX resume content and provides optimization suggestions
if __name__ == "__main__":
    print("Resume Optimizer agent initialized with the following tools:")
    print("- greet_agent: Friendly welcome and introduction to the service")
    print("- resume_parser: Parses LaTeX resume content and suggests improvements")
    print("\nRun 'python -m google.adk.cli web' to start the web interface.")
    print("Then visit http://localhost:8000 to interact with the agent.")

