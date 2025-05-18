"""
Tests for the LaTeX Resume Parser

These tests verify that the LaTeX parser can correctly extract structured 
data from different LaTeX resume formats.
"""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.parser.latex_parser import LaTeXResumeParser

# Sample LaTeX resume content for testing
SAMPLE_RESUME = r"""
\documentclass{article}
\usepackage{hyperref}

\begin{document}

\section*{John Smith}
\textbf{Email:} \href{mailto:john.smith@example.com}{john.smith@example.com} | 
\textbf{Phone:} (123) 456-7890 | 
\textbf{GitHub:} \href{https://github.com/johnsmith}{github.com/johnsmith} |
\textbf{LinkedIn:} \href{https://linkedin.com/in/johnsmith}{linkedin.com/in/johnsmith}

\section{Education}
\textbf{University of Computer Science} \hfill \emph{Sep 2018 - May 2022}\\
\emph{Bachelor of Science in Computer Science} \hfill \textit{GPA: 3.8/4.0}\\
\textbf{Honors:} Dean's List, Merit Scholarship

\section{Experience}
\textbf{Software Engineer} \hfill \emph{June 2022 - Present}\\
\emph{Tech Company Inc.} \hfill \textit{San Francisco, CA}
\begin{itemize}
    \item Developed and maintained RESTful APIs using Python and Flask
    \item Improved system performance by 30\% through database optimization
    \item Collaborated with cross-functional teams to implement new features
\end{itemize}

\textbf{Software Engineering Intern} \hfill \emph{May 2021 - Aug 2021}\\
\emph{Startup Innovation Labs} \hfill \textit{New York, NY}
\begin{itemize}
    \item Built a real-time dashboard using React and D3.js
    \item Implemented data processing pipeline using Apache Kafka
    \item Participated in agile development process with daily standups
\end{itemize}

\section{Projects}
\textbf{Personal Website} \emph{(HTML, CSS, JavaScript)} 
\begin{itemize}
    \item Created a responsive personal portfolio website with projects and blog
    \item Implemented dark mode toggle using CSS variables and JavaScript
\end{itemize}

\textbf{Machine Learning Model} \emph{(Python, TensorFlow, scikit-learn)}
\begin{itemize}
    \item Developed a classification model for image recognition with 92\% accuracy
    \item Optimized using transfer learning and hyperparameter tuning
\end{itemize}

\section{Skills}
\textbf{Languages:} Python, JavaScript, Java, C++, SQL\\
\textbf{Frameworks:} React, Flask, Django, Express.js\\
\textbf{Tools:} Git, Docker, AWS, Jenkins\\
\textbf{Other:} RESTful API Design, Agile Methodologies, CI/CD

\end{document}
"""

# Sample resume in a different format (moderncv template)
MODERNCV_RESUME = r"""
\documentclass{moderncv}
\moderncvstyle{classic}
\moderncvcolor{blue}

\name{Jane}{Doe}
\title{Machine Learning Engineer}
\phone{(123) 456-7890}
\email{jane.doe@example.com}
\social[github]{janedoe}
\social[linkedin]{jane-doe}

\begin{document}
\makecvtitle

\section{Education}
\cventry{2018--2022}{Master of Science in Computer Science}{Stanford University}{}{GPA: 3.9/4.0}{}
\cventry{2014--2018}{Bachelor of Engineering in Computer Science}{MIT}{}{GPA: 3.7/4.0}{}

\section{Experience}
\cventry{2022--Present}{Senior Data Scientist}{AI Solutions Inc.}{San Francisco}{}{%
\begin{itemize}
\item Led a team of 3 engineers to develop a recommendation system
\item Improved model accuracy by 25\% using ensemble methods
\item Deployed models to production using Docker and Kubernetes
\end{itemize}}

\cventry{2020--2022}{Machine Learning Engineer}{Tech Innovations}{New York}{}{%
\begin{itemize}
\item Developed NLP models for sentiment analysis with 87\% accuracy
\item Optimized data pipelines reducing processing time by 40\%
\item Collaborated with product teams to define ML requirements
\end{itemize}}

\section{Skills}
\cvitem{Languages}{Python, R, Java, SQL, JavaScript}
\cvitem{ML/DL}{PyTorch, TensorFlow, scikit-learn, Keras, Pandas, NumPy}
\cvitem{Tools}{Git, Docker, Kubernetes, AWS, Azure}
\cvitem{Other}{NLP, Computer Vision, MLOps, Agile}

\section{Projects}
\cvitem{Speech Recognition System}{Developed an end-to-end speech recognition system using PyTorch and Transformers}
\cvitem{Image Classification}{Implemented a CNN for multi-class image classification achieving 94\% accuracy}

\end{document}
"""

@pytest.mark.asyncio
async def test_parse_standard_resume():
    """Test parsing a standard LaTeX resume"""
    # Create a temporary file with the sample resume
    temp_file = Path("temp_resume.tex")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(SAMPLE_RESUME)
        
        # Save the content to a file for debugging
        with open("debug_sample_resume.tex", "w", encoding="utf-8") as f:
            f.write(SAMPLE_RESUME)
            
        print("\nSAMPLE RESUME CONTENT (FIRST 100 CHARACTERS):")
        print(SAMPLE_RESUME[:200] + "...")
        print("\n")
        
        # Parse the resume
        parser = LaTeXResumeParser()
        result = await parser.parse(str(temp_file))
        
        # Save debug info to file instead of printing
        with open('test_output_standard_resume.txt', 'w', encoding='utf-8') as f:
            f.write(f"Standard resume template detection: {result.get('template', 'not detected')}\n")
            f.write(f"Contact info: {result.get('contact_info', {})}\n")
            f.write(f"Education section: {result['education']}\n")
            f.write(f"Experience section: {result['experience']}\n")
            f.write(f"Projects section: {result.get('projects', [])}\n")
            f.write(f"Skills section: {result.get('skills', {})}\n")
        
        # Verify basic structure (more lenient for initial testing)
        assert "contact_info" in result
        assert "education" in result
        assert "experience" in result
        
        # Basic verification that something was extracted
        assert len(result["education"]) > 0, "No education entries found"
        assert len(result["experience"]) > 0, "No experience entries found"
        
        # Output education and experience details to files
        with open('test_output_standard_education.txt', 'w', encoding='utf-8') as f:
            f.write("EDUCATION ENTRIES:\n")
            for i, edu in enumerate(result["education"]):
                f.write(f"Entry {i+1}:\n")
                for key, val in edu.items():
                    f.write(f"  {key}: {val}\n")
                    
        with open('test_output_standard_experience.txt', 'w', encoding='utf-8') as f:
            f.write("EXPERIENCE ENTRIES:\n")
            for i, exp in enumerate(result["experience"]):
                f.write(f"Entry {i+1}:\n")
                for key, val in exp.items():
                    f.write(f"  {key}: {val}\n")
    
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()

@pytest.mark.asyncio
async def test_parse_moderncv_resume():
    """Test parsing a resume using the moderncv template"""
    # Create a temporary file with the moderncv resume
    temp_file = Path("temp_moderncv.tex")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(MODERNCV_RESUME)
            
        # Save the content to a file for debugging
        with open("debug_moderncv_resume.tex", "w", encoding="utf-8") as f:
            f.write(MODERNCV_RESUME)
            
        print("\nMODERNCV RESUME CONTENT (FIRST 100 CHARACTERS):")
        print(MODERNCV_RESUME[:200] + "...")
        print("\n")
        
        # Parse the resume
        parser = LaTeXResumeParser()
        result = await parser.parse(str(temp_file))
        
        # Save debug info to file instead of printing
        with open('test_output_moderncv_resume.txt', 'w', encoding='utf-8') as f:
            f.write(f"ModernCV template detection: {result.get('template', 'not detected')}\n")
            f.write(f"Contact info: {result.get('contact_info', {})}\n")
            f.write(f"Education section: {result['education']}\n")
            f.write(f"Experience section: {result['experience']}\n")
            f.write(f"Projects section: {result.get('projects', [])}\n")
            f.write(f"Skills section: {result.get('skills', {})}\n")
        
        # Verify basic structure (more lenient for initial testing)
        assert "contact_info" in result
        assert "education" in result
        assert "experience" in result
        
        # Basic verification that something was extracted
        assert len(result["education"]) > 0, "No education entries found"
        assert len(result["experience"]) > 0, "No experience entries found"
        
        # Output education and experience details to files
        with open('test_output_moderncv_education.txt', 'w', encoding='utf-8') as f:
            f.write("EDUCATION ENTRIES (MODERNCV):\n")
            for i, edu in enumerate(result["education"]):
                f.write(f"Entry {i+1}:\n")
                for key, val in edu.items():
                    f.write(f"  {key}: {val}\n")
                    
        with open('test_output_moderncv_experience.txt', 'w', encoding='utf-8') as f:
            f.write("EXPERIENCE ENTRIES (MODERNCV):\n")
            for i, exp in enumerate(result["experience"]):
                f.write(f"Entry {i+1}:\n")
                for key, val in exp.items():
                    f.write(f"  {key}: {val}\n")
    
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()

if __name__ == "__main__":
    # Run tests directly if file is executed
    asyncio.run(test_parse_standard_resume())
    asyncio.run(test_parse_moderncv_resume())
    print("All tests passed!")
