# Resume Optimizer (RO)

A specialized application for optimizing resumes for Computer Science, Data Science, and AI/ML positions based on job descriptions and special instructions.

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
- OpenAI API Key (for AI content optimization)

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

4. Create a `.env` file with your API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Usage

1. Set up your OpenAI API key in the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

2. Run the FastAPI server:
```bash
python -m uvicorn main:app --reload
```

3. Navigate to http://127.0.0.1:8000 in your browser to access the web interface.

### Web Interface

The web interface allows you to:
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

### Collaboration Framework

This project is designed for collaborative development with two developers using Windsurf. We follow Agile/Scrum methodology with:

- Two-week sprints with clearly defined MVP tasks
- Component-based ownership to minimize merge conflicts
- Daily communication through structured logs
- Detailed component boundaries for clear interfaces

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
