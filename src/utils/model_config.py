"""
Model Configuration Utility

This module provides utilities for configuring and selecting AI models
for the Resume Optimizer application.
"""

import os
from pathlib import Path
from typing import Optional, Dict, List

def configure_openrouter(api_key: Optional[str] = None) -> bool:
    """
    Configure OpenRouter API key either from parameter or environment variables
    
    Args:
        api_key: Optional API key to use directly
        
    Returns:
        bool: True if API key was set successfully
    """
    # First priority: directly provided API key
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key
        return True
    
    # Second priority: API key in .env file (already loaded by python-dotenv)
    if os.getenv("OPENROUTER_API_KEY"):
        return True
    
    # If no API key is available
    return False

def get_model_preference(use_openrouter: bool = True) -> List[str]:
    """
    Returns the preferred order of model providers based on configuration
    
    Args:
        use_openrouter: Whether to prioritize OpenRouter if available
        
    Returns:
        List[str]: Provider preference order
    """
    # Default preference with OpenRouter first if key is available
    if use_openrouter and os.getenv("OPENROUTER_API_KEY"):
        return ["openrouter", "huggingface", "llamacpp", "openai"]
    
    # Default to free models first, then paid models
    return ["huggingface", "llamacpp", "openai"]

def get_recommended_model(provider: str) -> str:
    """
    Get the recommended model for a given provider
    
    Args:
        provider: Model provider name
        
    Returns:
        str: Recommended model name
    """
    recommendations = {
        "openrouter": "google/gemini-2.0-flash-exp:free",  # Free high-quality model
        "openai": "gpt-3.5-turbo",                       # Most widely used
        "huggingface": "mistralai/Mistral-7B-Instruct-v0.2",
        "llamacpp": "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    }
    
    return recommendations.get(provider, "")
