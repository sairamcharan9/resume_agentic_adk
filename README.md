# Resume Optimizer

A powerful AI-driven tool that analyzes LaTeX resumes and provides tailored optimization suggestions to help match job descriptions and increase interview chances.

## Features

- **LaTeX Resume Scanning**: Automatically finds and processes LaTeX resumes in directories
- **Experience Extraction**: Identifies work experience details including positions, companies, dates, and bullet points
- **Tailored Optimization**: Provides targeted suggestions to improve resume content based on job descriptions
- **Content Enhancement**: Helps add quantifiable achievements, emphasize leadership, and highlight transferable skills

## Prerequisites

- Python 3.9+ installed
- Google API key for Gemini model access (get one at https://makersuite.google.com/)
- Google ADK (Agent Development Kit) installed

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sairamcharan9/resume_agentic_adk.git
   cd resume_agentic_adk
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install Google ADK and other dependencies:
   ```
   # Install Google ADK
   pip install -U google-adk
   
   # Install other project dependencies
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   
5. Initialize the ADK directory (if not already initialized):
   ```
   adk init
   ```

## Usage

### Running the Application

1. Start the ADK web interface:
   ```
   adk web
   ```
   This will launch the Google ADK web interface in your default browser

2. In the ADK web interface, select the Resume Optimizer project

3. Configure the agent with your API key and settings

4. Start a conversation with the Resume Optimizer agent

5. Follow the agent's instructions to optimize your resume

### Workflow

1. **Greeting**: The agent welcomes you and explains the service
2. **Finding Resume Files**: The agent can scan directories for LaTeX resume files
3. **Extracting Experience**: Work experience sections are parsed and structured
4. **Analyzing Experience**: Each position is evaluated for relevance to target job roles
5. **Optimization Suggestions**: Detailed recommendations are provided to improve content

## Project Structure

```
resume_agentic_adk/
├── main.py                    # Application entry point (alternative to ADK web)
├── main.tex                   # Example LaTeX resume template
├── job_description.txt       # Example job description for testing
├── requirements.txt           # Project dependencies
├── .env                      # Environment variables (create this yourself)
├── resumeoptimizer/           # Core package directory
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # ADK agent definition with tools
│   ├── tools.py              # Tool functions (LaTeX parsing & analysis)
│   └── instructions.py       # Agent instructions and prompt templates
├── .adk/                     # ADK configuration directory (created by ADK init)
└── README.md                 # This documentation
```

## Using Your Own LaTeX Resume

1. Place your LaTeX resume (`.tex` file) in the project directory or a subdirectory
2. Run the application and instruct the agent to find your resume
3. The agent will automatically extract experience information and provide optimization suggestions

## Example Conversations with the Agent

- "Hello, I'd like to optimize my resume for a machine learning engineer position"
- "Please analyze my LaTeX resume in the current directory"
- "Can you extract the experience sections from my resume?"
- "How can I improve my work experience descriptions to match this job description?"
- "What keywords should I add to my resume to pass ATS screening?"

## Troubleshooting

- **API Key Issues**: Ensure your Google API key is correctly set in the `.env` file
- **LaTeX Parsing Errors**: Validate that your LaTeX resume follows standard formatting
- **Port Conflicts**: If port 5001 is already in use, modify the port in `main.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google ADK for providing the agent framework
- LaTeX community for standardized resume templates
