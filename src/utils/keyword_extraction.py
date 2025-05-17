"""
Keyword Extraction Module

This module provides advanced functionality for extracting, ranking, and analyzing
keywords from job descriptions for use in resume optimization.
"""

import re
import json
from typing import List, Dict, Any, Tuple, Set, Optional
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class KeywordExtractor:
    """
    Advanced keyword extraction and analysis from job descriptions.
    Provides methods for extracting, ranking, and categorizing keywords
    for resume optimization.
    """
    
    def __init__(self, domain_knowledge_path: Optional[str] = None):
        """
        Initialize the keyword extractor with domain knowledge and NLP tools.
        
        Args:
            domain_knowledge_path: Optional path to JSON file with domain-specific knowledge
        """
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Domain-specific knowledge
        self.domain_knowledge = self._load_domain_knowledge(domain_knowledge_path)
        
        # Skill categories for organization
        self.skill_categories = {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", 
                "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "express", "node.js",
                "fastapi", "laravel", "rails", "asp.net", "tensorflow", "pytorch", "keras"
            ],
            "databases": [
                "sql", "mysql", "postgresql", "mongodb", "dynamodb", "redis", "elasticsearch",
                "oracle", "sqlite", "cassandra", "couchdb", "mariadb", "neo4j"
            ],
            "cloud_platforms": [
                "aws", "azure", "gcp", "google cloud", "cloud computing", "serverless",
                "lambda", "ec2", "s3", "docker", "kubernetes", "heroku", "digitalocean"
            ],
            "tools": [
                "git", "github", "gitlab", "bitbucket", "jira", "confluence", "jenkins",
                "travis", "circle ci", "terraform", "ansible", "prometheus", "grafana"
            ],
            "methodologies": [
                "agile", "scrum", "kanban", "tdd", "bdd", "ci/cd", "devops", "mlops",
                "waterfall", "lean", "extreme programming", "pair programming"
            ],
            "soft_skills": [
                "communication", "teamwork", "leadership", "problem solving", "analytical",
                "time management", "adaptability", "creativity", "critical thinking"
            ]
        }
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 3),
            use_idf=True
        )
    
    def _load_domain_knowledge(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load domain-specific knowledge from file or use default knowledge.
        
        Args:
            path: Path to JSON file with domain knowledge
            
        Returns:
            Dictionary with domain knowledge
        """
        default_knowledge = {
            "computer_science": {
                "roles": ["software engineer", "software developer", "full stack", "backend", 
                          "frontend", "devops", "sre", "system architect"],
                "skills": ["algorithms", "data structures", "system design", "microservices", 
                          "distributed systems", "databases", "api design", "web development"],
                "experience_patterns": [
                    r"(\d+)\+?\s+years?",
                    r"experience\s+(?:of\s+)?(\d+)\+?\s+years?",
                    r"senior|mid-level|junior|entry-level"
                ]
            },
            "data_science": {
                "roles": ["data scientist", "data analyst", "data engineer", "ml engineer",
                         "bi analyst", "statistician", "quantitative analyst"],
                "skills": ["statistics", "machine learning", "data analysis", "data visualization",
                          "etl", "data modeling", "database design", "predictive modeling"],
                "experience_patterns": [
                    r"(\d+)\+?\s+years?",
                    r"experience\s+(?:of\s+)?(\d+)\+?\s+years?",
                    r"senior|mid-level|junior|entry-level"
                ]
            },
            "ai_ml": {
                "roles": ["machine learning engineer", "ai researcher", "nlp engineer", 
                         "computer vision engineer", "deep learning engineer"],
                "skills": ["deep learning", "neural networks", "nlp", "computer vision",
                          "reinforcement learning", "model training", "model deployment"],
                "experience_patterns": [
                    r"(\d+)\+?\s+years?",
                    r"experience\s+(?:of\s+)?(\d+)\+?\s+years?",
                    r"senior|mid-level|junior|entry-level"
                ]
            }
        }
        
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading domain knowledge from {path}: {e}")
                return default_knowledge
        else:
            return default_knowledge
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text by removing special characters, converting to lowercase,
        tokenizing, removing stop words, and lemmatizing.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        filtered_tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        return ' '.join(filtered_tokens)
    
    def extract_keywords_tfidf(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        # Preprocess text
        preprocessed_text = self.preprocess_text(text)
        
        # Fit and transform
        tfidf_matrix = self.tfidf_vectorizer.fit_transform([preprocessed_text])
        
        # Get feature names and scores
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        # Sort by score
        sorted_keywords = [(feature_names[i], scores[i]) for i in scores.argsort()[::-1]]
        
        return sorted_keywords[:top_n]
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text using spaCy.
        
        Args:
            text: Text to extract named entities from
            
        Returns:
            Dictionary with entity types as keys and lists of entities as values
        """
        doc = nlp(text)
        
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        return entities
    
    def extract_technical_skills(self, text: str, domain: str = "computer_science") -> Dict[str, List[str]]:
        """
        Extract technical skills from text based on predefined categories and domain knowledge.
        
        Args:
            text: Text to extract skills from
            domain: Domain to focus on (computer_science, data_science, or ai_ml)
            
        Returns:
            Dictionary with skill categories as keys and lists of skills as values
        """
        text_lower = text.lower()
        
        # Extract skills by category
        skills_by_category = {}
        for category, skills in self.skill_categories.items():
            found_skills = []
            for skill in skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found_skills.append(skill)
            if found_skills:
                skills_by_category[category] = found_skills
        
        # Add domain-specific skills
        domain_skills = self.domain_knowledge.get(domain, {}).get("skills", [])
        found_domain_skills = []
        for skill in domain_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_domain_skills.append(skill)
        if found_domain_skills:
            skills_by_category["domain_specific"] = found_domain_skills
        
        return skills_by_category
    
    def extract_experience_requirements(self, text: str, domain: str = "computer_science") -> Dict[str, Any]:
        """
        Extract experience requirements from text.
        
        Args:
            text: Text to extract experience requirements from
            domain: Domain to focus on
            
        Returns:
            Dictionary with experience requirements
        """
        text_lower = text.lower()
        
        experience = {
            "years": None,
            "level": None,
            "education": [],
            "certifications": []
        }
        
        # Extract years of experience
        exp_patterns = [
            r"(\d+)\+?\s+years?\s+(?:of\s+)?experience",
            r"experience\s+(?:of\s+)?(\d+)\+?\s+years?",
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                experience["years"] = int(matches[0])
                break
        
        # Extract experience level
        level_patterns = {
            "entry": [r"entry[ -]level", r"junior", r"beginner"],
            "mid": [r"mid[ -]level", r"intermediate", r"associate"],
            "senior": [r"senior", r"sr\.", r"experienced", r"lead"],
            "expert": [r"expert", r"principal", r"staff", r"architect"]
        }
        
        for level, patterns in level_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + pattern + r'\b', text_lower):
                    experience["level"] = level
                    break
            if experience["level"]:
                break
        
        # Extract education requirements
        edu_patterns = [
            r"bachelor'?s?|master'?s?|phd|doctorate|bs|ba|ms|msc|meng|bsc|beng",
            r"degree in (?:computer science|cs|software engineering|data science|machine learning|artificial intelligence|ai|ml|information technology|it)"
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                experience["education"].append(match.strip())
        
        # Extract certifications
        cert_patterns = [
            r"aws certified", r"azure certified", r"google cloud certified", 
            r"certified in", r"certification", r"cissp", r"cisa", r"cism", 
            r"pmp", r"agile certified", r"scrum certified"
        ]
        
        for pattern in cert_patterns:
            if re.search(r'\b' + pattern + r'\b', text_lower):
                experience["certifications"].append(pattern)
        
        return experience
    
    def analyze_job_description(self, text: str, domain: str = "computer_science", top_n_keywords: int = 20) -> Dict[str, Any]:
        """
        Comprehensive analysis of a job description.
        
        Args:
            text: Job description text
            domain: Domain to focus on
            top_n_keywords: Number of top keywords to return
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "keywords": self.extract_keywords_tfidf(text, top_n_keywords),
            "entities": self.extract_named_entities(text),
            "skills": self.extract_technical_skills(text, domain),
            "experience": self.extract_experience_requirements(text, domain)
        }
        
        return analysis
