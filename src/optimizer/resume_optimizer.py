"""
Resume Optimizer Module

This module is responsible for optimizing resume content based on job descriptions
and special instructions, specifically for Computer Science, Data Science, and AI/ML positions.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass

# LangChain imports
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Import required modules
from src.utils.job_analyzer import JobDescriptionAnalyzer
from src.utils.ai_integration import AIManager

class ResumeOptimizer:
    """
    Optimize resume content based on job descriptions and special instructions
    for Computer Science, Data Science, and AI/ML domains.
    """
    
    def __init__(self, ai_manager: Optional[AIManager] = None):
        """Initialize the resume optimizer with AI model and templates
        
        Args:
            ai_manager: Optional AIManager instance for model customization
        """
        # Initialize the AI manager or create a default one
        if ai_manager is None:
            # Create default AIManager - prefer free models if available
            self.ai_manager = AIManager()
        else:
            self.ai_manager = ai_manager
            
        # Use the LLM from the AI manager
        self.llm = self.ai_manager.llm
        
        # Initialize the job description analyzer
        self.job_analyzer = JobDescriptionAnalyzer()
        
        # Define domain-specific keywords
        self.domains = {
            "computer_science": [
                "software development", "programming", "algorithms", "data structures",
                "software engineering", "web development", "mobile development", 
                "devops", "system design", "backend", "frontend", "full-stack",
                "cloud computing", "microservices", "containers", "version control",
                "CI/CD", "testing", "debugging", "API", "scalability", "performance"
            ],
            "data_science": [
                "data analysis", "statistics", "machine learning", "data visualization",
                "big data", "data mining", "predictive modeling", "data engineering",
                "ETL", "data warehousing", "business intelligence", "A/B testing",
                "hypothesis testing", "regression", "clustering", "feature engineering",
                "data cleaning", "SQL", "NoSQL", "data pipelines", "data modeling"
            ],
            "ai_ml": [
                "artificial intelligence", "machine learning", "deep learning", "neural networks",
                "natural language processing", "computer vision", "reinforcement learning",
                "generative AI", "transformers", "large language models", "supervised learning",
                "unsupervised learning", "model training", "model deployment", "MLOps",
                "feature extraction", "hyperparameter tuning", "transfer learning"
            ]
        }
        
        # Setup output parser for structured responses
        self.response_schemas = [
            ResponseSchema(name="optimized_item",
                           description="The optimized resume item (experience or project) with all required fields"),
            ResponseSchema(name="changes_made",
                           description="List of specific changes made to optimize this item"),
            ResponseSchema(name="relevance_score",
                           description="A score from 1-100 indicating how relevant this item is to the job description"),
            ResponseSchema(name="keywords_used",
                           description="List of job description keywords incorporated into this item")
        ]
        
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()
    
    async def optimize(self, 
                       parsed_resume: Dict[str, Any],
                       job_description: Any,
                       special_instructions: Optional[Any] = None) -> Dict[str, Any]:
        """
        Optimize a parsed resume based on the job description and special instructions
        
        Args:
            parsed_resume: Structured resume data from the LaTeXResumeParser
            job_description: JobDescription model with title, description, requirements, etc.
            special_instructions: Optional SpecialInstructions model with focus areas, etc.
            
        Returns:
            Dict containing optimized resume data and optimization metrics
        """
        try:
            # Analyze job description to extract key requirements, skills, and keywords
            job_analysis = await self.job_analyzer.analyze(
                job_description.title,
                job_description.description,
                job_description.requirements,
                domain=job_description.domain
            )
            
            # Create optimized resume structure
            optimized_resume = {
                "contact_info": parsed_resume["contact_info"],
                "education": parsed_resume["education"],  # Education usually doesn't need optimization
                "experience": [],
                "projects": [],
                "skills": await self._optimize_skills(parsed_resume["skills"], job_analysis),
                "publications": parsed_resume["publications"],  # Publications usually don't need optimization
                "awards": parsed_resume["awards"],
                "summary": "",  # Will be generated
                "improvements": [],  # List of key improvements
                "keywords_matched": [],  # Keywords matched from job description
                "ats_recommendations": []  # ATS-specific recommendations
            }
            
            # Special instructions processing
            focus_areas = []
            highlight_skills = []
            tone = "professional"
            
            if special_instructions:
                focus_areas = special_instructions.focus_areas or []
                highlight_skills = special_instructions.highlight_skills or []
                tone = special_instructions.tone or "professional"
            
            # Optimize experience section
            optimized_resume["experience"] = await self._optimize_experience(
                parsed_resume["experience"],
                job_analysis,
                focus_areas,
                highlight_skills,
                tone
            )
            
            # Optimize projects section
            optimized_resume["projects"] = await self._optimize_projects(
                parsed_resume["projects"],
                job_analysis,
                focus_areas,
                highlight_skills,
                tone
            )
            
            # Generate a summary of optimizations
            optimized_resume["summary"] = await self._generate_optimization_summary(
                optimized_resume,
                job_analysis,
                job_description.title
            )
            
            # Compile list of keywords matched
            all_keywords = set()
            for exp in optimized_resume["experience"]:
                if "keywords_used" in exp:
                    all_keywords.update(exp["keywords_used"])
            
            for proj in optimized_resume["projects"]:
                if "keywords_used" in proj:
                    all_keywords.update(proj["keywords_used"])
                    
            optimized_resume["keywords_matched"] = list(all_keywords)
            
            # Generate ATS recommendations
            optimized_resume["ats_recommendations"] = await self._generate_ats_recommendations(
                optimized_resume,
                job_analysis
            )
            
            return optimized_resume
            
        except Exception as e:
            raise Exception(f"Resume optimization failed: {str(e)}")
    
    async def _optimize_experience(self,
                                  experience_items: List[Dict[str, Any]],
                                  job_analysis: Dict[str, Any],
                                  focus_areas: List[str],
                                  highlight_skills: List[str],
                                  tone: str) -> List[Dict[str, Any]]:
        """Optimize experience items based on job requirements"""
        optimized_items = []
        
        # Sort experience items by relevance to job description
        # This is a preliminary sort before detailed optimization
        experience_items = sorted(
            experience_items,
            key=lambda x: self._calculate_initial_relevance(x, job_analysis),
            reverse=True
        )
        
        # Process each experience item in parallel
        tasks = []
        for item in experience_items:
            tasks.append(self._optimize_experience_item(item, job_analysis, focus_areas, highlight_skills, tone))
        
        results = await asyncio.gather(*tasks)
        
        # Add successful results to optimized items
        for result in results:
            if result:
                optimized_items.append(result)
        
        # Sort final items by relevance score
        optimized_items = sorted(
            optimized_items, 
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )
        
        return optimized_items
    
    async def _optimize_experience_item(self,
                                       item: Dict[str, Any],
                                       job_analysis: Dict[str, Any],
                                       focus_areas: List[str],
                                       highlight_skills: List[str],
                                       tone: str) -> Dict[str, Any]:
        """Optimize a single experience item using LLM"""
        try:
            # Create a prompt for optimizing experience
            prompt_template = PromptTemplate(
                input_variables=["experience_item", "job_description", "job_requirements", 
                                "keywords", "focus_areas", "highlight_skills", "tone"],
                template="""You are an expert resume optimizer for {tone} {job_description}.
                
                EXPERIENCE ITEM TO OPTIMIZE:
                {experience_item}
                
                JOB DESCRIPTION: 
                {job_description}
                
                KEY JOB REQUIREMENTS:
                {job_requirements}
                
                IMPORTANT KEYWORDS TO INCLUDE:
                {keywords}
                
                FOCUS AREAS (if any):
                {focus_areas}
                
                SKILLS TO HIGHLIGHT (if any):
                {highlight_skills}
                
                OPTIMIZATION INSTRUCTIONS:
                1. Enhance the description to better align with job requirements while keeping factual information accurate
                2. Incorporate relevant keywords from the job description
                3. Use strong action verbs and quantify achievements when possible
                4. Format bullet points to highlight achievements and skills most relevant to the job
                5. Maintain the domain-specific terminology (CS/Data Science/AI) accurately
                6. Ensure descriptions emphasize impact and results
                
                {format_instructions}
                """
            )
            
            # Prepare the input
            experience_str = f"Role: {item.get('role', '')}\nCompany: {item.get('company', '')}\nDuration: {item.get('duration', '')}\nDescription: {item.get('description', '')}"
            
            # Job requirements as a bulleted list
            requirements_str = "\n".join([f"• {req}" for req in job_analysis.get("requirements", [])])
            
            # Keywords as a comma-separated list
            keywords_str = ", ".join(job_analysis.get("keywords", []))
            
            # Focus areas and highlight skills
            focus_areas_str = "\n".join([f"• {area}" for area in focus_areas]) if focus_areas else "None specified"
            highlight_skills_str = ", ".join(highlight_skills) if highlight_skills else "None specified"
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = await chain.arun(
                experience_item=experience_str,
                job_description=job_analysis.get("title", ""),
                job_requirements=requirements_str,
                keywords=keywords_str,
                focus_areas=focus_areas_str,
                highlight_skills=highlight_skills_str,
                tone=tone,
                format_instructions=self.format_instructions
            )
            
            # Parse the structured output
            parsed_output = self.output_parser.parse(result)
            
            # Convert the optimized item string back to a dictionary
            optimized_item = self._parse_optimized_item(parsed_output["optimized_item"], "experience")
            
            # Add metadata from the optimization process
            optimized_item["changes_made"] = parsed_output["changes_made"]
            optimized_item["relevance_score"] = int(parsed_output["relevance_score"])
            optimized_item["keywords_used"] = parsed_output["keywords_used"]
            
            return optimized_item
            
        except Exception as e:
            print(f"Error optimizing experience item: {str(e)}")
            return item  # Return original item if optimization fails
    
    async def _optimize_projects(self,
                                projects_items: List[Dict[str, Any]],
                                job_analysis: Dict[str, Any],
                                focus_areas: List[str],
                                highlight_skills: List[str],
                                tone: str) -> List[Dict[str, Any]]:
        """Optimize project items based on job requirements"""
        optimized_items = []
        
        # Sort project items by relevance to job description
        # This is a preliminary sort before detailed optimization
        projects_items = sorted(
            projects_items,
            key=lambda x: self._calculate_initial_relevance(x, job_analysis),
            reverse=True
        )
        
        # Process each project item in parallel
        tasks = []
        for item in projects_items:
            tasks.append(self._optimize_project_item(item, job_analysis, focus_areas, highlight_skills, tone))
        
        results = await asyncio.gather(*tasks)
        
        # Add successful results to optimized items
        for result in results:
            if result:
                optimized_items.append(result)
        
        # Sort final items by relevance score
        optimized_items = sorted(
            optimized_items, 
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )
        
        return optimized_items
    
    async def _optimize_project_item(self,
                                    item: Dict[str, Any],
                                    job_analysis: Dict[str, Any],
                                    focus_areas: List[str],
                                    highlight_skills: List[str],
                                    tone: str) -> Dict[str, Any]:
        """Optimize a single project item using LLM"""
        try:
            # Create a prompt for optimizing projects
            prompt_template = PromptTemplate(
                input_variables=["project_item", "job_description", "job_requirements", 
                                "keywords", "focus_areas", "highlight_skills", "tone"],
                template="""You are an expert resume optimizer for {tone} {job_description}.
                
                PROJECT ITEM TO OPTIMIZE:
                {project_item}
                
                JOB DESCRIPTION: 
                {job_description}
                
                KEY JOB REQUIREMENTS:
                {job_requirements}
                
                IMPORTANT KEYWORDS TO INCLUDE:
                {keywords}
                
                FOCUS AREAS (if any):
                {focus_areas}
                
                SKILLS TO HIGHLIGHT (if any):
                {highlight_skills}
                
                OPTIMIZATION INSTRUCTIONS:
                1. Enhance the description to better align with job requirements while keeping factual information accurate
                2. Incorporate relevant technical keywords from the job description
                3. Highlight technologies that match or are related to those in the job description
                4. Format bullet points to emphasize technical achievements, problem-solving, and methodologies
                5. Ensure descriptions emphasize technical complexity and solutions implemented
                6. Quantify impact when possible (e.g., efficiency improvements, user metrics)
                
                {format_instructions}
                """
            )
            
            # Prepare the input
            project_str = f"Title: {item.get('title', '')}\nTechnologies: {item.get('technologies', '')}\nDescription: {item.get('description', '')}\nAchievements: {item.get('achievements', '')}"
            
            # Job requirements as a bulleted list
            requirements_str = "\n".join([f"• {req}" for req in job_analysis.get("requirements", [])])
            
            # Keywords as a comma-separated list
            keywords_str = ", ".join(job_analysis.get("keywords", []))
            
            # Focus areas and highlight skills
            focus_areas_str = "\n".join([f"• {area}" for area in focus_areas]) if focus_areas else "None specified"
            highlight_skills_str = ", ".join(highlight_skills) if highlight_skills else "None specified"
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = await chain.arun(
                project_item=project_str,
                job_description=job_analysis.get("title", ""),
                job_requirements=requirements_str,
                keywords=keywords_str,
                focus_areas=focus_areas_str,
                highlight_skills=highlight_skills_str,
                tone=tone,
                format_instructions=self.format_instructions
            )
            
            # Parse the structured output
            parsed_output = self.output_parser.parse(result)
            
            # Convert the optimized item string back to a dictionary
            optimized_item = self._parse_optimized_item(parsed_output["optimized_item"], "project")
            
            # Add metadata from the optimization process
            optimized_item["changes_made"] = parsed_output["changes_made"]
            optimized_item["relevance_score"] = int(parsed_output["relevance_score"])
            optimized_item["keywords_used"] = parsed_output["keywords_used"]
            
            return optimized_item
            
        except Exception as e:
            print(f"Error optimizing project item: {str(e)}")
            return item  # Return original item if optimization fails
    
    async def _optimize_skills(self,
                              skills: Dict[str, List[str]],
                              job_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Optimize skills section based on job requirements"""
        optimized_skills = {}
        
        # Extract all skills from the job analysis
        job_skills = set(job_analysis.get("skills", []))
        job_technologies = set(job_analysis.get("technologies", []))
        job_keywords = set(job_analysis.get("keywords", []))
        
        all_job_related = job_skills.union(job_technologies).union(job_keywords)
        
        # For each skill category
        for category, skill_list in skills.items():
            # Reorder skills based on relevance to job
            ordered_skills = sorted(
                skill_list,
                key=lambda skill: self._skill_relevance_score(skill, all_job_related),
                reverse=True
            )
            
            optimized_skills[category] = ordered_skills
        
        # If there are important job skills missing, add a recommendation
        missing_important_skills = []
        for skill in job_skills:
            found = False
            for category, skill_list in optimized_skills.items():
                if any(skill.lower() in s.lower() for s in skill_list):
                    found = True
                    break
            
            if not found:
                missing_important_skills.append(skill)
        
        if missing_important_skills:
            optimized_skills["_missing_skills"] = missing_important_skills
        
        return optimized_skills
    
    async def _generate_optimization_summary(self,
                                           optimized_resume: Dict[str, Any],
                                           job_analysis: Dict[str, Any],
                                           job_title: str) -> str:
        """Generate a summary of the optimizations performed"""
        try:
            # Create a prompt for generating the summary
            prompt_template = PromptTemplate(
                input_variables=["job_title", "num_experience", "num_projects", "top_keywords"],
                template="""Generate a concise summary of how this resume has been optimized for the {job_title} position.
                
                Optimization details:
                - {num_experience} experience items optimized
                - {num_projects} project items optimized
                - Top keywords incorporated: {top_keywords}
                
                Write 2-3 sentences highlighting the key improvements and focus areas.
                """
            )
            
            # Get top keywords (up to 10)
            all_keywords = []
            for exp in optimized_resume["experience"]:
                if "keywords_used" in exp:
                    all_keywords.extend(exp["keywords_used"])
            
            for proj in optimized_resume["projects"]:
                if "keywords_used" in proj:
                    all_keywords.extend(proj["keywords_used"])
            
            # Count frequency and get top keywords
            keyword_counts = {}
            for kw in all_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_keywords_str = ", ".join([kw for kw, _ in top_keywords])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            summary = await chain.arun(
                job_title=job_title,
                num_experience=len(optimized_resume["experience"]),
                num_projects=len(optimized_resume["projects"]),
                top_keywords=top_keywords_str
            )
            
            return summary.strip()
            
        except Exception as e:
            return f"Resume optimized for {job_title} position with focus on relevant skills and experience."
    
    async def _generate_ats_recommendations(self,
                                          optimized_resume: Dict[str, Any],
                                          job_analysis: Dict[str, Any]) -> List[str]:
        """Generate ATS-specific recommendations"""
        recommendations = []
        
        # Check for important keywords missing from the resume
        missing_keywords = []
        resume_text = self._get_full_resume_text(optimized_resume)
        
        for keyword in job_analysis.get("keywords", []):
            # Check if the keyword appears in the resume
            if keyword.lower() not in resume_text.lower():
                missing_keywords.append(keyword)
        
        if missing_keywords:
            recommendations.append(
                f"Consider adding these keywords: {', '.join(missing_keywords[:5])}"
            )
        
        # Check for common ATS issues
        if "skills" not in optimized_resume or not optimized_resume["skills"]:
            recommendations.append(
                "Add a skills section with relevant technical skills from the job description"
            )
        
        # Check if experience items have quantifiable achievements
        quantifiable_count = 0
        for exp in optimized_resume["experience"]:
            if "description" in exp:
                if re.search(r'\d+%|\d+ times|increased|decreased|reduced|improved|by \d+', exp["description"], re.IGNORECASE):
                    quantifiable_count += 1
        
        if quantifiable_count < len(optimized_resume["experience"]) / 2:
            recommendations.append(
                "Add more quantifiable achievements to your experience descriptions"
            )
        
        # Add general ATS recommendations
        recommendations.append(
            "Use standard section headings (Experience, Education, Skills, Projects)"
        )
        
        recommendations.append(
            "Ensure the job title appears verbatim in your resume"
        )
        
        return recommendations
    
    def _calculate_initial_relevance(self, item: Dict[str, Any], job_analysis: Dict[str, Any]) -> float:
        """Calculate initial relevance score for sorting before optimization"""
        score = 0
        text = ""
        
        # Combine all text fields in the item
        for field, value in item.items():
            if isinstance(value, str):
                text += " " + value
        
        # Check for keyword matches
        for keyword in job_analysis.get("keywords", []):
            if keyword.lower() in text.lower():
                score += 1
        
        # Check for skill matches
        for skill in job_analysis.get("skills", []):
            if skill.lower() in text.lower():
                score += 2  # Skills are more important than general keywords
        
        # Check for technology matches
        for tech in job_analysis.get("technologies", []):
            if tech.lower() in text.lower():
                score += 2  # Technologies are also important
        
        return score
    
    def _skill_relevance_score(self, skill: str, job_terms: set) -> int:
        """Calculate relevance score for a skill based on job terms"""
        score = 0
        
        # Direct match
        if skill.lower() in [term.lower() for term in job_terms]:
            score += 10
            return score  # Early return for exact matches
        
        # Partial match
        for term in job_terms:
            if term.lower() in skill.lower() or skill.lower() in term.lower():
                score += 5
        
        return score
    
    def _parse_optimized_item(self, item_str: str, item_type: str) -> Dict[str, Any]:
        """Parse the optimized item string back into a structured dictionary"""
        result = {}
        
        # Define expected fields based on item type
        if item_type == "experience":
            fields = ["role", "company", "duration", "description"]
        else:  # project
            fields = ["title", "technologies", "description", "achievements"]
        
        # Try to parse as key-value pairs
        lines = item_str.strip().split("\n")
        current_field = None
        
        for line in lines:
            # Check if this line starts a new field
            field_match = False
            for field in fields:
                if line.lower().startswith(f"{field}:"):
                    current_field = field
                    value = line[len(field)+1:].strip()
                    result[field] = value
                    field_match = True
                    break
            
            # If not a field header, append to current field
            if not field_match and current_field:
                result[current_field] += "\n" + line.strip()
        
        # If parsing failed, try a more flexible approach
        if not result:
            for field in fields:
                pattern = re.compile(f"{field}:(.+?)(?={fields[0]}:|{fields[1]}:|$)", re.IGNORECASE | re.DOTALL)
                match = pattern.search(item_str)
                if match:
                    result[field] = match.group(1).strip()
        
        return result
    
    def _get_full_resume_text(self, resume: Dict[str, Any]) -> str:
        """Get the full text of the resume for ATS analysis"""
        text = ""
        
        # Experience section
        for exp in resume.get("experience", []):
            for key, value in exp.items():
                if isinstance(value, str) and key not in ["changes_made", "keywords_used"]:
                    text += " " + value
        
        # Projects section
        for proj in resume.get("projects", []):
            for key, value in proj.items():
                if isinstance(value, str) and key not in ["changes_made", "keywords_used"]:
                    text += " " + value
        
        # Skills section
        for category, skills in resume.get("skills", {}).items():
            if category != "_missing_skills":
                text += " " + category
                for skill in skills:
                    text += " " + skill
        
        # Education section
        for edu in resume.get("education", []):
            if isinstance(edu, dict):
                for key, value in edu.items():
                    if isinstance(value, str):
                        text += " " + value
            elif isinstance(edu, str):
                text += " " + edu
        
        return text
