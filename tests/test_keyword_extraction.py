"""
Tests for the keyword extraction module.

This module contains unit tests for the KeywordExtractor class.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any, Tuple

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.keyword_extraction import KeywordExtractor

class TestKeywordExtractor(unittest.TestCase):
    """Test cases for the KeywordExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create an instance of the extractor
        self.extractor = KeywordExtractor()
        
        # Sample job description
        self.job_description = """
        Senior Software Engineer - Python

        Company XYZ is looking for a Senior Software Engineer with expertise in Python 
        to join our growing team. The ideal candidate will have 5+ years of experience 
        in software development and a strong background in web frameworks like Django and Flask.

        Key Requirements:
        - 5+ years of experience in Python development
        - Expert knowledge of Django or Flask
        - Experience with RESTful API design and implementation
        - Proficiency in JavaScript, HTML, and CSS
        - Familiarity with Docker, Kubernetes, and CI/CD pipelines
        - Experience with AWS cloud services
        - Bachelor's degree in Computer Science or equivalent experience
        - Strong problem-solving and communication skills

        Responsibilities:
        - Design and develop scalable, high-performance applications
        - Write clean, maintainable, and well-tested code
        - Contribute to architectural decisions and technical direction
        - Mentor junior developers and conduct code reviews
        - Collaborate with cross-functional teams to deliver features
        - Implement best practices for code quality and security
        """
    
    def test_preprocess_text(self):
        """Test text preprocessing functionality."""
        sample_text = "Python Developer with 5+ years of Experience in Django & Flask!"
        processed_text = self.extractor.preprocess_text(sample_text)
        
        # Verify lowercase conversion
        self.assertFalse(any(c.isupper() for c in processed_text))
        
        # Verify special character removal
        self.assertFalse(any(c in processed_text for c in "&!"))
        
        # Verify stop words are removed
        self.assertFalse(" with " in processed_text)
        self.assertFalse(" of " in processed_text)
        self.assertFalse(" in " in processed_text)
    
    def test_extract_technical_skills(self):
        """Test extraction of technical skills from text."""
        skills = self.extractor.extract_technical_skills(self.job_description, domain="computer_science")
        
        # Ensure all skill categories are properly organized
        self.assertTrue(isinstance(skills, dict), "Skills should be organized in a dictionary by category")
        
        # Check if common skill categories are present
        expected_categories = ["programming_languages", "frameworks", "cloud_platforms"]
        for category in expected_categories:
            self.assertTrue(
                any(category in key for key in skills.keys()),
                f"Expected to find skills category '{category}' in results"
            )
        
        # Check if key skills were found
        found_skills = [skill for category in skills.values() for skill in category]
        expected_skills = ["python", "django", "flask", "javascript", "aws", "docker", "kubernetes"]
        for skill in expected_skills:
            self.assertTrue(
                any(skill == s.lower() for s in found_skills),
                f"Expected to find skill '{skill}' in extracted skills"
            )
    
    def test_extract_experience_requirements(self):
        """Test extraction of experience requirements."""
        experience = self.extractor.extract_experience_requirements(self.job_description, domain="computer_science")
        
        # Verify experience years extraction
        self.assertEqual(experience["years"], 5, "Should extract 5 years experience requirement")
        
        # Verify experience level
        self.assertEqual(experience["level"], "senior", "Should identify senior level position")
        
        # Verify education requirements
        self.assertTrue(
            any("bachelor" in edu.lower() for edu in experience["education"]),
            "Should extract Bachelor's degree requirement"
        )
        
        # Verify education field
        self.assertTrue(
            any("computer science" in edu.lower() for edu in experience["education"]),
            "Should extract Computer Science as education field"
        )
    
    @patch('src.utils.keyword_extraction.TfidfVectorizer')
    def test_extract_keywords_tfidf(self, mock_tfidf):
        """Test TF-IDF keyword extraction with mocked vectorizer."""
        # Set up the mock
        mock_vectorizer_instance = MagicMock()
        mock_tfidf.return_value = mock_vectorizer_instance
        
        # Configure mock to return predictable feature names and scores
        mock_vectorizer_instance.fit_transform.return_value.toarray.return_value = [[0.5, 0.8, 0.3, 0.9, 0.6]]
        mock_vectorizer_instance.get_feature_names_out.return_value = [
            "python", "django", "javascript", "senior", "developer"
        ]
        
        # Run extraction
        keywords = self.extractor.extract_keywords_tfidf(self.job_description, top_n=3)
        
        # Verify results
        self.assertEqual(len(keywords), 3, "Should return top 3 keywords")
        self.assertEqual(keywords[0][0], "senior", "Highest scoring keyword should be 'senior'")
        self.assertEqual(keywords[1][0], "django", "Second highest keyword should be 'django'")
        
        # Verify each item is a tuple of (string, float)
        for keyword, score in keywords:
            self.assertTrue(isinstance(keyword, str), "Keyword should be a string")
            self.assertTrue(isinstance(score, float), "Score should be a float")
    
    @patch('src.utils.keyword_extraction.nlp')
    def test_extract_named_entities(self, mock_nlp):
        """Test named entity extraction with mocked spaCy."""
        # Create mock entities
        mock_entity1 = MagicMock()
        mock_entity1.text = "Python"
        mock_entity1.label_ = "SKILL"
        
        mock_entity2 = MagicMock()
        mock_entity2.text = "Computer Science"
        mock_entity2.label_ = "FIELD"
        
        mock_entity3 = MagicMock()
        mock_entity3.text = "AWS"
        mock_entity3.label_ = "PRODUCT"
        
        # Configure mock doc
        mock_doc = MagicMock()
        mock_doc.ents = [mock_entity1, mock_entity2, mock_entity3]
        mock_nlp.return_value = mock_doc
        
        # Run extraction
        entities = self.extractor.extract_named_entities(self.job_description)
        
        # Verify results
        self.assertEqual(len(entities), 3, "Should extract 3 different entity types")
        self.assertEqual(entities["SKILL"], ["Python"], "Should extract Python as a SKILL")
        self.assertEqual(entities["FIELD"], ["Computer Science"], "Should extract Computer Science as a FIELD")
        self.assertEqual(entities["PRODUCT"], ["AWS"], "Should extract AWS as a PRODUCT")
    
    def test_analyze_job_description(self):
        """Test the comprehensive job description analysis."""
        # Patch component methods to isolate test
        with patch.object(self.extractor, 'extract_keywords_tfidf') as mock_keywords, \
             patch.object(self.extractor, 'extract_named_entities') as mock_entities, \
             patch.object(self.extractor, 'extract_technical_skills') as mock_skills, \
             patch.object(self.extractor, 'extract_experience_requirements') as mock_experience:
            
            # Configure mocks
            mock_keywords.return_value = [("python", 0.9), ("django", 0.8), ("senior", 0.7)]
            mock_entities.return_value = {"SKILL": ["Python", "Django"], "ORG": ["Company XYZ"]}
            mock_skills.return_value = {"programming_languages": ["python"], "frameworks": ["django", "flask"]}
            mock_experience.return_value = {"years": 5, "level": "senior", "education": ["Bachelor's in CS"]}
            
            # Run analysis
            result = self.extractor.analyze_job_description(self.job_description)
            
            # Verify results structure
            self.assertTrue("keywords" in result, "Result should contain keywords")
            self.assertTrue("entities" in result, "Result should contain entities")
            self.assertTrue("skills" in result, "Result should contain skills")
            self.assertTrue("experience" in result, "Result should contain experience")
            
            # Verify method calls
            mock_keywords.assert_called_once()
            mock_entities.assert_called_once()
            mock_skills.assert_called_once()
            mock_experience.assert_called_once()

if __name__ == "__main__":
    unittest.main()
