"""
End-to-End Test for Resume Optimizer

This test validates the complete optimization pipeline from resume upload through
optimization to PDF generation and ensures all components work together correctly.
"""

import os
import sys
import asyncio
import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest import mock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.latex_parser import LaTeXResumeParser
from src.optimizer.resume_optimizer import ResumeOptimizer
from src.latex_generator.generator import LaTeXGenerator
from src.ats.ats_analyzer import ATSAnalyzer
from src.utils.ai_integration import AIManager


class TestEndToEnd:
    """Test the complete Resume Optimizer workflow"""

    @pytest.fixture
    def sample_resume(self) -> Path:
        """Fixture to provide a sample LaTeX resume"""
        resume_path = Path(__file__).parent / "samples" / "sample_resume.tex"
        if not resume_path.exists():
            # Create test directory if it doesn't exist
            resume_path.parent.mkdir(exist_ok=True)
            
            # Write a basic LaTeX resume for testing
            resume_path.write_text(r"""
\documentclass{article}
\usepackage[margin=1in]{geometry}

\begin{document}

\begin{center}
    {\LARGE \textbf{John Doe}}\\
    123 Main Street, Anytown, USA 12345\\
    (555) 123-4567 | john.doe@email.com | linkedin.com/in/johndoe | github.com/johndoe
\end{center}

\section*{Education}
\textbf{University of Technology} \hfill Anytown, USA\\
B.S. Computer Science, GPA: 3.8/4.0 \hfill Sept 2018 - May 2022
\begin{itemize}
    \item Coursework: Data Structures, Algorithms, Machine Learning, Databases, Software Engineering
    \item Honors: Dean's List (All Semesters), Outstanding Academic Achievement Award
\end{itemize}

\section*{Experience}
\textbf{Software Engineer Intern} \hfill June 2021 - August 2021\\
Tech Company, Anytown, USA
\begin{itemize}
    \item Developed a RESTful API using Python and Flask that improved data retrieval speeds by 30\%
    \item Implemented automated unit tests that increased code coverage by 15\%
    \item Collaborated with a team of 5 engineers to design and deploy microservices architecture
\end{itemize}

\textbf{Research Assistant} \hfill Jan 2020 - May 2021\\
University AI Lab, Anytown, USA
\begin{itemize}
    \item Implemented machine learning algorithms for natural language processing tasks
    \item Collected and preprocessed datasets for training models, improving accuracy by 12\%
    \item Presented research findings at university symposium
\end{itemize}

\section*{Projects}
\textbf{E-commerce Platform} \hfill Github.com/johndoe/ecommerce\\
\begin{itemize}
    \item Built a full-stack e-commerce platform using React, Node.js, and MongoDB
    \item Implemented secure payment processing with Stripe API
    \item Deployed application using Docker containers on AWS EC2
\end{itemize}

\textbf{Smart Home System} \hfill Github.com/johndoe/smarthome\\
\begin{itemize}
    \item Developed IoT system using Raspberry Pi to control home appliances
    \item Created a mobile app using React Native for remote control
    \item Implemented voice control using natural language processing
\end{itemize}

\section*{Skills}
\textbf{Programming Languages:} Python, JavaScript, Java, C++, SQL\\
\textbf{Technologies:} React, Node.js, Express, Django, Flask, Docker, Git, AWS, TensorFlow\\
\textbf{Concepts:} Data Structures, Algorithms, Machine Learning, RESTful APIs, CI/CD, Agile Methodologies

\end{document}
""")
        return resume_path

    @pytest.fixture
    def sample_job_description(self) -> Dict[str, Any]:
        """Fixture to provide a sample job description"""
        return {
            "title": "Software Engineer",
            "description": """
            We are looking for a talented Software Engineer to join our engineering team.
            The ideal candidate has experience in full-stack development, with a focus on
            building scalable web applications. You should have strong problem-solving skills
            and experience with modern JavaScript frameworks.
            
            Responsibilities:
            - Design and implement new features for our web application
            - Write clean, maintainable and efficient code
            - Work with product managers to understand requirements
            - Participate in code reviews and architectural discussions
            - Fix bugs and improve application performance
            
            Requirements:
            - Bachelor's degree in Computer Science or related field
            - 2+ years of experience in software development
            - Proficient in JavaScript and Python
            - Experience with React and Node.js
            - Familiarity with database technologies (SQL and NoSQL)
            - Experience with cloud services (AWS, GCP, or Azure)
            - Strong problem-solving and analytical skills
            """,
            "requirements": [
                "JavaScript",
                "Python",
                "React",
                "Node.js",
                "Database technologies",
                "Cloud services",
                "Problem-solving skills"
            ],
            "company": "Tech Innovators Inc.",
            "location": "San Francisco, CA",
            "domain": "computer_science"
        }

    @pytest.fixture
    def mock_ai_manager(self):
        """Fixture to mock AI Manager responses"""
        with mock.patch('src.optimizer.resume_optimizer.AIManager') as mock_ai:
            # Mock the optimize method to return a plausible optimization
            mock_instance = mock_ai.return_value
            
            async def mock_optimize(*args, **kwargs):
                return {
                    "summary": "Resume optimized for software engineering role",
                    "improvements": [
                        "Highlighted JavaScript and Python skills",
                        "Added React and Node.js experience",
                        "Emphasized cloud service knowledge"
                    ],
                    "contact_info": {
                        "name": "John Doe",
                        "email": "john.doe@email.com",
                        "phone": "(555) 123-4567",
                        "linkedin": "linkedin.com/in/johndoe",
                        "github": "github.com/johndoe",
                        "address": "123 Main Street, Anytown, USA 12345"
                    },
                    "education": [
                        {
                            "institution": "University of Technology",
                            "degree": "B.S. Computer Science",
                            "gpa": "3.8/4.0",
                            "location": "Anytown, USA",
                            "date": "Sept 2018 - May 2022",
                            "details": [
                                "Coursework: Data Structures, Algorithms, Machine Learning, Databases, Software Engineering",
                                "Honors: Dean's List (All Semesters), Outstanding Academic Achievement Award"
                            ]
                        }
                    ],
                    "experience": [
                        {
                            "role": "Software Engineer Intern",
                            "company": "Tech Company",
                            "location": "Anytown, USA",
                            "date": "June 2021 - August 2021",
                            "details": [
                                "Developed a RESTful API using Python and Flask that improved data retrieval speeds by 30%",
                                "Implemented automated unit tests using Jest that increased code coverage by 15%",
                                "Collaborated with a team of 5 engineers to design and deploy React-based microservices architecture"
                            ]
                        },
                        {
                            "role": "Research Assistant",
                            "company": "University AI Lab",
                            "location": "Anytown, USA",
                            "date": "Jan 2020 - May 2021",
                            "details": [
                                "Implemented machine learning algorithms for natural language processing tasks using Python",
                                "Collected and preprocessed datasets for training models, improving accuracy by 12%",
                                "Presented research findings at university symposium on AI technologies"
                            ]
                        }
                    ],
                    "projects": [
                        {
                            "name": "E-commerce Platform",
                            "url": "Github.com/johndoe/ecommerce",
                            "details": [
                                "Built a full-stack e-commerce platform using React, Node.js, and MongoDB",
                                "Implemented secure payment processing with Stripe API and AWS Lambda functions",
                                "Deployed application using Docker containers on AWS EC2 with CI/CD pipeline"
                            ]
                        },
                        {
                            "name": "Smart Home System",
                            "url": "Github.com/johndoe/smarthome",
                            "details": [
                                "Developed IoT system using Raspberry Pi and JavaScript to control home appliances",
                                "Created a mobile app using React Native for remote control with real-time updates",
                                "Implemented voice control using natural language processing and cloud-based APIs"
                            ]
                        }
                    ],
                    "skills": {
                        "Programming Languages": "Python, JavaScript, Java, C++, SQL",
                        "Technologies": "React, Node.js, Express, Django, Flask, Docker, Git, AWS, TensorFlow",
                        "Concepts": "Data Structures, Algorithms, Machine Learning, RESTful APIs, CI/CD, Agile Methodologies"
                    }
                }
            
            mock_instance.optimize.side_effect = mock_optimize
            yield mock_instance

    @pytest.mark.asyncio
    async def test_complete_optimization_pipeline(self, sample_resume, sample_job_description, mock_ai_manager):
        """Test the complete optimization pipeline from parsing to generation"""
        try:
            # 1. Parse the resume
            parser = LaTeXResumeParser()
            parsed_resume = await parser.parse(str(sample_resume))
            assert parsed_resume is not None
            assert "contact_info" in parsed_resume
            assert "education" in parsed_resume
            assert "experience" in parsed_resume
            assert "skills" in parsed_resume
            
            print("✓ Resume parsed successfully")
            
            # 2. Create optimizer (with mocked AI)
            optimizer = ResumeOptimizer(ai_manager=mock_ai_manager)
            
            # 3. Optimize the resume
            optimized_data = await optimizer.optimize(
                parsed_resume,
                sample_job_description,
                special_instructions={"focus_areas": ["web development", "cloud technologies"]}
            )
            
            assert optimized_data is not None
            assert "summary" in optimized_data
            assert "improvements" in optimized_data
            assert len(optimized_data["improvements"]) > 0
            print("✓ Resume optimized successfully")
            
            # 4. Generate LaTeX output
            latex_gen = LaTeXGenerator()
            with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
                output_path = Path(tmp.name)
                
            await latex_gen.generate(optimized_data, output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            latex_content = output_path.read_text()
            assert "\\documentclass" in latex_content
            assert "\\begin{document}" in latex_content
            print("✓ LaTeX file generated successfully")
            
            # 5. Generate PDF (if latexmk is available)
            pdf_path = output_path.with_suffix(".pdf")
            try:
                await latex_gen.generate_pdf(output_path)
                pdf_exists = pdf_path.exists()
                if pdf_exists:
                    print("✓ PDF file generated successfully")
                else:
                    print("⚠ PDF generation skipped (latexmk may not be available)")
            except Exception as e:
                print(f"⚠ PDF generation failed: {str(e)}")
            
            # 6. Analyze ATS compatibility
            ats_analyzer = ATSAnalyzer()
            ats_results = await ats_analyzer.analyze(output_path, sample_job_description)
            
            assert ats_results is not None
            assert "ats_score" in ats_results
            assert "keyword_match_score" in ats_results
            assert 0 <= ats_results["ats_score"] <= 100
            assert 0 <= ats_results["keyword_match_score"] <= 100
            print("✓ ATS analysis completed successfully")
            
            # 7. Clean up temporary files
            output_path.unlink(missing_ok=True)
            pdf_path.unlink(missing_ok=True)
            
            print("\n✓ End-to-end test completed successfully")
            
        except Exception as e:
            pytest.fail(f"End-to-end test failed: {str(e)}")

if __name__ == "__main__":
    # Run the test directly if this file is executed
    asyncio.run(TestEndToEnd().test_complete_optimization_pipeline(
        TestEndToEnd().sample_resume(),
        TestEndToEnd().sample_job_description(),
        TestEndToEnd().mock_ai_manager()
    ))
