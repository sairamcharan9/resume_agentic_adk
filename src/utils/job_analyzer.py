"""
Job Description Analyzer

This module analyzes job descriptions to extract key requirements, skills,
and keywords relevant for resume optimization.
"""

import re
import asyncio
from typing import Dict, List, Any, Optional
import os

# Import Langchain components
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

class JobDescriptionAnalyzer:
    """
    Analyzes job descriptions to extract key information for resume optimization,
    with specialized focus on Computer Science, Data Science, and AI/ML positions.
    """
    
    def __init__(self):
        """Initialize the job description analyzer with LLM model and domain-specific terms"""
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.2,  # Low temperature for consistent, factual analysis
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Domain-specific keyword sets
        self.domain_terms = {
            "computer_science": [
                "software engineer", "software developer", "full stack", "backend", "frontend", 
                "devops", "system design", "microservices", "cloud", "aws", "azure", 
                "distributed systems", "algorithms", "data structures", "software architecture",
                "REST API", "GraphQL", "containerization", "docker", "kubernetes", "CI/CD",
                "agile", "scrum", "git", "version control", "testing", "debugging",
                "scalability", "performance optimization", "web development", "mobile development"
            ],
            "data_science": [
                "data scientist", "data analyst", "data engineer", "business intelligence",
                "statistical analysis", "data mining", "machine learning", "data visualization",
                "predictive modeling", "A/B testing", "hypothesis testing", "regression",
                "clustering", "dimensionality reduction", "feature engineering", "ETL",
                "data warehousing", "SQL", "NoSQL", "big data", "data pipeline",
                "pandas", "numpy", "matplotlib", "scikit-learn", "tableau", "power bi",
                "data cleaning", "exploratory data analysis", "statistical significance"
            ],
            "ai_ml": [
                "machine learning engineer", "ai researcher", "nlp engineer", "computer vision",
                "deep learning", "neural networks", "reinforcement learning", "natural language processing",
                "computer vision", "generative ai", "transformers", "large language models",
                "tensorflow", "pytorch", "keras", "model training", "model deployment",
                "model evaluation", "hyperparameter tuning", "feature extraction",
                "transfer learning", "sentiment analysis", "image recognition", "speech recognition",
                "MLOps", "AI ethics", "supervised learning", "unsupervised learning"
            ]
        }
        
        # Programming languages, frameworks, and tools by domain
        self.tech_by_domain = {
            "computer_science": [
                # Languages
                "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby",
                # Web Frameworks
                "react", "angular", "vue", "django", "flask", "spring", "express", "asp.net",
                "fastapi", "ruby on rails", "laravel", "node.js",
                # Mobile
                "android", "ios", "swift", "kotlin", "react native", "flutter",
                # DevOps & Infrastructure
                "docker", "kubernetes", "jenkins", "aws", "azure", "gcp", "terraform", "ansible",
                "prometheus", "grafana", "elk stack", "ci/cd",
                # Databases
                "sql", "mysql", "postgresql", "mongodb", "dynamodb", "redis", "elasticsearch",
                "cassandra", "oracle", "sql server"
            ],
            "data_science": [
                # Languages
                "python", "r", "sql", "scala", "julia",
                # Libraries & Frameworks
                "pandas", "numpy", "scipy", "scikit-learn", "matplotlib", "seaborn", "plotly",
                "tensorflow", "keras", "pytorch", "pyspark", "dplyr", "ggplot2", "tidyr",
                # Big Data
                "hadoop", "spark", "kafka", "airflow", "hive", "pig", "snowflake", "databricks",
                # BI Tools
                "tableau", "power bi", "looker", "quicksight", "domo", "mode analytics",
                # Databases
                "sql", "mysql", "postgresql", "redshift", "bigquery", "snowflake", "mongodb"
            ],
            "ai_ml": [
                # Languages
                "python", "c++", "julia", "r",
                # ML Frameworks
                "tensorflow", "pytorch", "keras", "scikit-learn", "hugging face", "transformers",
                "fast.ai", "mxnet", "xgboost", "lightgbm", "catboost",
                # NLP
                "nltk", "spacy", "gensim", "bert", "gpt", "word2vec", "glove", "transformers",
                # Computer Vision
                "opencv", "pillow", "torch vision", "yolo", "resnet", "efficientnet",
                # MLOps
                "mlflow", "kubeflow", "airbyte", "airflow", "weights & biases", "sagemaker",
                "docker", "kubernetes", "github actions", "tensorboard", "ray",
                # Big Data for ML
                "spark", "dask", "vaex", "hadoop", "kafka"
            ]
        }
        
        # Setup output parser for structured responses
        self.response_schemas = [
            ResponseSchema(name="title",
                           description="Standardized job title"),
            ResponseSchema(name="requirements",
                           description="List of key job requirements extracted from the description"),
            ResponseSchema(name="skills",
                           description="List of technical and soft skills required for the job"),
            ResponseSchema(name="technologies",
                           description="List of specific technologies, frameworks, languages, and tools mentioned"),
            ResponseSchema(name="keywords",
                           description="List of important keywords from the job description"),
            ResponseSchema(name="experience_level",
                           description="The experience level required (entry, mid, senior, lead, etc.)"),
            ResponseSchema(name="domain_focus",
                           description="The specific focus area within CS/Data Science/AI")
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()
    
    async def analyze(self, 
                     title: str,
                     description: str,
                     requirements: List[str],
                     domain: str = "computer_science") -> Dict[str, Any]:
        """
        Analyze a job description to extract key information
        
        Args:
            title: Job title
            description: Full job description text
            requirements: List of explicit requirements from the job posting
            domain: Domain focus (computer_science, data_science, or ai_ml)
            
        Returns:
            Dict containing analyzed job information
        """
        try:
            # Combine requirements into a string
            requirements_text = "\n".join([f"- {req}" for req in requirements])
            
            # Get domain-specific terms to focus on
            domain_terms = self.domain_terms.get(domain, self.domain_terms["computer_science"])
            domain_techs = self.tech_by_domain.get(domain, self.tech_by_domain["computer_science"])
            
            # Create prompt for job analysis
            prompt_template = PromptTemplate(
                input_variables=["title", "description", "requirements", "domain", "domain_terms", "domain_techs"],
                template="""You are an expert in analyzing job descriptions for {domain} positions to help tailor resumes.

JOB TITLE:
{title}

JOB DESCRIPTION:
{description}

LISTED REQUIREMENTS:
{requirements}

DOMAIN FOCUS: {domain}

RELEVANT DOMAIN TERMS:
{domain_terms}

RELEVANT TECHNOLOGIES:
{domain_techs}

ANALYSIS INSTRUCTIONS:
1. Focus exclusively on the {domain} domain
2. Identify explicit and implicit requirements from the job description
3. Extract technical skills, soft skills, and required experience
4. Identify specific technologies, frameworks, languages, and tools mentioned
5. Extract keywords that would be important for resume matching
6. Determine the experience level required
7. Identify the specific focus area within the broader domain

{format_instructions}
"""
            )
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = await chain.arun(
                title=title,
                description=description,
                requirements=requirements_text,
                domain=domain,
                domain_terms=", ".join(domain_terms[:20]),  # Limit to avoid token overload
                domain_techs=", ".join(domain_techs[:20]),  # Limit to avoid token overload
                format_instructions=self.format_instructions
            )
            
            # Parse the structured output
            parsed_output = self.output_parser.parse(result)
            
            return parsed_output
            
        except Exception as e:
            raise Exception(f"Job description analysis failed: {str(e)}")
    
    def analyze_text(self, job_description_text: str, domain: str = "computer_science") -> Dict[str, Any]:
        """
        Analyze a consolidated job description text to extract structured information
        
        This method processes a full job description text and extracts the job title,
        requirements, and other key information without requiring separate inputs.
        
        Args:
            job_description_text: The full job description text
            domain: Domain focus (computer_science, data_science, or ai_ml)
            
        Returns:
            Dict containing analyzed job information
        """
        try:
            # Extract quick keywords for initial analysis
            quick_keywords = self.extract_quick_keywords(job_description_text, domain)
            
            # Try to extract job title from the text
            title = self._extract_job_title(job_description_text)
            
            # Try to extract requirements from the text
            requirements = self._extract_requirements(job_description_text)
            
            # Use the full analysis method with extracted components
            result = asyncio.run(self.analyze(
                title=title,
                description=job_description_text,
                requirements=requirements,
                domain=domain
            ))
            
            return result
        
        except Exception as e:
            # Fallback to a simple analysis if the full analysis fails
            return {
                "title": self._extract_job_title(job_description_text),
                "requirements": self._extract_requirements(job_description_text),
                "skills": quick_keywords,
                "keywords": quick_keywords,
                "technologies": [k for k in quick_keywords if k in self.tech_by_domain.get(domain, [])],
                "experience_level": self._extract_experience_level(job_description_text),
                "domain_focus": domain
            }
    
    def _extract_job_title(self, text: str) -> str:
        """
        Extract the job title from a job description text
        
        Args:
            text: Job description text
            
        Returns:
            Extracted job title or default
        """
        # Common job title patterns
        title_patterns = [
            # Look for common title formats like "Job Title: Software Engineer"
            r"(?:job title|position|role)\s*(?::|is|as)\s*([^\n.,]{3,50})",
            # Look for titles at the beginning with emphasis (uppercase, etc)
            r"^\s*([A-Z][A-Z\s]{3,30})\s*$",
            # Look for common tech job titles
            r"\b(software engineer|data scientist|machine learning engineer|data engineer|full stack developer|frontend developer|backend developer|devops engineer|cloud architect|product manager|project manager|technical lead|engineering manager|CTO|VP of Engineering|SDET|QA Engineer)\b"
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                return matches[0].strip()
        
        # If no specific title found, look for the first sentence that might contain the title
        first_lines = text.split('\n')[:3]  # Check first 3 lines
        for line in first_lines:
            line = line.strip()
            if 5 < len(line) < 100 and not line.endswith(':'):  # Reasonable title length
                return line
        
        return "Position"  # Default fallback
    
    def _extract_requirements(self, text: str) -> List[str]:
        """
        Extract requirements from a job description text
        
        Args:
            text: Job description text
            
        Returns:
            List of extracted requirements
        """
        requirements = []
        
        # Look for requirements section
        req_section_patterns = [
            r"(?:requirements|qualifications|what you('ll| will) need|what we('re| are) looking for)\s*:?([\s\S]*?)(?:\n\n|\n\s*\n|$|skills|responsibilities|what you('ll| will) do)",
            r"(?:\n|^)\s*[\*\-•]\s*([^\n]{10,150})(?:\n|$)"
        ]
        
        for pattern in req_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # If the match is a tuple (multiple capture groups), get the last non-empty one
                    content = next((m for m in reversed(match) if m), "")
                else:
                    content = match
                
                # Split by common list indicators
                items = re.split(r'\n\s*[\*\-•]\s*', content)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 10:
                        requirements.append(item)
        
        # If no structured requirements found, look for sentences with requirement keywords
        if not requirements:
            req_keywords = ["required", "must have", "should have", "minimum", "at least", "proficient"]
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in req_keywords):
                    requirements.append(sentence.strip())
        
        return requirements[:10]  # Return top 10 requirements to avoid overwhelming
    
    def _extract_experience_level(self, text: str) -> str:
        """
        Extract experience level from job description text
        
        Args:
            text: Job description text
            
        Returns:
            Estimated experience level
        """
        text_lower = text.lower()
        
        # Check for explicit level mentions
        level_patterns = {
            "entry": [r"entry[ -]level", r"junior", r"0-2 years", r"less than 2 years", r"new grad", r"recent graduate"],
            "mid": [r"mid[ -]level", r"intermediate", r"2-5 years", r"3-5 years", r"3\+ years"],
            "senior": [r"senior", r"sr\.", r"lead", r"5\+ years", r"5-7 years", r"7\+ years", r"principal"],
            "manager": [r"manager", r"director", r"head of", r"vp", r"chief", r"10\+ years"]
        }
        
        for level, patterns in level_patterns.items():
            if any(re.search(pattern, text_lower) for pattern in patterns):
                return level
        
        # Default to mid-level if no clear indication
        return "mid"
    
    def extract_quick_keywords(self, text: str, domain: str = "computer_science") -> List[str]:
        """
        Quickly extract potential keywords from text without using the LLM
        Useful for initial processing and sorting
        
        Args:
            text: Text to analyze
            domain: Domain to focus on
            
        Returns:
            List of extracted keywords
        """
        keywords = []
        
        # Get domain-specific terms
        domain_terms = self.domain_terms.get(domain, self.domain_terms["computer_science"])
        domain_techs = self.tech_by_domain.get(domain, self.tech_by_domain["computer_science"])
        
        all_terms = domain_terms + domain_techs
        
        # Simple keyword extraction based on domain terms
        for term in all_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                keywords.append(term)
        
        # Extract years of experience requirements
        exp_patterns = [
            r'(\d+)\+?\s+years?\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\+?\s+years?',
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                keywords.append(f"{match}+ years experience")
        
        # Extract education requirements
        edu_patterns = [
            r"bachelor'?s?|master'?s?|phd|doctorate|bs|ba|ms|msc|meng|bsc|beng",
            r"degree in (?:computer science|cs|software engineering|data science|machine learning|artificial intelligence|ai|ml|information technology|it)"
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                keywords.append(match.lower())
        
        return list(set(keywords))  # Remove duplicates
