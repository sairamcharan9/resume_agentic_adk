"""
Tests for the AI integration module.

This module contains unit tests for the AIManager class.
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.ai_integration import AIManager

class TestAIManager(unittest.TestCase):
    """Test cases for the AIManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock OPENAI_API_KEY environment variable
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "fake-api-key"})
        self.env_patcher.start()
        
        # Mock ChatOpenAI to prevent actual API calls
        self.chat_openai_patcher = patch('src.utils.ai_integration.ChatOpenAI')
        self.mock_chat_openai = self.chat_openai_patcher.start()
        
        # Mock LLMChain
        self.llm_chain_patcher = patch('src.utils.ai_integration.LLMChain')
        self.mock_llm_chain = self.llm_chain_patcher.start()
        
        # Create a mock chain instance
        self.mock_chain_instance = MagicMock()
        self.mock_llm_chain.return_value = self.mock_chain_instance
        self.mock_chain_instance.arun.return_value = "Optimized content result"
        
        # Create an instance of AIManager
        self.ai_manager = AIManager()
        
        # Sample data for tests
        self.sample_section = "I am a software engineer with 5 years of experience in Python development."
        self.sample_job_requirements = "Looking for a senior Python developer with Django experience."
        self.sample_keywords = ["Python", "Django", "senior", "web development"]
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()
        self.chat_openai_patcher.stop()
        self.llm_chain_patcher.stop()
    
    def test_initialization(self):
        """Test AIManager initialization."""
        # Verify that ChatOpenAI was called with expected parameters
        self.mock_chat_openai.assert_called_once()
        
        # Verify that prompts were initialized
        self.assertTrue(hasattr(self.ai_manager, 'section_optimization_template'))
        self.assertTrue(hasattr(self.ai_manager, 'education_optimization_template'))
        self.assertTrue(hasattr(self.ai_manager, 'experience_optimization_template'))
        self.assertTrue(hasattr(self.ai_manager, 'skills_optimization_template'))
        self.assertTrue(hasattr(self.ai_manager, 'summary_optimization_template'))
    
    def test_api_key_requirement(self):
        """Test that API key is required."""
        # Remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            # Verify that initialization raises an error without API key
            with self.assertRaises(ValueError):
                AIManager()
    
    def test_optimize_resume_section(self):
        """Test resume section optimization."""
        # Run the method and get result
        result = asyncio.run(
            self.ai_manager.optimize_resume_section(
                "Summary",
                self.sample_section,
                self.sample_job_requirements,
                self.sample_keywords
            )
        )
        
        # Verify that LLMChain was initialized with the correct prompt
        self.mock_llm_chain.assert_called_once_with(
            llm=self.ai_manager.llm,
            prompt=self.ai_manager.section_optimization_template
        )
        
        # Verify that arun was called with the expected arguments
        self.mock_chain_instance.arun.assert_called_once()
        args = self.mock_chain_instance.arun.call_args[1]
        self.assertEqual(args["section_type"], "Summary")
        self.assertEqual(args["original_content"], self.sample_section)
        self.assertEqual(args["job_requirements"], self.sample_job_requirements)
        self.assertEqual(args["keywords"], ", ".join(self.sample_keywords))
        
        # Verify the result
        self.assertEqual(result, "Optimized content result")
    
    @patch('src.utils.ai_integration.StructuredOutputParser')
    def test_create_skill_match_analysis(self, mock_parser):
        """Test skill match analysis."""
        # Configure mock parser
        mock_parser_instance = MagicMock()
        mock_parser.from_response_schemas.return_value = mock_parser_instance
        mock_parser_instance.get_format_instructions.return_value = "format instructions"
        mock_parser_instance.parse.return_value = {
            "matching_skills": ["Python", "Django"],
            "missing_skills": ["React", "AWS"],
            "skill_match_percentage": 60,
            "recommendations": ["Add React to your skills"]
        }
        
        # Sample data
        resume_skills = ["Python", "Django", "Flask", "JavaScript"]
        job_skills = ["Python", "Django", "React", "AWS"]
        
        # Run the method
        result = asyncio.run(
            self.ai_manager.create_skill_match_analysis(
                resume_skills,
                job_skills,
                "computer_science"
            )
        )
        
        # Verify chain creation and execution
        self.mock_llm_chain.assert_called()
        self.mock_chain_instance.arun.assert_called_once()
        
        # Verify arguments passed to chain
        args = self.mock_chain_instance.arun.call_args[1]
        self.assertEqual(args["resume_skills"], ", ".join(resume_skills))
        self.assertEqual(args["job_skills"], ", ".join(job_skills))
        self.assertEqual(args["domain"], "computer_science")
        
        # Verify result parsing
        mock_parser_instance.parse.assert_called_once()
        
        # Verify result structure
        self.assertEqual(result["matching_skills"], ["Python", "Django"])
        self.assertEqual(result["missing_skills"], ["React", "AWS"])
        self.assertEqual(result["skill_match_percentage"], 60)
        self.assertEqual(result["recommendations"], ["Add React to your skills"])
    
    @patch('src.utils.ai_integration.StructuredOutputParser')
    def test_generate_ats_recommendations(self, mock_parser):
        """Test ATS recommendations generation."""
        # Configure mock parser
        mock_parser_instance = MagicMock()
        mock_parser.from_response_schemas.return_value = mock_parser_instance
        mock_parser_instance.get_format_instructions.return_value = "format instructions"
        mock_parser_instance.parse.return_value = {
            "ats_score": 75,
            "keyword_match": 80,
            "format_score": 70,
            "found_keywords": ["Python", "Developer"],
            "missing_keywords": ["Django", "AWS"],
            "format_issues": ["Complex formatting might confuse ATS"],
            "recommendations": ["Add more keywords", "Simplify formatting"]
        }
        
        # Sample data
        resume_text = "Python Developer with 5 years of experience"
        job_description = "Senior Python Developer with Django and AWS experience"
        
        # Run the method
        result = asyncio.run(
            self.ai_manager.generate_ats_recommendations(
                resume_text,
                job_description,
                "computer_science"
            )
        )
        
        # Verify chain creation and execution
        self.mock_llm_chain.assert_called()
        self.mock_chain_instance.arun.assert_called_once()
        
        # Verify arguments passed to chain
        args = self.mock_chain_instance.arun.call_args[1]
        self.assertEqual(args["resume_text"], resume_text)
        self.assertEqual(args["job_description"], job_description)
        self.assertEqual(args["domain"], "computer_science")
        
        # Verify result parsing
        mock_parser_instance.parse.assert_called_once()
        
        # Verify result structure
        self.assertEqual(result["ats_score"], 75)
        self.assertEqual(result["keyword_match"], 80)
        self.assertEqual(result["format_score"], 70)
        self.assertEqual(result["found_keywords"], ["Python", "Developer"])
        self.assertEqual(result["missing_keywords"], ["Django", "AWS"])
        self.assertEqual(result["format_issues"], ["Complex formatting might confuse ATS"])
        self.assertEqual(result["recommendations"], ["Add more keywords", "Simplify formatting"])
    
    def test_generate_impact_statements(self):
        """Test impact statement generation."""
        # Sample data
        experiences = [
            "Developed a web application using Python and Django",
            "Managed a team of 3 developers"
        ]
        skills = ["Python", "Django", "Team Management"]
        job_requirements = "Looking for a technical lead with Python experience"
        
        # Run the method
        result = asyncio.run(
            self.ai_manager.generate_impact_statements(
                experiences,
                skills,
                job_requirements,
                "computer_science"
            )
        )
        
        # Configure mock return value after first call to simulate splitting returned string into lines
        self.mock_chain_instance.arun.return_value = "Enhanced impact statement 1\nEnhanced impact statement 2"
        
        # Run the method again with the updated mock
        result = asyncio.run(
            self.ai_manager.generate_impact_statements(
                experiences,
                skills,
                job_requirements,
                "computer_science"
            )
        )
        
        # Verify chain creation and execution
        self.mock_llm_chain.assert_called()
        self.mock_chain_instance.arun.assert_called()
        
        # Verify arguments passed to chain
        args = self.mock_chain_instance.arun.call_args[1]
        self.assertEqual(args["experiences"], "\n".join(experiences))
        self.assertEqual(args["skills"], ", ".join(skills))
        self.assertEqual(args["job_requirements"], job_requirements)
        self.assertEqual(args["domain"], "computer_science")
        
        # Verify result is a list of statements
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Enhanced impact statement 1")
        self.assertEqual(result[1], "Enhanced impact statement 2")

if __name__ == "__main__":
    unittest.main()
