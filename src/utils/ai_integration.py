"""
AI Integration Module

This module handles integration with various AI models for resume optimization,
providing prompts, chains, and model management. Supports both commercial APIs
like OpenAI and free open-source models via Hugging Face.
"""

import os
import json
import enum
from typing import Dict, List, Any, Optional, Union, Literal
from pathlib import Path
import asyncio
import logging

# Local imports
from src.utils.model_config import configure_openrouter

# LangChain imports
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.docstore.document import Document as LangchainDocument
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_community.retrievers import BM25Retriever

# Model imports
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from langchain_community.llms import LlamaCpp
from langchain_community.embeddings import HuggingFaceEmbeddings

# Optional imports for Hugging Face integration
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("Hugging Face transformers library not available. Falling back to OpenAI if configured.")

# Optional imports for llama.cpp integration
try:
    from llama_cpp import Llama
    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False
    logging.warning("llama-cpp-python not available. Cannot use local Llama models.")

class ModelProvider(str, enum.Enum):
    """Supported AI model providers"""
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"
    LLAMACPP = "llamacpp"

class AIManager:
    """
    Manages AI models, prompts, and chains for resume optimization.
    Supports multiple model providers including OpenAI, Hugging Face, and local models.
    """
    
    # Default models for different providers
    DEFAULT_MODELS = {
        ModelProvider.OPENAI: "gpt-3.5-turbo",
        ModelProvider.OPENROUTER: "anthropic/claude-3-opus",  # High quality but costlier
        ModelProvider.HUGGINGFACE: "mistralai/Mistral-7B-Instruct-v0.2",
        ModelProvider.LLAMACPP: "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    }
    
    def __init__(self, 
                provider: Union[str, ModelProvider] = ModelProvider.HUGGINGFACE, 
                model_name: Optional[str] = None, 
                temperature: float = 0.2,
                device: str = "cpu",
                model_kwargs: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI Manager with specified provider, model and settings.
        
        Args:
            provider: The model provider to use ("openai", "huggingface", or "llamacpp")
            model_name: The model to use (provider-specific). If None, uses default for provider
            temperature: Model temperature (0.0 to 1.0), lower for more consistent outputs
            device: Device to run the model on ("cpu" or "cuda" for GPU support)
            model_kwargs: Additional keyword arguments to pass to the model
        """
        if isinstance(provider, str):
            try:
                provider = ModelProvider(provider.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid provider '{provider}'. Must be one of: {', '.join([p.value for p in ModelProvider])}"
                )
        
        self.provider = provider
        self.temperature = temperature
        self.device = device
        self.model_kwargs = model_kwargs or {}
        
        # Use default model if none specified
        if model_name is None:
            model_name = self.DEFAULT_MODELS[provider]
        
        self.model_name = model_name
        
        # Initialize the model based on provider
        self._initialize_model()
        
        # Initialize text splitter for long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Load prompts
        self._initialize_prompts()
    
    def _initialize_model(self):
        """
        Initialize the appropriate model based on the selected provider.
        """
        if self.provider == ModelProvider.OPENAI:
            self._initialize_openai_model()
        elif self.provider == ModelProvider.OPENROUTER:
            self._initialize_openrouter_model()
        elif self.provider == ModelProvider.HUGGINGFACE:
            self._initialize_huggingface_model()
        elif self.provider == ModelProvider.LLAMACPP:
            self._initialize_llamacpp_model()
        else:
            raise ValueError(f"Unsupported model provider: {self.provider}")
            
    def _initialize_openai_model(self):
        """
        Initialize an OpenAI model.
        """
        # Check if API key is available
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key is not set. Set the OPENAI_API_KEY environment variable.")
            
        # Initialize the model
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            **self.model_kwargs
        )
        
    def _initialize_openrouter_model(self):
        """
        Initialize an OpenRouter model that provides access to various top-tier AI models
        through a unified API (Claude, Anthropic, Meta's models, etc).
        """
        # Check if API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            raise ValueError("OpenRouter API key is not set. Set the OPENROUTER_API_KEY environment variable.")
            
        # Initialize the model with OpenRouter base URL
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            # OpenRouter specific parameters
            model_kwargs={
                "HTTP_REFERER": "https://resume-optimizer.local",  # Required by OpenRouter
                "x-title": "Resume Optimizer"  # Optional: identify your app
            },
            **self.model_kwargs
        )
        
    def _initialize_huggingface_model(self):
        """
        Initialize a Hugging Face model.
        """
        if not HUGGINGFACE_AVAILABLE:
            raise ImportError(
                "Hugging Face transformers library is not installed. "
                "Install it with 'pip install transformers torch' to use Hugging Face models."
            )
            
        try:
            # Load tokenizer and model with reduced precision for efficiency
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # For larger models, 8-bit quantization to reduce VRAM usage
            model_kwargs = {"device_map": self.device}
            if "8bit" in self.model_kwargs and self.model_kwargs["8bit"]:
                model_kwargs["load_in_8bit"] = True
            
            # Load model with appropriate settings
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Create text generation pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=self.temperature,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            # Create LangChain interface for the model
            self.llm = HuggingFacePipeline(pipeline=pipe)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Hugging Face model: {e}") from e
            
    def _initialize_llamacpp_model(self):
        """
        Initialize a llama.cpp model for efficient local inference.
        """
        if not LLAMACPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install it with 'pip install llama-cpp-python' to use local Llama models."
            )
            
        try:
            # Default parameters that work well for most systems
            llamacpp_kwargs = {
                "n_ctx": 4096,  # Context window size
                "n_batch": 512,  # Batch size for more efficient processing
                "n_threads": max(1, os.cpu_count() // 2),  # Use half of available CPU cores
                "n_gpu_layers": 0  # By default don't use GPU layers
            }
            
            # Override defaults with user-provided settings
            if self.model_kwargs:
                llamacpp_kwargs.update(self.model_kwargs)
                
            # Create LangChain wrapper for the model
            self.llm = LlamaCpp(
                model_path=self.model_name,
                temperature=self.temperature,
                max_tokens=512,
                top_p=0.95,
                verbose=False,
                **llamacpp_kwargs
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize llama.cpp model: {e}") from e
    
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

def get_available_models():
    """
    Return the available AI models based on installed packages and configuration.
    
    Returns:
        Dict[str, List[str]]: Dictionary of available models by provider
    """
    available = {}
    
    # Configure OpenRouter with the API key
    configure_openrouter("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")
    
    # OpenRouter models (diverse selection of powerful models)
    if os.getenv("OPENROUTER_API_KEY"):
        available[ModelProvider.OPENROUTER] = [
            "anthropic/claude-3-opus",    # Highest quality, more expensive
            "anthropic/claude-3-sonnet",  # Balanced quality and cost
            "anthropic/claude-3-haiku",   # Fastest, most economical
            "meta-llama/llama-3-70b-instruct", # Meta's largest model
            "google/gemini-pro",         # Google's model
            "google/gemini-2.0-flash-exp:free", # Free access to Gemini through OpenRouter
            "mistralai/mistral-large"     # Mistral's commercial model
        ]
    
    # OpenAI models
    if os.getenv("OPENAI_API_KEY"):
        available[ModelProvider.OPENAI] = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo"
        ]
    
    # Hugging Face models
    if HUGGINGFACE_AVAILABLE:
        available[ModelProvider.HUGGINGFACE] = [
            "mistralai/Mistral-7B-Instruct-v0.2",  # Good general purpose model
            "google/flan-t5-large",               # Smaller, more efficient
            "meta-llama/Llama-2-7b-chat-hf",      # If authenticated with HF
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0" # Tiny model for testing
        ]
    
    # Local Llama.cpp models
    if LLAMACPP_AVAILABLE:
        # Check for model files in a 'models' directory
        models_dir = Path("models")
        if models_dir.exists() and models_dir.is_dir():
            local_models = [str(p.relative_to('.')) for p in models_dir.glob("*.gguf")]
            if local_models:
                available[ModelProvider.LLAMACPP] = local_models
    
    return available

def create_model_factory(provider_preference: List[ModelProvider] = None):
    """
    Create an AI model based on available providers and preference order.
    
    Args:
        provider_preference: List of providers in order of preference
                            Default: [OPENROUTER, HUGGINGFACE, LLAMACPP, OPENAI]  
    
    Returns:
        AIManager: Initialized AI model with the first available provider
    """
    if provider_preference is None:
        # If OpenRouter API key is available, prioritize it, otherwise use free models first
        if os.getenv("OPENROUTER_API_KEY"):
            provider_preference = [ModelProvider.OPENROUTER, ModelProvider.HUGGINGFACE, ModelProvider.LLAMACPP, ModelProvider.OPENAI]
        else:
            # Default to free models first, then paid models
            provider_preference = [ModelProvider.HUGGINGFACE, ModelProvider.LLAMACPP, ModelProvider.OPENAI]
    
    available_models = get_available_models()
    
    # Try providers in order of preference
    for provider in provider_preference:
        if provider in available_models and available_models[provider]:
            try:
                # Use first model from the available models for this provider
                model_name = available_models[provider][0]
                logging.info(f"Using {provider} model: {model_name}")
                
                # For LLAMACPP, ensure full path if just model name
                if provider == ModelProvider.LLAMACPP and not Path(model_name).is_absolute():
                    if not model_name.startswith('models/'):
                        model_name = f"models/{model_name}"
                
                return AIManager(provider=provider, model_name=model_name)
            except Exception as e:
                logging.warning(f"Failed to initialize {provider} model: {str(e)}")
                continue
    
    raise ValueError("No available AI models found. Please install at least one of: transformers+torch, llama-cpp-python, or set OPENAI_API_KEY.")

def main():
    """Test the AI integration module with different model providers."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Resume Optimizer - AI Integration Test")
    print("====================================")
    
    # Get available models
    available_models = get_available_models()
    if not available_models:
        print("No AI models available. Please install transformers+torch, llama-cpp-python, or set OPENAI_API_KEY.")
        return
    
    print("\nAvailable Model Providers:")
    for provider, models in available_models.items():
        print(f"- {provider}: {len(models)} model(s) available")
        for model in models:
            print(f"  - {model}")
    
    try:
        # Create AI model with default provider preference
        ai_manager = create_model_factory()
        print(f"\nUsing model provider: {ai_manager.provider}")
        print(f"Model: {ai_manager.model_name}")
        
        # Sample data for optimization
        section_type = "Work Experience"
        original_content = (
            "Software Engineer at XYZ Corp (2020-Present)\n"
            "- Developed web applications using React and Node.js\n"
            "- Implemented database solutions using MongoDB\n"
            "- Worked with a team of 5 developers on various projects\n"
        )
        job_requirements = (
            "We're looking for a Python Developer with Django experience.\n"
            "Must have 3+ years of experience with Python web development.\n"
            "Experience with PostgreSQL and RESTful API design is required.\n"
            "Knowledge of cloud platforms like AWS is a plus.\n"
        )
        keywords = ["Python", "Django", "PostgreSQL", "RESTful API", "AWS"]
        
        print("\nOptimizing resume section...")
        result = asyncio.run(ai_manager.optimize_resume_section(
            section_type, original_content, job_requirements, keywords
        ))
        
        print("\nOriginal Content:")
        print(original_content)
        print("\nOptimized Content:")
        print(result)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
