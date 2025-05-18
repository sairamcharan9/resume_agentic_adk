# Resume Optimizer (RO)

A specialized application for optimizing resumes for Computer Science, Data Science, and AI/ML positions based on job descriptions and special instructions. Features multiple AI model providers and flexible configuration options.

## Overview

The Resume Optimizer (RO) takes three inputs:
1. Job description
2. Current resume (LaTeX format)
3. Special instructions (optional)

It then analyzes and optimizes the resume to better match the job requirements while maintaining factual accuracy, and outputs an optimized resume in LaTeX format.

## MVP Approach

The project follows a Minimum Viable Product (MVP) approach with these priorities:
1. Basic LaTeX resume parsing for structured data extraction
2. ✅ Job description keyword analysis for CS/DS/AI-ML domains
3. ✅ AI-powered content optimization with LangChain integration
4. LaTeX generation of optimized resume
5. ✅ ATS compatibility analysis and recommendations
6. Simple feedback collection and processing

**Current Status**: Core backend functionality including job analysis and AI-powered optimization is implemented. Frontend interface and LaTeX parsing/generation in progress.

## Features

- **LaTeX Resume Parsing**: Parse LaTeX resume files to extract structured data
- **Job Description Analysis**: Extract key skills, requirements, and qualifications
- **ATS (Applicant Tracking System) Optimization**: Format resume to maximize ATS compatibility 
- **AI-Powered Content Optimization**: Tailor resume content to match job requirements
- **Domain-Specific Optimization**: Specialized for Computer Science, Data Science, and AI/ML fields
- **Feedback Loop**: Continuously improve optimization quality based on user feedback
- **LaTeX Template Generation**: Output professionally formatted LaTeX files
- **Flexible AI Model Selection**: Choose from multiple AI providers including OpenAI, OpenRouter, Hugging Face, and local models
- **Custom API Key Configuration**: Input your own API keys directly through the user interface

## AI Model Integration

The Resume Optimizer supports multiple AI model providers to give you flexibility in choosing the right model for your needs:

### Supported Providers

1. **OpenAI**
   - GPT-3.5 Turbo
   - GPT-4
   - GPT-4 Turbo

2. **OpenRouter**
   - Claude models (Anthropic)
   - Google Gemini 2.0 Flash Experimental (Free option)
   - LLaMA models (Meta)
   - Mistral models
   - And many other models accessible through OpenRouter

3. **Hugging Face**
   - Various open-source models hosted on Hugging Face

4. **Local Models**
   - Support for running models locally using Ollama

### Using Custom API Keys

You can provide your own API keys directly through the frontend interface:

1. Select your preferred model provider from the dropdown menu
2. Enter your API key in the designated field (required for OpenAI and OpenRouter)
3. Choose a specific model from the available options
4. The application will use your provided configuration for all optimization requests

This feature allows you to:
- Use your own API credits
- Access premium models like GPT-4
- Maintain control over which models process your data

## Project Structure

```
resume-optimizer/
├── src/
│   ├── parser/         # LaTeX resume parsing modules
│   ├── optimizer/      # Content optimization modules
│   ├── latex_generator/# LaTeX document generation
│   ├── ats/            # ATS compatibility modules
│   ├── feedback/       # Feedback collection and processing
│   └── utils/          # Utility functions
├── docs/               # Documentation
├── tests/              # Test cases
├── scrum/              # Scrum artifacts (sprint plans, task breakdowns)
│   ├── sprint_planning.md       # Sprint goals and user stories
│   ├── task_breakdown.md        # Detailed task assignments
│   ├── communication_log.md     # Daily work coordination
│   ├── thought_process_journal.md  # Design decisions
│   ├── component_boundaries.md  # Interface definitions
│   ├── blocker_log.md           # Issue tracking
│   ├── developer1_session_guide.md  # Dev 1 workflow guide
│   └── developer2_session_guide.md  # Dev 2 workflow guide
├── templates/          # LaTeX resume templates
├── main.py             # Main application entry point
└── requirements.txt    # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- LaTeX installed on your system
- API Key from one of the supported providers (optional, can be provided through the UI):
  - OpenAI API Key
  - OpenRouter API Key
  - Hugging Face API Token (for some models)
  - Local Ollama installation (for local models)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-optimizer.git
cd resume-optimizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

Note: You can also provide these API keys directly through the web interface.

### Usage

1. (Optional) Set up your API keys in the `.env` file as shown in the installation steps, or prepare to enter them in the web interface.

2. Run the FastAPI server:
```bash
python -m uvicorn main:app --reload
```

3. Navigate to http://127.0.0.1:8000 in your browser to access the web interface.

4. In the web interface, select your preferred AI model provider and configure it:
   - Choose a provider (OpenAI, OpenRouter, Hugging Face, Local)
   - Enter your API key if required
   - Select a specific model from the available options
   - Google Gemini 2.0 Flash is available as a free option through OpenRouter

5. Proceed with resume optimization using your configured model.

### Web Interface

The web interface allows you to:

- Select your preferred AI model provider and specific model
- Configure API keys directly through the UI
- Access free model options like Google Gemini 2.0 Flash Experimental
- Upload a LaTeX resume file (.tex)
- Enter job description details including title and requirements
- Add special instructions for optimization
- Submit for processing
- View and download the optimized resume

### API Endpoints

The application exposes the following API endpoints:

- `GET /` - Web interface home page
- `POST /api/optimize` - Optimize a resume based on job description
- `GET /api/download/{resume_id}` - Download an optimized resume
- `POST /api/feedback` - Submit feedback on optimization
- `GET /api/templates` - List available resume templates

## Development

### Testing and CI/CD

The project uses pytest for unit testing with code coverage tracking:

```bash
# Run tests with coverage report
python -m pytest tests/ -v --cov=src --cov-report=term --cov-report=html
```

#### GitHub Actions

The project is set up with GitHub Actions workflow to automatically run tests on code pushes and pull requests:

- Automatically runs on pushes to main and dev-* branches
- Runs on multiple Python versions (3.8, 3.9)
- Generates code coverage reports
- Uploads test artifacts for easy review

The workflow configuration is in `.github/workflows/run-tests.yml`.

### Collaboration Framework

This project is designed for collaborative development with two developers using Windsurf. We follow Agile/Scrum methodology with:

- Two-week sprints with clearly defined MVP tasks
- Component-based ownership to minimize merge conflicts
- Daily communication through structured logs
- Detailed component boundaries for clear interfaces
- Continuous integration via GitHub Actions

### Component Ownership

**Developer 1 Responsibilities:**
- Frontend interface and API endpoints
- LaTeX Resume Parser
- LaTeX Generator
- Feedback Collection and Processing
- Frontend-Backend Integration

**Developer 2 Responsibilities:**
- ✅ Job Description Analyzer
- ✅ Resume Optimization Algorithms
- ✅ ATS Analyzer and Scoring
- ✅ Core Optimization Engine
- ✅ AI Integration for Content Enhancement
- Performance Optimization

**Shared Responsibilities:**
- Architecture decisions
- Integration testing
- Documentation

**Implementation Notes**:
- Developer 2 has completed the job analyzer, keyword extraction, and AI integration components
- These components use LangChain, TF-IDF, and spaCy for advanced NLP capabilities
- All components include comprehensive unit tests

### Session Workflow

Each development session follows a structured workflow:
1. Update communication log with planned work
2. Review component boundaries before modifications
3. Document design decisions in thought process journal
4. Report blockers immediately
5. Update task status in sprint planning

See the `scrum/developer1_session_guide.md` and `scrum/developer2_session_guide.md` for detailed workflow instructions.

## Security Considerations

### API Key Management

This application offers two methods for providing API keys:

1. **Environment Variables**: Store API keys in a `.env` file (recommended for development)
2. **Web Interface**: Enter API keys directly in the UI (convenient for quick testing)

Best practices for API key security:

- **DO NOT** commit your `.env` file or any file containing API keys to version control
- The application does not store API keys entered through the UI in a persistent database
- Consider using environment variables for production deployments
- Regularly rotate your API keys following the provider's recommendations

## Troubleshooting

### Common Issues with AI Models

**Issue**: Model provider returns an error
**Solution**: 
- Verify your API key is correct and has sufficient credits/quota
- Check that the selected model is available through your subscription tier
- For OpenRouter, ensure the specific model you've selected is accessible

**Issue**: Free Gemini model not working
**Solution**:
- The Google Gemini 2.0 Flash Experimental model is provided through OpenRouter
- This model may have usage limitations or could become unavailable
- Try selecting a different model if you encounter issues

**Issue**: Local models not appearing
**Solution**:
- Ensure Ollama is properly installed and running on your system
- Check that your selected model has been downloaded to your Ollama instance
- Verify network connectivity between the application and Ollama

**Issue**: Slow response times
**Solution**:
- Larger models (like GPT-4) typically have longer response times
- Consider using a smaller or faster model for quicker results
- Check your network connection and provider status

## License

This project is licensed under the MIT License - see the LICENSE file for details.
