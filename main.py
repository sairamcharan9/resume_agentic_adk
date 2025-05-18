from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import json
import tempfile
from pathlib import Path
import asyncio
import aiofiles
import uuid
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import components from our modules
from src.parser.latex_parser import LaTeXResumeParser
from src.optimizer.resume_optimizer import ResumeOptimizer
from src.latex_generator.generator import LaTeXGenerator
from src.ats.ats_analyzer import ATSAnalyzer
from src.feedback.feedback_processor import FeedbackProcessor
from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Optimizer API",
    description="Optimize your resume for CS, Data Science, and AI/ML positions based on job descriptions",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create temporary directory for file storage
temp_dir = Path("temp")
temp_dir.mkdir(exist_ok=True)

# Pydantic models
class JobDescription(BaseModel):
    title: str
    description: str
    requirements: List[str]
    company: Optional[str] = None
    location: Optional[str] = None
    domain: Optional[str] = "computer_science"  # Options: computer_science, data_science, ai_ml

class SpecialInstructions(BaseModel):
    focus_areas: Optional[List[str]] = None
    highlight_skills: Optional[List[str]] = None
    tone: Optional[str] = "professional"  # Options: professional, technical, research
    additional_notes: Optional[str] = None

class OptimizationRequest(BaseModel):
    job_description: JobDescription
    special_instructions: Optional[SpecialInstructions] = None
    feedback_id: Optional[str] = None  # For feedback loop

class OptimizationResponse(BaseModel):
    resume_id: str
    ats_score: float
    keyword_match_score: float
    optimization_summary: str
    key_improvements: List[str]
    download_url: str
    feedback_url: str

class FeedbackSubmission(BaseModel):
    resume_id: str
    effectiveness_rating: int  # 1-5
    quality_rating: int  # 1-5
    comments: Optional[str] = None
    interview_result: Optional[str] = None  # invited, rejected, etc.

# Routes
@app.get("/")
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize_resume(
    background_tasks: BackgroundTasks,
    job_description: str = Form(...),
    resume_file: UploadFile = File(...),
    model_provider: str = Form('huggingface'),  # Default to Hugging Face
    openai_model: Optional[str] = Form(None),
    openrouter_model: Optional[str] = Form(None),
    huggingface_model: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    special_instructions: Optional[str] = Form(None)
):
    """
    Optimize a LaTeX resume for a specific job description
    
    - Parses the uploaded LaTeX resume
    - Analyzes the job description for key requirements
    - Optimizes the resume content to match job requirements
    - Generates a new LaTeX resume file
    - Analyzes ATS compatibility
    - Returns optimization stats and download link
    """
    try:
        # Generate a unique ID for this optimization
        resume_id = f"ro_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
        
        # Parse input data
        job_desc_data = json.loads(job_description)
        job_desc_obj = JobDescription(**job_desc_data)
        
        special_instr_obj = None
        if special_instructions:
            special_instr_data = json.loads(special_instructions)
            special_instr_obj = SpecialInstructions(**special_instr_data)
        
        # Save the uploaded file
        resume_path = temp_dir / f"{resume_id}_original.tex"
        async with aiofiles.open(resume_path, 'wb') as out_file:
            content = await resume_file.read()
            await out_file.write(content)
        
        # Configure AI model based on user selection
        from src.utils.ai_integration import AIManager, ModelProvider
        from src.utils.model_config import configure_openrouter
        
        # Set up the selected model
        selected_model = None
        if model_provider == 'openai' and openai_model:
            selected_model = openai_model
            if api_key:  # Set OpenAI API key if provided
                os.environ["OPENAI_API_KEY"] = api_key
        elif model_provider == 'openrouter' and openrouter_model:
            selected_model = openrouter_model
            if api_key:  # Set OpenRouter API key if provided
                configure_openrouter(api_key)
        elif model_provider == 'huggingface' and huggingface_model:
            selected_model = huggingface_model
        
        # Create AI manager with the selected configuration
        ai_manager = AIManager(
            provider=model_provider,
            model_name=selected_model,
            temperature=0.3
        )
        
        # Initialize components
        parser = LaTeXResumeParser()
        optimizer = ResumeOptimizer(ai_manager=ai_manager)
        latex_gen = LaTeXGenerator()
        ats_analyzer = ATSAnalyzer()
        
        # Parse resume
        parsed_resume = await parser.parse(str(resume_path))
        
        # Optimize resume
        optimized_data = await optimizer.optimize(
            parsed_resume,
            job_desc_obj,
            special_instructions=special_instr_obj
        )
        
        # Generate LaTeX
        output_path = temp_dir / f"{resume_id}_optimized.tex"
        await latex_gen.generate(optimized_data, output_path)
        
        # Analyze ATS compatibility
        ats_results = await ats_analyzer.analyze(output_path, job_desc_obj)
        
        # Schedule cleanup in the background
        background_tasks.add_task(cleanup_files, resume_id, hours=24)
        
        # Create response
        response = OptimizationResponse(
            resume_id=resume_id,
            ats_score=ats_results["ats_score"],
            keyword_match_score=ats_results["keyword_match_score"],
            optimization_summary=optimized_data["summary"],
            key_improvements=optimized_data["improvements"],
            download_url=f"/api/download/{resume_id}",
            feedback_url=f"/api/feedback/{resume_id}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error during optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.get("/api/download/{resume_id}")
async def download_resume(resume_id: str):
    """Download the optimized resume file"""
    file_path = temp_dir / f"{resume_id}_optimized.tex"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Optimized resume not found")
    
    return FileResponse(
        path=file_path,
        filename=f"optimized_resume_{resume_id}.tex",
        media_type="application/x-tex"
    )

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackSubmission):
    """Submit feedback for a resume optimization"""
    processor = FeedbackProcessor()
    await processor.process_feedback(feedback)
    return {"status": "Feedback received", "message": "Thank you for your feedback!"}

@app.get("/api/templates")
async def list_templates():
    """List available resume templates"""
    template_dir = Path("templates/latex")
    templates = [f.stem for f in template_dir.glob("*.tex")]
    return {"templates": templates}

async def cleanup_files(resume_id: str, hours: int = 24):
    """Clean up temporary files after a specified time"""
    await asyncio.sleep(hours * 3600)
    
    for file_pattern in [f"{resume_id}_original.tex", f"{resume_id}_optimized.tex"]:
        file_path = temp_dir / file_pattern
        if file_path.exists():
            file_path.unlink()
    
    logger.info(f"Cleaned up files for resume {resume_id}")

# Create placeholder files for imports to work
for module_dir in ["parser", "optimizer", "latex_generator", "ats", "feedback", "utils"]:
    os.makedirs(f"src/{module_dir}", exist_ok=True)
    init_file = Path(f"src/{module_dir}/__init__.py")
    if not init_file.exists():
        init_file.touch()

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
