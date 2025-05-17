"""
Feedback Processor Module

This module processes user feedback on resume optimizations to improve future results
through a continuous learning loop.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
from datetime import datetime

class FeedbackProcessor:
    """
    Process and analyze user feedback on resume optimizations to improve future
    optimization performance through a continuous learning loop.
    """
    
    def __init__(self):
        """Initialize the feedback processor with storage paths"""
        # Directory for storing feedback data
        self.feedback_dir = Path("data/feedback")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        # File for aggregated feedback analysis
        self.analysis_file = self.feedback_dir / "feedback_analysis.json"
        
        # Initialize feedback analysis if doesn't exist
        if not self.analysis_file.exists():
            self._initialize_analysis()
    
    async def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback on resume optimization
        
        Args:
            feedback_data: Dict containing feedback information
            
        Returns:
            Dict with processing status and confirmation
        """
        try:
            # Extract feedback info
            resume_id = feedback_data.get("resume_id")
            effectiveness_rating = feedback_data.get("effectiveness_rating", 0)
            quality_rating = feedback_data.get("quality_rating", 0)
            comments = feedback_data.get("comments", "")
            interview_result = feedback_data.get("interview_result", "")
            
            # Validate required fields
            if not resume_id:
                return {"status": "error", "message": "Missing resume ID"}
            
            # Create feedback record
            feedback_record = {
                "resume_id": resume_id,
                "effectiveness_rating": effectiveness_rating,
                "quality_rating": quality_rating,
                "comments": comments,
                "interview_result": interview_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save individual feedback
            await self._save_feedback(resume_id, feedback_record)
            
            # Update aggregated analysis
            await self._update_analysis(feedback_record)
            
            return {
                "status": "success",
                "message": "Feedback processed successfully",
                "feedback_id": f"feedback_{resume_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
        except Exception as e:
            print(f"Error processing feedback: {str(e)}")
            return {"status": "error", "message": f"Failed to process feedback: {str(e)}"}
    
    async def get_feedback_insights(self) -> Dict[str, Any]:
        """
        Get insights from aggregated feedback for improving resume optimization
        
        Returns:
            Dict containing feedback insights and recommendations
        """
        try:
            if not self.analysis_file.exists():
                return {"status": "error", "message": "No feedback data available"}
            
            # Load analysis data
            with open(self.analysis_file, 'r') as file:
                analysis = json.load(file)
            
            # Generate insights
            avg_effectiveness = analysis["metrics"]["avg_effectiveness"]
            avg_quality = analysis["metrics"]["avg_quality"]
            total_feedback = analysis["metrics"]["total_feedback"]
            
            # Calculate success rates from interview results
            interview_results = analysis["interview_results"]
            total_with_interview_result = sum(interview_results.values())
            
            success_rate = 0
            if total_with_interview_result > 0:
                success_count = interview_results.get("invited", 0) + interview_results.get("offered", 0)
                success_rate = (success_count / total_with_interview_result) * 100
            
            # Get top positive and negative comment themes
            positive_themes = sorted(
                analysis["positive_themes"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            negative_themes = sorted(
                analysis["negative_themes"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            # Format insights
            insights = {
                "metrics": {
                    "total_feedback": total_feedback,
                    "avg_effectiveness": round(avg_effectiveness, 1),
                    "avg_quality": round(avg_quality, 1),
                    "interview_success_rate": round(success_rate, 1)
                },
                "strengths": [theme for theme, _ in positive_themes],
                "areas_for_improvement": [theme for theme, _ in negative_themes],
                "recommendations": self._generate_recommendations(
                    avg_effectiveness,
                    avg_quality,
                    positive_themes,
                    negative_themes
                )
            }
            
            return insights
            
        except Exception as e:
            print(f"Error generating feedback insights: {str(e)}")
            return {"status": "error", "message": f"Failed to generate insights: {str(e)}"}
    
    async def _save_feedback(self, resume_id: str, feedback_data: Dict[str, Any]) -> None:
        """Save individual feedback to a file"""
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = self.feedback_dir / f"feedback_{resume_id}_{timestamp}.json"
        
        # Save feedback data
        async with asyncio.Lock():  # Ensure thread safety
            with open(filename, 'w') as file:
                json.dump(feedback_data, file, indent=2)
    
    async def _update_analysis(self, feedback_data: Dict[str, Any]) -> None:
        """Update the aggregated feedback analysis"""
        async with asyncio.Lock():  # Ensure thread safety
            # Load current analysis
            if self.analysis_file.exists():
                with open(self.analysis_file, 'r') as file:
                    analysis = json.load(file)
            else:
                analysis = self._initialize_analysis()
            
            # Update metrics
            metrics = analysis["metrics"]
            metrics["total_feedback"] += 1
            
            # Update ratings
            effectiveness = feedback_data.get("effectiveness_rating", 0)
            quality = feedback_data.get("quality_rating", 0)
            
            if effectiveness > 0:
                metrics["total_effectiveness"] += effectiveness
                metrics["avg_effectiveness"] = metrics["total_effectiveness"] / metrics["total_feedback"]
            
            if quality > 0:
                metrics["total_quality"] += quality
                metrics["avg_quality"] = metrics["total_quality"] / metrics["total_feedback"]
            
            # Update interview results
            interview_result = feedback_data.get("interview_result", "").lower()
            if interview_result:
                analysis["interview_results"][interview_result] = analysis["interview_results"].get(interview_result, 0) + 1
            
            # Process comments for themes
            comments = feedback_data.get("comments", "")
            if comments:
                self._extract_comment_themes(comments, analysis)
            
            # Save updated analysis
            with open(self.analysis_file, 'w') as file:
                json.dump(analysis, file, indent=2)
    
    def _initialize_analysis(self) -> Dict[str, Any]:
        """Initialize the feedback analysis structure"""
        analysis = {
            "metrics": {
                "total_feedback": 0,
                "total_effectiveness": 0,
                "total_quality": 0,
                "avg_effectiveness": 0,
                "avg_quality": 0
            },
            "interview_results": {
                "invited": 0,
                "rejected": 0,
                "pending": 0,
                "offered": 0,
                "other": 0
            },
            "positive_themes": {},
            "negative_themes": {}
        }
        
        # Save the initial structure
        with open(self.analysis_file, 'w') as file:
            json.dump(analysis, file, indent=2)
        
        return analysis
    
    def _extract_comment_themes(self, comment: str, analysis: Dict[str, Any]) -> None:
        """Extract themes from feedback comments"""
        # List of positive theme keywords
        positive_keywords = [
            "helpful", "useful", "improved", "better", "excellent", "great",
            "clear", "effective", "concise", "professional", "relevant", "accurate"
        ]
        
        # List of negative theme keywords
        negative_keywords = [
            "unhelpful", "useless", "worse", "poor", "unclear", "ineffective",
            "verbose", "unprofessional", "irrelevant", "inaccurate", "misleading",
            "confusing", "error", "wrong", "bad", "missing"
        ]
        
        # Convert comment to lowercase for case-insensitive matching
        comment_lower = comment.lower()
        
        # Check for positive themes
        for keyword in positive_keywords:
            if keyword in comment_lower:
                theme = f"positive_{keyword}"
                analysis["positive_themes"][theme] = analysis["positive_themes"].get(theme, 0) + 1
        
        # Check for negative themes
        for keyword in negative_keywords:
            if keyword in comment_lower:
                theme = f"negative_{keyword}"
                analysis["negative_themes"][theme] = analysis["negative_themes"].get(theme, 0) + 1
    
    def _generate_recommendations(self,
                                avg_effectiveness: float,
                                avg_quality: float,
                                positive_themes: List[tuple],
                                negative_themes: List[tuple]) -> List[str]:
        """Generate recommendations based on feedback analysis"""
        recommendations = []
        
        # Add recommendations based on metrics
        if avg_effectiveness < 3.5:
            recommendations.append(
                "Improve resume optimization effectiveness by focusing on better keyword matching"
            )
        
        if avg_quality < 3.5:
            recommendations.append(
                "Enhance output quality with more professional formatting and clearer content"
            )
        
        # Add recommendations based on negative themes
        for theme, _ in negative_themes:
            if "unclear" in theme:
                recommendations.append(
                    "Improve clarity of optimized content with more specific achievements"
                )
            elif "irrelevant" in theme:
                recommendations.append(
                    "Focus on more relevant skills and experiences for each job description"
                )
            elif "inaccurate" in theme or "error" in theme:
                recommendations.append(
                    "Enhance accuracy in parsing and optimizing resume content"
                )
        
        # Add general recommendation if no specific ones generated
        if not recommendations:
            recommendations.append(
                "Continue to refine optimization algorithms based on successful resumes"
            )
        
        return recommendations
