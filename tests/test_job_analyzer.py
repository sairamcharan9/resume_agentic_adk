"""
Tests for the job description analyzer module.

This module contains unit tests for the JobDescriptionAnalyzer class.
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock
import json
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.job_analyzer import JobDescriptionAnalyzer

class TestJobDescriptionAnalyzer(unittest.TestCase):
    """Test cases for the JobDescriptionAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock OPENAI_API_KEY environment variable
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "fake-api-key"})
        self.env_patcher.start()
        
        # Mock the LLM to prevent actual API calls
        self.llm_patcher = patch('src.utils.job_analyzer.ChatOpenAI')
        self.mock_llm = self.llm_patcher.start()
        
        # Create an instance of the analyzer
        self.analyzer = JobDescriptionAnalyzer()
        
        # Sample job description and requirements
        self.job_title = "Senior Software Engineer"
        self.job_description = """
        We are looking for a Senior Software Engineer to join our team.
        
        Responsibilities:
        - Design and develop high-quality software solutions
        - Collaborate with cross-functional teams
        - Mentor junior developers
        - Implement best practices for code quality and security
        - Participate in code reviews and technical discussions
        
        Requirements:
        - 5+ years of experience in software development
        - Strong knowledge of Python and JavaScript
        - Experience with web frameworks like Django or Flask
        - Familiarity with cloud platforms (AWS/Azure)
        - Good understanding of database design and optimization
        """
        
        self.requirements = [
            "5+ years of experience in software development",
            "Strong knowledge of Python and JavaScript",
            "Experience with web frameworks like Django or Flask",
            "Familiarity with cloud platforms (AWS/Azure)",
            "Good understanding of database design and optimization"
        ]
        
        self.expected_output = {
            "title": "Senior Software Engineer",
            "requirements": [
                "5+ years of experience in software development",
                "Strong knowledge of Python and JavaScript",
                "Experience with web frameworks (Django/Flask)",
                "Familiarity with cloud platforms (AWS/Azure)",
                "Database design and optimization knowledge"
            ],
            "skills": [
                "Python",
                "JavaScript",
                "Django",
                "Flask",
                "AWS",
                "Azure",
                "Database design",
                "Mentoring",
                "Code review"
            ],
            "technologies": [
                "Python",
                "JavaScript",
                "Django",
                "Flask",
                "AWS",
                "Azure"
            ],
            "keywords": [
                "senior",
                "software engineer",
                "python",
                "javascript",
                "django",
                "flask",
                "aws",
                "azure",
                "database",
                "5+ years"
            ],
            "experience_level": "senior",
            "domain_focus": "backend development"
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()
        self.llm_patcher.stop()
    
    def test_extract_quick_keywords(self):
        """Test quick keyword extraction without using LLM."""
        # Test for computer_science domain
        keywords = self.analyzer.extract_quick_keywords(
            self.job_description, 
            domain="computer_science"
        )
        
        # Check if essential keywords are extracted
        expected_keywords = ["python", "javascript", "software developer", "5+ years experience"]
        for keyword in expected_keywords:
            self.assertTrue(
                any(keyword in kw.lower() for kw in keywords),
                f"Expected keyword '{keyword}' not found in extracted keywords: {keywords}"
            )
    
    @patch('src.utils.job_analyzer.LLMChain')
    def test_analyze(self, mock_llm_chain):
        """Test the analyze method with mocked LLM chain."""
        # Set up the mock
        mock_chain_instance = MagicMock()
        mock_llm_chain.return_value = mock_chain_instance
        mock_chain_instance.arun.return_value = json.dumps(self.expected_output)
        
        # Set up the output parser mock
        self.analyzer.output_parser = MagicMock()
        self.analyzer.output_parser.parse.return_value = self.expected_output
        
        # Run the test
        result = asyncio.run(
            self.analyzer.analyze(
                self.job_title,
                self.job_description,
                self.requirements
            )
        )
        
        # Check the results
        self.assertEqual(result["title"], "Senior Software Engineer")
        self.assertEqual(result["experience_level"], "senior")
        self.assertTrue(isinstance(result["requirements"], list))
        self.assertTrue(isinstance(result["skills"], list))
        self.assertTrue(isinstance(result["technologies"], list))
        self.assertTrue(isinstance(result["keywords"], list))
        
        # Verify that LLMChain.arun was called with expected arguments
        mock_chain_instance.arun.assert_called_once()
        call_args = mock_chain_instance.arun.call_args[1]
        self.assertEqual(call_args["title"], self.job_title)
        self.assertEqual(call_args["description"], self.job_description)
        self.assertTrue("requirements" in call_args)
        self.assertEqual(call_args["domain"], "computer_science")  # Default domain

if __name__ == "__main__":
    unittest.main()
