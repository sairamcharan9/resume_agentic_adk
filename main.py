import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Import our agent components
from resumeoptimizer.agent import call_agent, session, runner, USER_ID, SESSION_ID
from resumeoptimizer.instructions import SIMPLE_INSTRUCTIONS

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

def interactive_session():
    """Run an interactive console session with the Resume Optimizer agent"""
    print("\nWelcome to the Resume Optimizer interactive console!")
    print("Type 'exit' to quit")
    
    # Interactive loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
            
        # Process the message through our call_agent function
        response = call_agent(user_input)

# Main entry point
if __name__ == "__main__":
    print("Resume Optimizer initialized with sequential workflow:")
    print("1. Greeting and welcome")
    print("2. Resume processing")
    print("3. Job analysis")
    print("4. Match scoring and optimization")
    print("\nOptions:")
    print("1. Run 'python -m google.adk.cli web' to start the web interface")
    print("2. Run this script directly to use the interactive console")
    
    # Check if user wants to run in interactive mode
    user_choice = input("Would you like to start the interactive console? (y/n): ")
    if user_choice.lower().startswith('y'):
        interactive_session()
    else:
        print("\nTo use the web interface, run 'python -m google.adk.cli web'")
        print("Then visit http://localhost:8000 to interact with the agent.")

