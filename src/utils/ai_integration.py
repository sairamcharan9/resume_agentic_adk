"""
AI Integration Module

This module handles integration with various AI models for resume optimization,
providing prompts, chains, and model management.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import asyncio

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.docstore.document import Document as LangchainDocument
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.retrievers import BM25Retriever

class AIManager:
    """
    Manages AI models, prompts, and chains for resume optimization.
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        """
        Initialize the AI Manager with specified model and temperature.
        
        Args:
            model_name: The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4")
            temperature: Model temperature (0.0 to 1.0), lower for more consistent outputs
        """
        # Check if API key is available
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key is not set. Set the OPENAI_API_KEY environment variable.")
        
        # Initialize the model
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize text splitter for long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Load prompts
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize prompt templates for different optimization tasks"""
        
        # Resume section optimization prompt
        self.section_optimization_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are an expert resume optimizer specializing in adapting content to match job descriptions "
                "while maintaining factual accuracy. Your goal is to improve a resume section to better align "
                "with the target job requirements."
            ),
            HumanMessagePromptTemplate.from_template(
                "I need to optimize this resume section to better match the job requirements:\n\n"
                "SECTION TYPE: {section_type}\n\n"
                "ORIGINAL CONTENT:\n{original_content}\n\n"
                "JOB REQUIREMENTS:\n{job_requirements}\n\n"
                "KEY SKILLS AND KEYWORDS:\n{keywords}\n\n"
                "OPTIMIZATION INSTRUCTIONS:\n"
                "1. Maintain all factual information - do not fabricate experience or skills\n"
                "2. Incorporate relevant keywords naturally\n"
                "3. Emphasize achievements and quantifiable results\n"
                "4. Use strong action verbs\n"
                "5. Keep a professional, concise tone\n"
                "6. Format consistently\n\n"
                "Please provide the optimized content for this section."
            )
        ])
        
        # Education optimization prompt
        self.education_optimization_template = PromptTemplate(
            input_variables=["education_entries", "job_requirements", "keywords"],
            template="""Optimize these education entries to better align with the job requirements
while maintaining complete factual accuracy.

ORIGINAL EDUCATION ENTRIES:
{education_entries}

JOB REQUIREMENTS:
{job_requirements}

KEY SKILLS AND KEYWORDS:
{keywords}

For each education entry:
1. Keep all factual information unchanged (institution, degree, dates)
2. Highlight relevant coursework that aligns with job requirements
3. Emphasize projects or achievements that demonstrate relevant skills
4. Use consistent formatting across all entries
5. List most recent/highest education first

OPTIMIZED EDUCATION ENTRIES:
"""
        )
        
        # Experience optimization prompt with focus on technical roles
        self.experience_optimization_template = PromptTemplate(
            input_variables=["experience_entries", "job_requirements", "keywords", "domain"],
            template="""Optimize these work experience entries to better match the job requirements in the {domain} domain
while maintaining complete factual accuracy.

ORIGINAL EXPERIENCE ENTRIES:
{experience_entries}

JOB REQUIREMENTS:
{job_requirements}

KEY SKILLS AND KEYWORDS:
{keywords}

For each experience entry:
1. Keep all factual information unchanged (company, role, dates)
2. Use strong action verbs and emphasize achievements with metrics
3. Incorporate relevant keywords naturally
4. Focus on accomplishments most relevant to the target job
5. Highlight technical skills that match the job requirements
6. Use bullet points effectively (3-5 per role)
7. Maintain professional tone and concise language

OPTIMIZED EXPERIENCE ENTRIES:
"""
        )
        
        # Skills optimization prompt
        self.skills_optimization_template = PromptTemplate(
            input_variables=["skills", "job_requirements", "keywords", "domain"],
            template="""Optimize this skills section to better match the job requirements in the {domain} domain.
Remember to maintain honesty - do not add skills that aren't in the original list.

ORIGINAL SKILLS:
{skills}

JOB REQUIREMENTS:
{job_requirements}

KEY SKILLS AND KEYWORDS:
{keywords}

Please:
1. Reorganize skills to prioritize those most relevant to the job requirements
2. Group skills by category (e.g., Programming Languages, Frameworks, Tools)
3. Use consistent formatting
4. Match the terminology used in the job description where appropriate
5. Do not fabricate or add skills not in the original list

OPTIMIZED SKILLS SECTION:
"""
        )
        
        # Summary/Profile optimization prompt
        self.summary_optimization_template = PromptTemplate(
            input_variables=["original_summary", "job_requirements", "keywords", "experience_level", "domain"],
            template="""Create an optimized professional summary for a {experience_level} professional in the {domain} field.

ORIGINAL SUMMARY:
{original_summary}

JOB REQUIREMENTS:
{job_requirements}

KEY SKILLS AND KEYWORDS:
{keywords}

Please create a powerful, concise professional summary that:
1. Captures attention in 3-5 sentences
2. Incorporates relevant keywords naturally
3. Highlights the candidate's unique value proposition
4. Aligns with the specific job requirements
5. Maintains a professional tone
6. Emphasizes experience level appropriately
7. Avoids clichés and generic statements

OPTIMIZED PROFESSIONAL SUMMARY:
"""
        )
    
    async def optimize_resume_section(self, 
                                section_type: str, 
                                original_content: str, 
                                job_requirements: str, 
                                keywords: List[str]) -> str:
        """
        Optimize a specific resume section to better match job requirements.
        
        Args:
            section_type: Type of section (e.g., "Experience", "Education", "Skills")
            original_content: Original section content
            job_requirements: Job requirements text
            keywords: List of relevant keywords
            
        Returns:
            Optimized section content
        """
        try:
            # Create the chain
            chain = LLMChain(llm=self.llm, prompt=self.section_optimization_template)
            
            # Run the chain
            result = await chain.arun(
                section_type=section_type,
                original_content=original_content,
                job_requirements=job_requirements,
                keywords=", ".join(keywords)
            )
            
            return result.strip()
            
        except Exception as e:
            raise Exception(f"Error optimizing resume section: {str(e)}")
    
    async def create_skill_match_analysis(self, 
                                        resume_skills: List[str], 
                                        job_skills: List[str],
                                        domain: str = "computer_science") -> Dict[str, Any]:
        """
        Analyze how well a resume's skills match the job requirements.
        
        Args:
            resume_skills: List of skills from the resume
            job_skills: List of skills from the job description
            domain: Domain focus (computer_science, data_science, ai_ml)
            
        Returns:
            Dictionary with match analysis
        """
        # Setup output parser for structured response
        response_schemas = [
            ResponseSchema(name="matching_skills", 
                           description="List of skills that are present in both the resume and job requirements"),
            ResponseSchema(name="missing_skills", 
                           description="List of skills from job requirements that are missing in the resume"),
            ResponseSchema(name="skill_match_percentage", 
                           description="Percentage of job skills covered by the resume (0-100)"),
            ResponseSchema(name="recommendations", 
                           description="List of recommendations for improving skill match")
        ]
        
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create the prompt template
        skill_match_template = PromptTemplate(
            input_variables=["resume_skills", "job_skills", "domain"],
            partial_variables={"format_instructions": format_instructions},
            template="""Analyze how well these resume skills match the job requirements for a {domain} position.

RESUME SKILLS:
{resume_skills}

JOB REQUIREMENTS SKILLS:
{job_skills}

Please provide:
1. A list of matching skills (skills present in both the resume and job requirements)
2. A list of missing skills (important skills from job requirements not found in the resume)
3. A skill match percentage (what percentage of job skills are covered by the resume)
4. Specific recommendations for improving the skill match

{format_instructions}
"""
        )
        
        try:
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=skill_match_template)
            result = await chain.arun(
                resume_skills=", ".join(resume_skills),
                job_skills=", ".join(job_skills),
                domain=domain
            )
            
            # Parse the structured output
            parsed_output = output_parser.parse(result)
            
            return parsed_output
            
        except Exception as e:
            raise Exception(f"Error analyzing skill match: {str(e)}")
    
    async def generate_ats_recommendations(self,
                                          resume_text: str,
                                          job_description: str,
                                          domain: str = "computer_science") -> Dict[str, Any]:
        """
        Generate recommendations for improving ATS compatibility.
        
        Args:
            resume_text: Full text of the resume
            job_description: Full text of the job description
            domain: Domain focus (computer_science, data_science, ai_ml)
            
        Returns:
            Dictionary with ATS recommendations
        """
        # Setup output parser for structured response
        response_schemas = [
            ResponseSchema(name="ats_score", 
                           description="Estimated ATS compatibility score (0-100)"),
            ResponseSchema(name="keyword_match", 
                           description="Score for keyword matching (0-100)"),
            ResponseSchema(name="format_score", 
                           description="Score for resume formatting (0-100)"),
            ResponseSchema(name="found_keywords", 
                           description="List of important keywords found in the resume"),
            ResponseSchema(name="missing_keywords", 
                           description="List of important keywords from the job description missing in the resume"),
            ResponseSchema(name="format_issues", 
                           description="List of identified formatting issues that could affect ATS scanning"),
            ResponseSchema(name="recommendations", 
                           description="List of specific recommendations to improve ATS compatibility")
        ]
        
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create the prompt template
        ats_template = PromptTemplate(
            input_variables=["resume_text", "job_description", "domain"],
            partial_variables={"format_instructions": format_instructions},
            template="""As an ATS (Applicant Tracking System) expert, analyze this resume against the job description for a {domain} position.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a comprehensive ATS compatibility analysis including:
1. An overall ATS compatibility score (0-100)
2. A keyword match score (0-100)
3. A format/structure score (0-100)
4. Important keywords found in the resume that match the job description
5. Important keywords from the job description missing in the resume
6. Any formatting issues that could negatively affect ATS scanning
7. Specific recommendations to improve ATS compatibility

Focus on the following ATS issues:
- Keyword matching with job description
- Use of standard section headings
- Appropriate formatting (avoiding tables, images, headers/footers, columns)
- Proper use of bullet points
- File format considerations
- Overall scannability

{format_instructions}
"""
        )
        
        try:
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=ats_template)
            result = await chain.arun(
                resume_text=resume_text,
                job_description=job_description,
                domain=domain
            )
            
            # Parse the structured output
            parsed_output = output_parser.parse(result)
            
            return parsed_output
            
        except Exception as e:
            raise Exception(f"Error generating ATS recommendations: {str(e)}")
    
    async def generate_impact_statements(self,
                                        experiences: List[str],
                                        skills: List[str],
                                        job_requirements: str,
                                        domain: str = "computer_science") -> List[str]:
        """
        Generate impact statements for work experiences to better highlight achievements.
        
        Args:
            experiences: List of experience bullet points
            skills: List of skills
            job_requirements: Job requirements text
            domain: Domain focus (computer_science, data_science, ai_ml)
            
        Returns:
            List of enhanced impact statements
        """
        impact_template = PromptTemplate(
            input_variables=["experiences", "skills", "job_requirements", "domain"],
            template="""Enhance these experience bullet points to create stronger impact statements for a {domain} position.
Focus on quantifiable achievements and results while maintaining factual accuracy.

ORIGINAL EXPERIENCE BULLET POINTS:
{experiences}

CANDIDATE SKILLS:
{skills}

JOB REQUIREMENTS:
{job_requirements}

For each bullet point:
1. Keep the core achievement or responsibility factually accurate
2. Add specific metrics or results where possible (%, numbers, etc.)
3. Use strong action verbs
4. Connect the achievement to a business impact
5. Incorporate relevant technical skills naturally
6. Format consistently (start with action verb, focus on results)

ENHANCED IMPACT STATEMENTS:
"""
        )
        
        try:
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=impact_template)
            result = await chain.arun(
                experiences="\n".join(experiences),
                skills=", ".join(skills),
                job_requirements=job_requirements,
                domain=domain
            )
            
            # Split the results into separate statements
            impact_statements = [stmt.strip() for stmt in result.strip().split("\n") if stmt.strip()]
            
            return impact_statements
            
        except Exception as e:
            raise Exception(f"Error generating impact statements: {str(e)}")




def main():
    """Test function for development purposes"""
    async def test_ai_manager():
        ai_manager = AIManager()
        
        # Test optimizing a resume section
        section = "I am a software engineer with 5 years of experience in web development."
        job_reqs = "Looking for a senior Python developer with experience in Django and REST APIs."
        keywords = ["Python", "Django", "REST API", "senior", "web development"]
        
        result = await ai_manager.optimize_resume_section(
            "Summary", section, job_reqs, keywords
        )
        
        print("Optimized Section:")
        print(result)
    
    # Run the test
    asyncio.run(test_ai_manager())

if __name__ == "__main__":
    main()
