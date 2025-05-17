"""
ATS (Applicant Tracking System) Analyzer Module

This module analyzes resumes for ATS compatibility and provides suggestions
for improving ATS performance, specifically for CS, Data Science, and AI/ML resumes.
"""

import re
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

class ATSAnalyzer:
    """
    Analyzes resumes for compatibility with Applicant Tracking Systems
    and provides optimization recommendations specific to technical fields.
    """
    
    def __init__(self):
        """Initialize the ATS analyzer with rules and patterns"""
        # Common ATS issues
        self.ats_issues = {
            "file_format": "LaTeX files need to be converted to PDF before submission",
            "tables": "Tables can confuse ATS systems; use simple formatting",
            "columns": "Multiple columns may not parse correctly in ATS systems",
            "headers_footers": "Headers and footers might be ignored by ATS systems",
            "graphics": "Graphics, logos, and images will be ignored by ATS systems",
            "font": "Unusual fonts may not parse correctly; stick with standard fonts",
            "section_headings": "Use standard section headings (Experience, Education, Skills, Projects)",
            "keyword_density": "Include job-specific keywords but avoid keyword stuffing"
        }
        
        # Keywords specific to each domain
        self.domain_keywords = {
            "computer_science": [
                "software", "development", "programming", "engineer", "developer",
                "java", "python", "javascript", "c++", "web", "full-stack", "backend",
                "frontend", "cloud", "aws", "azure", "microservices", "api",
                "agile", "scrum", "git", "algorithms", "data structures", "testing"
            ],
            "data_science": [
                "data", "analysis", "analytics", "scientist", "machine learning",
                "statistics", "sql", "python", "r", "tableau", "visualization", 
                "pandas", "numpy", "sklearn", "tensorflow", "modeling", "big data",
                "data mining", "hypothesis testing", "regression", "clustering"
            ],
            "ai_ml": [
                "artificial intelligence", "machine learning", "deep learning", "neural networks",
                "nlp", "computer vision", "tensorflow", "pytorch", "keras", "model",
                "training", "algorithms", "supervised", "unsupervised", "reinforcement",
                "classification", "regression", "feature engineering", "data preprocessing"
            ]
        }
    
    async def analyze(self, 
                     resume_path: Path,
                     job_description: Any,
                     domain: str = "computer_science") -> Dict[str, Any]:
        """
        Analyze a resume for ATS compatibility
        
        Args:
            resume_path: Path to the resume file
            job_description: JobDescription model with title, description, requirements
            domain: Domain focus (computer_science, data_science, or ai_ml)
            
        Returns:
            Dict containing ATS analysis results and recommendations
        """
        try:
            # Read the resume file
            with open(resume_path, 'r', encoding='utf-8') as file:
                resume_content = file.read()
            
            # Extract plain text from LaTeX (basic extraction for analysis)
            plain_text = self._extract_text_from_latex(resume_content)
            
            # Get keywords from job description
            job_keywords = self._extract_keywords_from_job(job_description)
            
            # Add domain-specific keywords
            domain_keywords = self.domain_keywords.get(domain, self.domain_keywords["computer_science"])
            all_keywords = set(job_keywords + domain_keywords)
            
            # Analyze keyword matches
            matched_keywords, keyword_density = self._analyze_keywords(plain_text, all_keywords)
            
            # Calculate keyword match score
            match_score = self._calculate_keyword_match_score(
                matched_keywords,
                job_keywords,
                domain_keywords
            )
            
            # Check for ATS issues
            ats_issues = self._check_for_ats_issues(resume_content)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                ats_issues,
                matched_keywords,
                job_keywords,
                keyword_density,
                domain
            )
            
            # Calculate overall ATS score
            ats_score = self._calculate_ats_score(
                match_score,
                len(ats_issues),
                keyword_density,
                domain
            )
            
            # Prepare result
            result = {
                "ats_score": ats_score,
                "keyword_match_score": match_score,
                "matched_keywords": matched_keywords,
                "missing_keywords": [k for k in job_keywords if k not in matched_keywords],
                "keyword_density": keyword_density,
                "ats_issues": ats_issues,
                "recommendations": recommendations
            }
            
            return result
            
        except Exception as e:
            print(f"ATS analysis failed: {str(e)}")
            # Return a default result if analysis fails
            return {
                "ats_score": 70.0,  # Default moderate score
                "keyword_match_score": 65.0,
                "matched_keywords": [],
                "missing_keywords": [],
                "keyword_density": 0.0,
                "ats_issues": ["Analysis failed: " + str(e)],
                "recommendations": ["Convert LaTeX to PDF before submitting to ATS systems"]
            }
    
    def _extract_text_from_latex(self, latex_content: str) -> str:
        """Extract plain text from LaTeX content for ATS analysis"""
        text = latex_content
        
        # Remove LaTeX comments
        text = re.sub(r'%.*?\n', '\n', text)
        
        # Remove the preamble (everything before \begin{document})
        doc_begin = text.find('\\begin{document}')
        if doc_begin != -1:
            text = text[doc_begin + len('\\begin{document}'):]
        
        # Remove the end (everything after \end{document})
        doc_end = text.find('\\end{document}')
        if doc_end != -1:
            text = text[:doc_end]
        
        # Remove common LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})+', r'\2', text)
        text = re.sub(r'\{|\}', '', text)
        
        # Remove LaTeX environments
        text = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', text, flags=re.DOTALL)
        
        # Replace newlines with spaces
        text = re.sub(r'\\\\', ' ', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_keywords_from_job(self, job_description: Any) -> List[str]:
        """Extract keywords from the job description"""
        keywords = []
        
        # Add explicitly mentioned requirements
        for req in job_description.requirements:
            # Extract potential keywords
            words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.]*\b', req)
            for word in words:
                if len(word) > 2 and word.lower() not in ['and', 'the', 'for', 'with', 'etc']:
                    keywords.append(word.lower())
        
        # Add keywords from the job title
        title_words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.]*\b', job_description.title)
        for word in title_words:
            if len(word) > 2 and word.lower() not in ['and', 'the', 'for', 'with', 'etc']:
                keywords.append(word.lower())
        
        # Add keywords from job description
        desc_words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.]*\b', job_description.description)
        for word in desc_words:
            if len(word) > 4 and word.lower() not in ['and', 'the', 'for', 'with', 'etc', 'should', 'would', 'could']:
                keywords.append(word.lower())
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def _analyze_keywords(self, 
                         text: str, 
                         keywords: set) -> tuple[List[str], float]:
        """
        Analyze keyword matches in text
        
        Returns:
            Tuple of (matched_keywords, keyword_density)
        """
        matched_keywords = []
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Count matched keywords
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)
        
        # Calculate keyword density (matched keywords / word count)
        total_words = len(text.split())
        keyword_density = len(matched_keywords) / total_words if total_words > 0 else 0
        
        return matched_keywords, keyword_density
    
    def _calculate_keyword_match_score(self,
                                     matched_keywords: List[str],
                                     job_keywords: List[str],
                                     domain_keywords: List[str]) -> float:
        """Calculate the keyword match score (0-100)"""
        # Convert to sets for intersection operations
        matched_set = set(matched_keywords)
        job_set = set(job_keywords)
        domain_set = set(domain_keywords)
        
        # Calculate job keyword match percentage
        job_match_pct = len(matched_set.intersection(job_set)) / len(job_set) if job_set else 0
        
        # Calculate domain keyword match percentage
        domain_match_pct = len(matched_set.intersection(domain_set)) / len(domain_set) if domain_set else 0
        
        # Calculate weighted score (job keywords are more important)
        score = (job_match_pct * 0.7 + domain_match_pct * 0.3) * 100
        
        return min(round(score, 1), 100.0)  # Cap at 100
    
    def _check_for_ats_issues(self, resume_content: str) -> List[str]:
        """Check for common ATS compatibility issues in LaTeX resumes"""
        issues = []
        
        # Check for tables
        if '\\begin{table}' in resume_content or '\\begin{tabular}' in resume_content:
            issues.append(self.ats_issues["tables"])
        
        # Check for multi-column layout
        if '\\begin{multicols}' in resume_content or '\\twocolumn' in resume_content:
            issues.append(self.ats_issues["columns"])
        
        # Check for headers/footers
        if '\\pagestyle' in resume_content or '\\fancyhead' in resume_content or '\\fancyfoot' in resume_content:
            issues.append(self.ats_issues["headers_footers"])
        
        # Check for graphics/images
        if '\\includegraphics' in resume_content or '\\begin{figure}' in resume_content:
            issues.append(self.ats_issues["graphics"])
        
        # Check for non-standard fonts
        if '\\fontfamily' in resume_content or '\\newfontfamily' in resume_content:
            issues.append(self.ats_issues["font"])
        
        # Check for standard section headings
        standard_sections = ['experience', 'education', 'skills', 'projects']
        found_sections = []
        
        section_matches = re.findall(r'\\section\{(.*?)\}', resume_content, re.IGNORECASE)
        for match in section_matches:
            for section in standard_sections:
                if section in match.lower():
                    found_sections.append(section)
        
        missing_sections = [s for s in standard_sections if s not in found_sections]
        if missing_sections:
            issues.append(f"Missing standard section(s): {', '.join(missing_sections)}")
        
        # Remind about file format
        issues.append(self.ats_issues["file_format"])
        
        return issues
    
    def _generate_recommendations(self,
                                 ats_issues: List[str],
                                 matched_keywords: List[str],
                                 job_keywords: List[str],
                                 keyword_density: float,
                                 domain: str) -> List[str]:
        """Generate ATS optimization recommendations"""
        recommendations = []
        
        # Add recommendations based on ATS issues
        for issue in ats_issues:
            if issue != self.ats_issues["file_format"]:  # Skip the file format reminder
                recommendations.append(f"Fix: {issue}")
        
        # Check for missing important keywords
        missing_keywords = [k for k in job_keywords if k not in matched_keywords]
        if missing_keywords:
            top_missing = missing_keywords[:5]  # Limit to top 5
            recommendations.append(f"Add these keywords: {', '.join(top_missing)}")
        
        # Check keyword density
        if keyword_density > 0.1:
            recommendations.append("Keyword density is too high. Reduce keyword repetition for a more natural flow.")
        elif keyword_density < 0.03:
            recommendations.append("Keyword density is too low. Include more relevant keywords from the job description.")
        
        # Domain-specific recommendations
        if domain == "computer_science":
            recommendations.append("Emphasize technical skills, programming languages, and software development methodologies")
        elif domain == "data_science":
            recommendations.append("Highlight statistical analysis techniques, data visualization tools, and machine learning experience")
        elif domain == "ai_ml":
            recommendations.append("Showcase machine learning models, AI frameworks, and research experience")
        
        # General ATS recommendations
        recommendations.append("Use bullet points for experience and achievements")
        recommendations.append("Include the exact job title from the posting")
        recommendations.append("Convert the final document to PDF before submission")
        
        return recommendations
    
    def _calculate_ats_score(self,
                            keyword_match_score: float,
                            num_issues: int,
                            keyword_density: float,
                            domain: str) -> float:
        """Calculate overall ATS compatibility score (0-100)"""
        # Base score from keyword match
        score = keyword_match_score * 0.6
        
        # Deduct for ATS issues (each issue costs 5 points, up to 30)
        issue_penalty = min(num_issues * 5, 30)
        score -= issue_penalty
        
        # Adjust for keyword density
        if keyword_density < 0.02:
            score -= 10  # Too few keywords
        elif keyword_density > 0.1:
            score -= 15  # Too many keywords (keyword stuffing)
        elif 0.04 <= keyword_density <= 0.08:
            score += 10  # Optimal keyword density
        
        # Add domain-specific bonus (just for differentiation)
        domain_bonus = {
            "computer_science": 5,
            "data_science": 5,
            "ai_ml": 5
        }
        score += domain_bonus.get(domain, 0)
        
        # Ensure score is between 0 and 100
        return max(0, min(round(score, 1), 100))
