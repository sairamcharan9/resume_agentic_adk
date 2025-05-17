# Component Boundaries Document

This document defines the boundaries and interfaces between different components of the Resume Optimizer application. It serves as a reference for developers to ensure modular development without breaking integrations.

## Component Overview

```
Resume Optimizer
├── Parser Component
│   └── LaTeX Resume Parser
├── Analyzer Component
│   └── Job Description Analyzer
├── Optimizer Component
│   └── Resume Content Optimizer
├── Generator Component
│   └── LaTeX Generator
├── ATS Component
│   └── ATS Analyzer
├── Feedback Component
│   └── Feedback Processor
└── UI Component
    └── Web Interface
```

## Interface Definitions

### Parser Component Interface

**Owner:** Developer 1

**Input:**
- LaTeX resume file content (string)

**Output:**
```python
{
  "contact_info": {
    "name": str,
    "email": str,
    "phone": str,
    "linkedin": str,
    "github": str
  },
  "education": List[Dict],
  "experience": List[Dict[str, str]],  # Each dict contains role, company, duration, description
  "projects": List[Dict[str, str]],    # Each dict contains title, technologies, description, achievements
  "skills": Dict[str, List[str]],      # Category -> list of skills
  "publications": List[Dict],
  "awards": List[Dict],
  "template": str                      # Detected LaTeX template
}
```

**API Usage Example:**
```python
from src.parser.latex_parser import LaTeXResumeParser

parser = LaTeXResumeParser()
parsed_resume = await parser.parse("/path/to/resume.tex")
```

### Analyzer Component Interface

**Owner:** Developer 2

**Input:**
- Job title (string)
- Job description (string)
- Requirements (List[string])
- Domain (string, enum: "computer_science", "data_science", "ai_ml")

**Output:**
```python
{
  "title": str,                       # Standardized job title
  "requirements": List[str],          # Key job requirements
  "skills": List[str],                # Required skills
  "technologies": List[str],          # Required technologies/tools
  "keywords": List[str],              # Important keywords
  "experience_level": str,            # Junior, mid, senior, etc.
  "domain_focus": str                 # Specific focus area
}
```

**API Usage Example:**
```python
from src.utils.job_analyzer import JobDescriptionAnalyzer

analyzer = JobDescriptionAnalyzer()
job_analysis = await analyzer.analyze(
    "Software Engineer", 
    "Full job description text...", 
    ["Requirement 1", "Requirement 2"], 
    domain="computer_science"
)
```

### Optimizer Component Interface

**Owner:** Developer 2

**Input:**
- Parsed resume (Dict from Parser Component)
- Job analysis (Dict from Analyzer Component)
- Special instructions (Optional[Dict])

**Output:**
```python
{
  "contact_info": Dict,               # Same as input
  "education": List[Dict],            # Same as input
  "experience": List[Dict],           # Optimized experience items
  "projects": List[Dict],             # Optimized project items
  "skills": Dict[str, List[str]],     # Optimized skills
  "publications": List[Dict],         # Same as input
  "awards": List[Dict],               # Same as input
  "summary": str,                     # Optimization summary
  "improvements": List[str],          # Key improvements made
  "keywords_matched": List[str],      # Keywords matched from job
  "ats_recommendations": List[str]    # ATS recommendations
}
```

**API Usage Example:**
```python
from src.optimizer.resume_optimizer import ResumeOptimizer

optimizer = ResumeOptimizer()
optimized_data = await optimizer.optimize(
    parsed_resume,
    job_analysis,
    special_instructions
)
```

### Generator Component Interface

**Owner:** Developer 1

**Input:**
- Optimized resume data (Dict from Optimizer Component)
- Output path (Path)
- Template name (Optional[str])
- Domain (string)

**Output:**
- Path to generated LaTeX file (Path)

**API Usage Example:**
```python
from src.latex_generator.generator import LaTeXGenerator

generator = LaTeXGenerator()
output_path = await generator.generate(
    optimized_data,
    Path("/path/to/output.tex"),
    template_name="modern",
    domain="computer_science"
)
```

### ATS Component Interface

**Owner:** Developer 2

**Input:**
- Resume file path (Path)
- Job description (JobDescription object)
- Domain (string)

**Output:**
```python
{
  "ats_score": float,                 # Overall ATS compatibility (0-100)
  "keyword_match_score": float,       # Keyword match score (0-100)
  "matched_keywords": List[str],      # Keywords matched in resume
  "missing_keywords": List[str],      # Keywords not found in resume
  "keyword_density": float,           # Keyword density metric
  "ats_issues": List[str],            # Identified ATS issues
  "recommendations": List[str]        # Recommendations for improvement
}
```

**API Usage Example:**
```python
from src.ats.ats_analyzer import ATSAnalyzer

analyzer = ATSAnalyzer()
ats_results = await analyzer.analyze(
    Path("/path/to/resume.tex"),
    job_description,
    domain="computer_science"
)
```

### Feedback Component Interface

**Owner:** Developer 1

**Input:**
- Feedback data (Dict with ratings, comments, etc.)

**Output:**
```python
{
  "status": str,                      # "success" or "error"
  "message": str,                     # Confirmation or error message
  "feedback_id": str                  # ID for the submitted feedback
}
```

**API Usage Example:**
```python
from src.feedback.feedback_processor import FeedbackProcessor

processor = FeedbackProcessor()
result = await processor.process_feedback({
    "resume_id": "ro_12345",
    "effectiveness_rating": 4,
    "quality_rating": 5,
    "comments": "Very helpful optimization!",
    "interview_result": "invited"
})
```

## UI Component Interface

**Owner:** Developer 1

**Responsibility:**
- Web interface implementation
- Form handling and validation
- User experience design
- Frontend styling and responsiveness

## REST API Endpoints

### POST /api/optimize
- **Owner:** Shared (Developer 1 implements, Developer 2 assists with integration)
- **Description:** Main endpoint to optimize a resume
- **Consumes:** multipart/form-data
- **Parameters:**
  - job_description (JSON string)
  - resume_file (file)
  - special_instructions (optional JSON string)
- **Produces:** application/json

### GET /api/download/{resume_id}
- **Owner:** Developer 1
- **Description:** Download optimized resume file
- **Parameters:**
  - resume_id (path)
- **Produces:** application/x-tex

### POST /api/feedback
- **Owner:** Developer 1
- **Description:** Submit feedback on optimization
- **Consumes:** application/json
- **Produces:** application/json

### GET /api/templates
- **Owner:** Developer 1
- **Description:** List available resume templates
- **Produces:** application/json

## Data Flow Diagram

```
┌────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐
│  LaTeX     │     │   Job       │     │  Resume     │     │ LaTeX     │
│  Parser    │────▶│  Analyzer   │────▶│  Optimizer  │────▶│ Generator │
└────────────┘     └─────────────┘     └─────────────┘     └───────────┘
      ▲                                       │                  │
      │                                       │                  │
      │                                       ▼                  ▼
┌────────────┐                         ┌─────────────┐    ┌───────────┐
│ Web        │◀────────────────────────│    ATS      │    │  Output   │
│ Interface  │                         │  Analyzer   │    │   File    │
└────────────┘                         └─────────────┘    └───────────┘
      │                                       ▲
      │                                       │
      ▼                                       │
┌────────────┐                         ┌─────────────┐
│  Feedback  │────────────────────────▶│  Feedback   │
│   Form     │                         │ Processor   │
└────────────┘                         └─────────────┘
```
