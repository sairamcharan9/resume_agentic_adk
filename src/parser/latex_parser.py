"""
LaTeX Resume Parser Module

This module is responsible for parsing LaTeX resume files and converting them
into a structured format that can be used by the optimizer.
"""

import re
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

class LaTeXResumeParser:
    """Parse LaTeX resume files into structured data"""
    
    def __init__(self):
        """Initialize the LaTeX parser with common LaTeX resume sections and commands"""
        self.section_patterns = {
            "education": r"\\section{(?:Education|EDUCATION)}(.*?)(?:\\section|\Z)",
            "experience": r"\\section{(?:Experience|EXPERIENCE|Work Experience|WORK EXPERIENCE|Professional Experience|PROFESSIONAL EXPERIENCE)}(.*?)(?:\\section|\Z)",
            "projects": r"\\section{(?:Projects|PROJECTS|Selected Projects|SELECTED PROJECTS)}(.*?)(?:\\section|\Z)",
            "skills": r"\\section{(?:Skills|SKILLS|Technical Skills|TECHNICAL SKILLS)}(.*?)(?:\\section|\Z)",
            "publications": r"\\section{(?:Publications|PUBLICATIONS)}(.*?)(?:\\section|\Z)",
            "awards": r"\\section{(?:Awards|AWARDS|Honors|HONORS|Achievements|ACHIEVEMENTS)}(.*?)(?:\\section|\Z)"
        }
        
        # Common patterns in CS/DS/AI resumes
        self.experience_patterns = {
            "company": r"\\textbf{(.*?)}|\\textsc{(.*?)}|\\company{(.*?)}",
            "role": r"\\emph{(.*?)}|\\role{(.*?)}|\\jobtitle{(.*?)}",
            "date": r"\\date{(.*?)}|\\duration{(.*?)}|\\small{(.*?)}",
            "location": r"\\location{(.*?)}",
            "description": r"\\begin{itemize}(.*?)\\end{itemize}"
        }
        
        self.project_patterns = {
            "title": r"\\textbf{(.*?)}|\\project{(.*?)}",
            "technologies": r"\\technologies{(.*?)}|\\tech{(.*?)}|\\emph{(.*?)}",
            "description": r"\\begin{itemize}(.*?)\\end{itemize}"
        }
        
        self.skill_patterns = {
            "category": r"\\textbf{(.*?)}",
            "skills": r"\\item\s+(.*?)(?=\\item|\Z)"
        }
        
        # Custom commands that might be defined in the preamble
        self.custom_commands = {}
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a LaTeX resume file into a structured dictionary
        
        Args:
            file_path: Path to the LaTeX file
            
        Returns:
            Dict containing structured resume data
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract preamble to find custom commands
            preamble = self._extract_preamble(content)
            self._parse_custom_commands(preamble)
            
            # Extract document content (everything between \begin{document} and \end{document})
            document_content = self._extract_document_content(content)
            
            # Parse different sections
            parsed_resume = {}
            
            # Basic contact information
            parsed_resume["contact_info"] = self._parse_contact_info(document_content)
            
            # Education section
            parsed_resume["education"] = self._parse_section(document_content, "education")
            
            # Experience section
            parsed_resume["experience"] = self._parse_experience(document_content)
            
            # Projects section
            parsed_resume["projects"] = self._parse_projects(document_content)
            
            # Skills section
            parsed_resume["skills"] = self._parse_skills(document_content)
            
            # Publications section (important for research/academic)
            parsed_resume["publications"] = self._parse_section(document_content, "publications")
            
            # Awards/Achievements
            parsed_resume["awards"] = self._parse_section(document_content, "awards")
            
            # Add the template type if we can detect it
            parsed_resume["template"] = self._detect_template(content)
            
            return parsed_resume
            
        except Exception as e:
            raise Exception(f"Failed to parse LaTeX resume: {str(e)}")
    
    def _extract_preamble(self, content: str) -> str:
        """Extract the preamble from the LaTeX document"""
        begin_doc_match = re.search(r"\\begin{document}", content)
        if begin_doc_match:
            return content[:begin_doc_match.start()]
        return ""
    
    def _parse_custom_commands(self, preamble: str) -> None:
        """Parse custom commands defined in the preamble"""
        # Find all \newcommand definitions
        command_matches = re.finditer(r"\\newcommand{\\(\w+)}(\[\d+\])?\{(.*?)\}", preamble)
        for match in command_matches:
            command_name = match.group(1)
            command_def = match.group(3)
            self.custom_commands[command_name] = command_def
    
    def _extract_document_content(self, content: str) -> str:
        """Extract content between \begin{document} and \end{document}"""
        doc_match = re.search(r"\\begin{document}(.*?)\\end{document}", content, re.DOTALL)
        if doc_match:
            return doc_match.group(1)
        return content  # Return full content if not found
    
    def _parse_contact_info(self, content: str) -> Dict[str, str]:
        """Extract contact information from the document header"""
        contact_info = {}
        
        # Common patterns for contact info in LaTeX resumes
        name_match = re.search(r"\\name{(.*?)}", content) or re.search(r"\\centerline{\\Huge\\textbf{(.*?)}}", content)
        if name_match:
            contact_info["name"] = name_match.group(1)
        
        email_match = re.search(r"\\email{(.*?)}|\\href{mailto:(.*?)}", content)
        if email_match:
            contact_info["email"] = email_match.group(1) or email_match.group(2)
        
        phone_match = re.search(r"\\phone{(.*?)}|\\mobilephonesymbol\\s+(.*?)\\\\", content)
        if phone_match:
            contact_info["phone"] = phone_match.group(1) or phone_match.group(2)
        
        linkedin_match = re.search(r"\\linkedin{(.*?)}|\\href{https://www.linkedin.com/(.*?)}", content)
        if linkedin_match:
            contact_info["linkedin"] = linkedin_match.group(1) or linkedin_match.group(2)
        
        github_match = re.search(r"\\github{(.*?)}|\\href{https://github.com/(.*?)}", content)
        if github_match:
            contact_info["github"] = github_match.group(1) or github_match.group(2)
        
        return contact_info
    
    def _parse_section(self, content: str, section_name: str) -> List[Dict[str, Any]]:
        """Generic section parser based on the section name"""
        section_content = []
        pattern = self.section_patterns.get(section_name)
        
        if not pattern:
            return section_content
        
        section_match = re.search(pattern, content, re.DOTALL)
        if not section_match:
            return section_content
        
        raw_content = section_match.group(1)
        
        # For education, experience, etc. - implement specific parsing logic
        # This is a placeholder implementation
        items = re.finditer(r"\\item\s+(.*?)(?=\\item|\Z)", raw_content, re.DOTALL)
        for item in items:
            section_content.append({"content": item.group(1).strip()})
        
        return section_content
    
    def _parse_experience(self, content: str) -> List[Dict[str, Any]]:
        """Parse the experience section into structured data"""
        experience_items = []
        
        # Get the experience section
        section_match = re.search(self.section_patterns["experience"], content, re.DOTALL)
        if not section_match:
            return experience_items
        
        exp_content = section_match.group(1)
        
        # Find all experience entries - typically separated by \resumeSubheading, \item, or custom environments
        exp_entries = re.split(r"\\resumeSubheading|\\cventry|\\begin{rSubsection}|\\textbf{", exp_content)
        
        for entry in exp_entries:
            if not entry.strip():
                continue
                
            # If we split on \textbf{, we need to add it back
            if not entry.startswith("{"):
                entry = "\\textbf{" + entry
                
            exp_item = {}
            
            # Extract company name
            company_match = re.search(self.experience_patterns["company"], entry, re.DOTALL)
            if company_match:
                company = next((g for g in company_match.groups() if g), "")
                exp_item["company"] = self._clean_latex(company)
            
            # Extract role/title
            role_match = re.search(self.experience_patterns["role"], entry, re.DOTALL)
            if role_match:
                role = next((g for g in role_match.groups() if g), "")
                exp_item["role"] = self._clean_latex(role)
            
            # Extract dates
            date_match = re.search(self.experience_patterns["date"], entry, re.DOTALL)
            if date_match:
                date = next((g for g in date_match.groups() if g), "")
                exp_item["duration"] = self._clean_latex(date)
            
            # Extract description (usually in itemize environment)
            desc_match = re.search(self.experience_patterns["description"], entry, re.DOTALL)
            if desc_match:
                # Process bullet points
                bullets = re.findall(r"\\item\s+(.*?)(?=\\item|\Z)", desc_match.group(1), re.DOTALL)
                exp_item["description"] = "\n".join([self._clean_latex(bullet.strip()) for bullet in bullets])
            else:
                # If no itemize environment, try to extract text directly
                # Remove known sections we've already extracted
                for pattern in self.experience_patterns.values():
                    entry = re.sub(pattern, "", entry, re.DOTALL)
                
                # Clean up what's left as the description
                description = self._clean_latex(entry.strip())
                if description:
                    exp_item["description"] = description
            
            if exp_item:
                experience_items.append(exp_item)
        
        return experience_items
    
    def _parse_projects(self, content: str) -> List[Dict[str, Any]]:
        """Parse the projects section into structured data"""
        project_items = []
        
        # Get the projects section
        section_match = re.search(self.section_patterns["projects"], content, re.DOTALL)
        if not section_match:
            return project_items
        
        proj_content = section_match.group(1)
        
        # Find all project entries
        project_entries = re.split(r"\\resumeSubItem|\\begin{rSubsection}|\\textbf{", proj_content)
        
        for entry in project_entries:
            if not entry.strip():
                continue
                
            # If we split on \textbf{, we need to add it back
            if not entry.startswith("{"):
                entry = "\\textbf{" + entry
                
            proj_item = {}
            
            # Extract project title
            title_match = re.search(self.project_patterns["title"], entry, re.DOTALL)
            if title_match:
                title = next((g for g in title_match.groups() if g), "")
                proj_item["title"] = self._clean_latex(title)
            
            # Extract technologies
            tech_match = re.search(self.project_patterns["technologies"], entry, re.DOTALL)
            if tech_match:
                tech = next((g for g in tech_match.groups() if g), "")
                proj_item["technologies"] = self._clean_latex(tech)
            
            # Extract description
            desc_match = re.search(self.project_patterns["description"], entry, re.DOTALL)
            if desc_match:
                bullets = re.findall(r"\\item\s+(.*?)(?=\\item|\Z)", desc_match.group(1), re.DOTALL)
                desc_text = "\n".join([self._clean_latex(bullet.strip()) for bullet in bullets])
                
                # Separate out achievements if possible
                achievements = []
                description_lines = []
                
                for line in desc_text.split("\n"):
                    if any(keyword in line.lower() for keyword in ["achiev", "result", "impact", "increas", "reduc", "improv"]):
                        achievements.append(line)
                    else:
                        description_lines.append(line)
                
                proj_item["description"] = "\n".join(description_lines)
                if achievements:
                    proj_item["achievements"] = "\n".join(achievements)
                else:
                    proj_item["achievements"] = ""
            
            if proj_item:
                project_items.append(proj_item)
        
        return project_items
    
    def _parse_skills(self, content: str) -> Dict[str, List[str]]:
        """Parse the skills section into categories and skills"""
        skills_dict = {}
        
        # Get the skills section
        section_match = re.search(self.section_patterns["skills"], content, re.DOTALL)
        if not section_match:
            return skills_dict
        
        skills_content = section_match.group(1)
        
        # Try to identify categories of skills (common in CS/DS resumes)
        categories = re.finditer(self.skill_patterns["category"], skills_content)
        
        for cat_match in categories:
            category = self._clean_latex(cat_match.group(1))
            
            # Find the end of this category (either the next category or the end of the skills section)
            category_end = skills_content.find("\\textbf{", cat_match.end())
            if category_end == -1:
                category_end = len(skills_content)
            
            category_content = skills_content[cat_match.end():category_end]
            
            # Extract skills from this category
            skills_list = []
            skill_items = re.finditer(self.skill_patterns["skills"], category_content, re.DOTALL)
            
            for skill_match in skill_items:
                skill = self._clean_latex(skill_match.group(1))
                skills_list.append(skill)
            
            if skills_list:
                skills_dict[category] = skills_list
        
        # If no categories were found, try to extract skills directly
        if not skills_dict:
            skill_items = re.finditer(r"\\item\s+(.*?)(?=\\item|\Z)", skills_content, re.DOTALL)
            all_skills = []
            
            for skill_match in skill_items:
                skill = self._clean_latex(skill_match.group(1))
                all_skills.append(skill)
            
            if all_skills:
                skills_dict["Technical Skills"] = all_skills
        
        return skills_dict
    
    def _clean_latex(self, text: str) -> str:
        """Clean LaTeX formatting from text"""
        if not text:
            return ""
            
        # Remove common LaTeX formatting commands
        cleaned = text
        
        # Remove formatting commands like \textbf{}, \textit{}, etc.
        cleaned = re.sub(r"\\text(?:bf|it|sc|sl|tt){(.*?)}", r"\1", cleaned)
        
        # Remove hyperref commands
        cleaned = re.sub(r"\\href{.*?}{(.*?)}", r"\1", cleaned)
        
        # Remove \\ (newlines) and replace with space
        cleaned = re.sub(r"\\\\", " ", cleaned)
        
        # Remove other common commands
        cleaned = re.sub(r"\\[a-z]+{(.*?)}", r"\1", cleaned)
        
        # Remove braces
        cleaned = re.sub(r"[{}]", "", cleaned)
        
        # Remove extra whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        
        return cleaned
    
    def _detect_template(self, content: str) -> str:
        """Try to detect which LaTeX resume template is being used"""
        template_patterns = {
            "moderncv": r"\\documentclass{moderncv}",
            "awesome-cv": r"\\documentclass{awesome-cv}",
            "deedy-resume": r"\\def\\name{",
            "altacv": r"\\documentclass{altacv}",
            "res": r"\\documentclass{res}"
        }
        
        for template, pattern in template_patterns.items():
            if re.search(pattern, content):
                return template
        
        return "custom"
