# Resume Optimizer

A powerful AI-driven tool that analyzes LaTeX resumes and provides tailored optimization suggestions to help match job descriptions and increase interview chances.

## Features

- **LaTeX Resume Scanning**: Automatically finds and processes LaTeX resumes in directories
- **Experience Extraction**: Identifies work experience details including positions, companies, dates, and bullet points
- **Tailored Optimization**: Provides targeted suggestions to improve resume content based on job descriptions
- **Content Enhancement**: Helps add quantifiable achievements, emphasize leadership, and highlight transferable skills

## Prerequisites

- Python 3.9+ installed
- Google API key for Gemini model access
- Google ADK (Agent Development Kit) installed

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/resume-optimizer.git
   cd resume-optimizer
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

### Running the Application

1. Start the web server:
   ```
   python main.py
   ```
   This will launch the application on http://localhost:5001 by default

2. Open your web browser and navigate to http://localhost:5001

3. Follow the on-screen instructions to optimize your resume

### Workflow

1. **Greeting**: The agent welcomes you and explains the service
2. **Finding Resume Files**: The agent can scan directories for LaTeX resume files
3. **Extracting Experience**: Work experience sections are parsed and structured
4. **Analyzing Experience**: Each position is evaluated for relevance to target job roles
5. **Optimization Suggestions**: Detailed recommendations are provided to improve content

## Project Structure

```
resume-optimizer/
├── main.py                    # Main application entry point
├── requirements.txt           # Project dependencies
├── .env                      # Environment variables (you need to create this)
├── resumeoptimizer/
│   ├── agent.py              # Definition of the resume optimization agent
│   ├── tools.py              # Tool functions for resume analysis
│   └── insturctions.py       # Agent instructions and prompt templates
├── tests/                    # Test files
└── README.md                 # This documentation
```

## Using Your Own LaTeX Resume

1. Place your LaTeX resume (`.tex` file) in the project directory or a subdirectory
2. Run the application and instruct the agent to find your resume
3. The agent will automatically extract experience information and provide optimization suggestions

## Example Commands

- "Find my resume in the current directory"
- "Optimize my resume for a data science position"
- "Extract the experience from my resume"
- "Suggest improvements for my work experience bullet points"

## Troubleshooting

- **API Key Issues**: Ensure your Google API key is correctly set in the `.env` file
- **LaTeX Parsing Errors**: Validate that your LaTeX resume follows standard formatting
- **Port Conflicts**: If port 5001 is already in use, modify the port in `main.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google ADK for providing the agent framework
- LaTeX community for standardized resume templates
