"""
Tests for the LaTeX Generator Component

These tests verify that the LaTeX generator can correctly convert
structured resume data into formatted LaTeX files.
"""

import os
import sys
import asyncio
import pytest
from pathlib import Path
import re

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.latex_generator.generator import LaTeXGenerator

# Sample optimized resume data for testing
SAMPLE_RESUME_DATA = {
    "contact_info": {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "(123) 456-7890",
        "linkedin": "johnsmith",
        "github": "johnsmith"
    },
    "education": [
        {
            "institution": "University of Computer Science",
            "degree": "Bachelor of Science in Computer Science",
            "date": "Sep 2018 - May 2022",
            "location": "City, State",
            "gpa": "GPA: 3.8/4.0"
        }
    ],
    "experience": [
        {
            "role": "Software Engineer",
            "company": "Tech Company Inc.",
            "duration": "June 2022 - Present",
            "location": "San Francisco, CA",
            "description": "Developed and maintained RESTful APIs using Python and Flask\nImproved system performance by 30% through database optimization\nCollaborated with cross-functional teams to implement new features"
        },
        {
            "role": "Software Engineering Intern",
            "company": "Startup Innovation Labs",
            "duration": "May 2021 - Aug 2021",
            "location": "New York, NY",
            "description": "Built a real-time dashboard using React and D3.js\nImplemented data processing pipeline using Apache Kafka\nParticipated in agile development process with daily standups"
        }
    ],
    "projects": [
        {
            "title": "Personal Website",
            "technologies": "HTML, CSS, JavaScript",
            "description": "Created a responsive personal portfolio website with projects and blog\nImplemented dark mode toggle using CSS variables and JavaScript",
            "achievements": "Featured in a web design showcase"
        },
        {
            "title": "Machine Learning Model",
            "technologies": "Python, TensorFlow, scikit-learn",
            "description": "Developed a classification model for image recognition with 92% accuracy\nOptimized using transfer learning and hyperparameter tuning",
            "achievements": "Won 2nd place in campus AI competition"
        }
    ],
    "skills": {
        "Languages": ["Python", "JavaScript", "Java", "C++", "SQL"],
        "Frameworks": ["React", "Flask", "Django", "Express.js"],
        "Tools": ["Git", "Docker", "AWS", "Jenkins"],
        "Other": ["RESTful API Design", "Agile Methodologies", "CI/CD"]
    },
    "publications": [
        {"content": "Smith, J. (2022). Advancements in Machine Learning Techniques. Journal of AI Research, 45(2), 187-205."}
    ],
    "awards": [
        {"content": "Dean's List, Merit Scholarship (2018-2022)"}
    ],
    "template": "moderncv"
}


@pytest.fixture
def generator():
    """Returns a LaTeX Generator instance"""
    return LaTeXGenerator()


@pytest.fixture
def ensure_templates_dir():
    """Ensures the template directory exists and has at least one template"""
    templates_dir = Path("templates/latex")
    templates_dir.mkdir(exist_ok=True, parents=True)
    
    # Create a basic template file if one doesn't exist
    default_path = templates_dir / "modern.tex"
    if not default_path.exists():
        with open(default_path, 'w', encoding='utf-8') as f:
            f.write(r"""\documentclass[11pt,a4paper,sans]{moderncv}
\moderncvstyle{classic}
\moderncvcolor{blue}
\usepackage[utf8]{inputenc}
\usepackage[scale=0.85]{geometry}
\name{John}{Doe}
\title{Resume}
\phone{(123) 456-7890}
\email{john.doe@example.com}
\homepage{portfolio.com}
\social[github]{githubuser}
\social[linkedin]{linkedinuser}
\begin{document}
\makecvtitle
\section{Education}
\cventry{2018--2022}{Bachelor of Science in Computer Science}{University}{City}{}{GPA: 3.8/4.0}
\section{Experience}
\cventry{2022--Present}{Software Engineer}{Tech Company}{City}{}{
}
\end{document}""")
    
    return templates_dir


@pytest.mark.asyncio
async def test_generate_main_sections(generator, ensure_templates_dir, tmp_path):
    """Test that the generator creates a LaTeX file with all main sections"""
    output_path = tmp_path / "output_resume.tex"
    
    try:
        # Generate the LaTeX file
        result_path = await generator.generate(
            optimized_data=SAMPLE_RESUME_DATA,
            output_path=output_path,
            domain="computer_science"
        )
        
        print(f"\nGenerated LaTeX file at: {result_path}")
        assert result_path.exists(), f"Result path {result_path} does not exist"
        
        # Write debug information
        with open('latex_generator_debug.txt', 'w', encoding='utf-8') as debug_file:
            debug_file.write(f"Output path: {output_path}\n")
            debug_file.write(f"Result path: {result_path}\n")
            debug_file.write(f"Path exists: {result_path.exists()}\n")
            debug_file.write(f"Templates directory: {ensure_templates_dir}\n")
            debug_file.write(f"Templates exist: {(ensure_templates_dir / 'modern.tex').exists()}\n")
            
            # List files in templates directory
            debug_file.write("\nFiles in templates directory:\n")
            if ensure_templates_dir.exists():
                for file in ensure_templates_dir.iterdir():
                    debug_file.write(f"  {file}\n")
        
        # Read the generated file
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Write content to debug file
            with open('latex_generator_output.txt', 'w', encoding='utf-8') as debug_output:
                debug_output.write(content)
        
        # Check if all major sections are included
        assert "\\section{Education}" in content, "Education section missing"
        assert "\\section{Experience}" in content, "Experience section missing"
        assert "\\section{Projects}" in content, "Projects section missing"
        assert "\\section{Skills}" in content, "Skills section missing"
        
        # Check if contact info was updated
        assert "john.smith@example.com" in content, "Email not found in generated content"
        
        # Verify the content has proper LaTeX structure
        assert "\\begin{document}" in content, "Begin document tag missing"
        assert "\\end{document}" in content, "End document tag missing"
        
    except Exception as e:
        print(f"\nException in test_generate_main_sections: {str(e)}")
        # Write error information to a file
        with open('latex_generator_error.txt', 'w', encoding='utf-8') as error_file:
            error_file.write(f"Exception: {str(e)}\n")
            import traceback
            error_file.write(traceback.format_exc())
        raise


@pytest.mark.asyncio
async def test_education_section_generation(generator):
    """Test the generation of the education section specifically"""
    education_data = SAMPLE_RESUME_DATA["education"]
    latex_content = generator._generate_education_section(education_data)
    
    # Check basic structure
    assert "\\section{Education}" in latex_content
    
    # Check that education details are included
    assert "University of Computer Science" in latex_content
    assert "Bachelor of Science in Computer Science" in latex_content
    assert "GPA: 3.8/4.0" in latex_content


@pytest.mark.asyncio
async def test_experience_section_generation(generator):
    """Test the generation of the experience section specifically"""
    experience_data = SAMPLE_RESUME_DATA["experience"]
    latex_content = generator._generate_experience_section(experience_data)
    
    # Check basic structure
    assert "\\section{Experience}" in latex_content
    
    # Check that company and role details are included
    assert "Tech Company Inc." in latex_content
    assert "Software Engineer" in latex_content
    assert "Startup Innovation Labs" in latex_content
    
    # Check that bullet points are included
    assert "\\item " in latex_content
    assert "database optimization" in latex_content


@pytest.mark.asyncio
async def test_skills_section_generation(generator):
    """Test the generation of the skills section specifically"""
    skills_data = SAMPLE_RESUME_DATA["skills"]
    latex_content = generator._generate_skills_section(skills_data, "computer_science")
    
    # Check basic structure
    assert "\\section{Skills}" in latex_content
    
    # Check that skill categories are included
    assert "Languages" in latex_content
    assert "Frameworks" in latex_content
    assert "Tools" in latex_content
    
    # Check that specific skills are included
    assert "Python" in latex_content
    assert "JavaScript" in latex_content
    assert "React" in latex_content


@pytest.mark.asyncio
async def test_template_selection(generator, ensure_templates_dir):
    """Test that the generator selects the correct template"""
    # Test with an existing template
    template_path = generator._get_template_path("modern", "computer_science", "custom")
    assert template_path.name == "modern.tex"
    
    # Test with a non-existent template (should fall back to default)
    template_path = generator._get_template_path("nonexistent", "computer_science", "custom")
    assert template_path.exists()
    assert template_path.name in generator.default_templates.values()


@pytest.mark.asyncio
async def test_contact_info_updating(generator):
    """Test that contact information is updated in the template"""
    template_content = r"""
\name{Old}{Name}
\email{old@example.com}
\phone{(000) 000-0000}
\social[linkedin]{oldlinkedin}
\social[github]{oldgithub}
"""
    
    contact_info = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "(123) 456-7890",
        "linkedin": "johnlinkedin",
        "github": "johngithub"
    }
    
    updated_content = generator._update_contact_info(template_content, contact_info)
    
    # Check that all contact information was updated
    assert "\\name{John}{Smith}" in updated_content
    assert "\\email{john@example.com}" in updated_content
    assert "\\phone{(123) 456-7890}" in updated_content
    assert "\\social[linkedin]{johnlinkedin}" in updated_content
    assert "\\social[github]{johngithub}" in updated_content


if __name__ == "__main__":
    # Run tests directly if file is executed
    pytest.main(["-xvs", __file__])
