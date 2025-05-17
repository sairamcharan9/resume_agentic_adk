"""
LaTeX Generator Module

This module generates optimized LaTeX resume files based on the optimized
resume data structure and selected template.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import shutil
import re

class LaTeXGenerator:
    """
    Generate LaTeX resume files based on optimized resume data and templates
    specifically for Computer Science, Data Science, and AI/ML positions.
    """
    
    def __init__(self):
        """Initialize the LaTeX generator with template handling"""
        # Base path for LaTeX templates
        self.templates_dir = Path("templates/latex")
        
        # Ensure templates directory exists
        if not self.templates_dir.exists():
            os.makedirs(self.templates_dir, exist_ok=True)
        
        # Default templates by domain
        self.default_templates = {
            "computer_science": "cs_modern.tex",
            "data_science": "data_science_modern.tex",
            "ai_ml": "ai_research.tex",
            "default": "modern.tex"
        }
        
        # Common LaTeX commands and environments for resume sections
        self.latex_commands = {
            "section": "\\section{{{}}}\n",
            "subsection": "\\subsection{{{}}}\n",
            "item": "\\item {}\n",
            "itemize_begin": "\\begin{itemize}\n",
            "itemize_end": "\\end{itemize}\n",
            "textbf": "\\textbf{{{}}}"
        }
    
    async def generate(self, 
                      optimized_data: Dict[str, Any],
                      output_path: Path,
                      template_name: Optional[str] = None,
                      domain: str = "computer_science") -> Path:
        """
        Generate a LaTeX resume file based on optimized data
        
        Args:
            optimized_data: Optimized resume data structure
            output_path: Path to save the generated LaTeX file
            template_name: Optional template name to use
            domain: Domain focus (computer_science, data_science, or ai_ml)
            
        Returns:
            Path to the generated LaTeX file
        """
        try:
            # Determine template to use
            template_path = self._get_template_path(template_name, domain, optimized_data.get("template", "custom"))
            
            # Read the template
            with open(template_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
            
            # Find document body (between \begin{document} and \end{document})
            doc_match = re.search(r'(\\begin{document})(.*?)(\\end{document})', template_content, re.DOTALL)
            
            if not doc_match:
                raise ValueError("Invalid LaTeX template: Could not find document environment")
            
            begin_doc = doc_match.group(1)
            doc_content = doc_match.group(2)
            end_doc = doc_match.group(3)
            
            # Extract preamble (everything before \begin{document})
            preamble = template_content[:doc_match.start()]
            
            # Generate new document content
            new_content = await self._generate_content(optimized_data, domain)
            
            # Put it all together
            modified_template = preamble + begin_doc + new_content + end_doc
            
            # Update contact information in the preamble
            modified_template = self._update_contact_info(modified_template, optimized_data.get("contact_info", {}))
            
            # Write to output file
            output_path.parent.mkdir(exist_ok=True, parents=True)
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(modified_template)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"LaTeX generation failed: {str(e)}")
    
    def _get_template_path(self, 
                          template_name: Optional[str], 
                          domain: str,
                          original_template: str) -> Path:
        """Determine which template to use based on inputs"""
        # If a specific template name is provided, try to use it
        if template_name:
            template_path = self.templates_dir / template_name
            if template_path.exists():
                return template_path
            
            # Try adding .tex extension if missing
            if not template_name.endswith(".tex"):
                template_path = self.templates_dir / f"{template_name}.tex"
                if template_path.exists():
                    return template_path
        
        # If the original template was detected and we have a matching template
        if original_template != "custom":
            for template_file in self.templates_dir.glob("*.tex"):
                if original_template.lower() in template_file.stem.lower():
                    return template_file
        
        # Use domain-specific default
        default_template = self.default_templates.get(domain, self.default_templates["default"])
        default_path = self.templates_dir / default_template
        
        # If the domain-specific template doesn't exist, fall back to generic
        if not default_path.exists():
            default_path = self.templates_dir / self.default_templates["default"]
            
            # If even the generic template doesn't exist, create it
            if not default_path.exists():
                self._create_default_template(default_path)
        
        return default_path
    
    def _create_default_template(self, path: Path) -> None:
        """Create a default LaTeX resume template"""
        # Modern template content with clean layout
        template_content = r"""\documentclass[11pt,a4paper,sans]{moderncv}

% Modern CV theme
\moderncvstyle{classic}
\moderncvcolor{blue}

% Character encoding
\usepackage[utf8]{inputenc}
\usepackage[scale=0.85]{geometry}

% Personal data
\name{John}{Doe}
\title{Resume}
\phone{(123) 456-7890}
\email{john.doe@example.com}
\homepage{portfolio.com}
\social[github]{githubuser}
\social[linkedin]{linkedinuser}

\begin{document}
\makecvtitle

\section{Education}
\cventry{2018--2022}{Bachelor of Science in Computer Science}{University}{City}{}{GPA: 3.8/4.0}

\section{Experience}
\cventry{2022--Present}{Software Engineer}{Tech Company}{City}{}{
\begin{itemize}
\item Developed and maintained features for a web application using React and Node.js
\item Improved application performance by 30\% through code optimization
\item Collaborated with cross-functional teams to deliver high-quality software
\end{itemize}
}

\section{Projects}
\cventry{2021}{Project Name}{}{}{}{
\begin{itemize}
\item Developed a full-stack application using React, Node.js, and MongoDB
\item Implemented authentication and authorization using JWT
\item Deployed the application using Docker and AWS
\end{itemize}
}

\section{Skills}
\cvitem{Languages}{Python, JavaScript, Java, C++, SQL}
\cvitem{Frameworks}{React, Node.js, Express, Django, Flask}
\cvitem{Tools}{Git, Docker, AWS, Jenkins, Jira}
\cvitem{Databases}{PostgreSQL, MongoDB, Redis}

\end{document}
"""
        
        # Ensure the directory exists
        path.parent.mkdir(exist_ok=True, parents=True)
        
        # Write the template
        with open(path, 'w', encoding='utf-8') as file:
            file.write(template_content)
    
    async def _generate_content(self, optimized_data: Dict[str, Any], domain: str) -> str:
        """Generate the content for the LaTeX document based on optimized data"""
        content = ""
        
        # Education Section
        if optimized_data.get("education"):
            content += self._generate_education_section(optimized_data["education"])
        
        # Experience Section
        if optimized_data.get("experience"):
            content += self._generate_experience_section(optimized_data["experience"])
        
        # Projects Section
        if optimized_data.get("projects"):
            content += self._generate_projects_section(optimized_data["projects"])
        
        # Skills Section
        if optimized_data.get("skills"):
            content += self._generate_skills_section(optimized_data["skills"], domain)
        
        # Publications Section (important for research/academic positions)
        if optimized_data.get("publications"):
            content += self._generate_publications_section(optimized_data["publications"])
        
        # Awards Section
        if optimized_data.get("awards"):
            content += self._generate_awards_section(optimized_data["awards"])
        
        return content
    
    def _generate_education_section(self, education_data: List[Dict[str, Any]]) -> str:
        """Generate LaTeX for the education section"""
        content = self.latex_commands["section"].format("Education")
        
        for edu in education_data:
            if isinstance(edu, dict):
                # For structured education entries
                degree = edu.get("degree", "")
                institution = edu.get("institution", "")
                location = edu.get("location", "")
                date = edu.get("date", "")
                gpa = edu.get("gpa", "")
                
                # Use cventry or similar command from template
                content += f"\\cventry{{{date}}}{{{degree}}}{{{institution}}}{{{location}}}{{}}{{{gpa}}}\n"
            else:
                # For plain text education entries
                content += f"\\cvitem{{}}{{{edu}}}\n"
        
        return content
    
    def _generate_experience_section(self, experience_data: List[Dict[str, Any]]) -> str:
        """Generate LaTeX for the experience section"""
        content = self.latex_commands["section"].format("Experience")
        
        for exp in experience_data:
            role = exp.get("role", "")
            company = exp.get("company", "")
            duration = exp.get("duration", "")
            description = exp.get("description", "")
            
            # Use cventry for the experience item
            content += f"\\cventry{{{duration}}}{{{role}}}{{{company}}}{{}}{{}}{{\n"
            
            # Add description as bullet points
            if description:
                content += self.latex_commands["itemize_begin"]
                
                # Split description into bullet points if it contains line breaks
                for line in description.split("\n"):
                    if line.strip():
                        content += self.latex_commands["item"].format(line.strip())
                
                content += self.latex_commands["itemize_end"]
            
            content += "}\n"
        
        return content
    
    def _generate_projects_section(self, projects_data: List[Dict[str, Any]]) -> str:
        """Generate LaTeX for the projects section"""
        content = self.latex_commands["section"].format("Projects")
        
        for proj in projects_data:
            title = proj.get("title", "")
            technologies = proj.get("technologies", "")
            description = proj.get("description", "")
            achievements = proj.get("achievements", "")
            
            # Use cventry for the project item
            content += f"\\cventry{{}}{{{title}}}{{{technologies}}}{{}}{{}}{{\n"
            
            # Add description and achievements as bullet points
            content += self.latex_commands["itemize_begin"]
            
            # Add description bullet points
            if description:
                for line in description.split("\n"):
                    if line.strip():
                        content += self.latex_commands["item"].format(line.strip())
            
            # Add achievements with emphasis
            if achievements:
                for line in achievements.split("\n"):
                    if line.strip():
                        content += self.latex_commands["item"].format(f"\\textit{{Achievement:}} {line.strip()}")
            
            content += self.latex_commands["itemize_end"]
            content += "}\n"
        
        return content
    
    def _generate_skills_section(self, skills_data: Dict[str, List[str]], domain: str) -> str:
        """Generate LaTeX for the skills section"""
        content = self.latex_commands["section"].format("Skills")
        
        # Handle missing skills recommendations
        missing_skills = skills_data.pop("_missing_skills", []) if "_missing_skills" in skills_data else []
        
        # Generate content for each skill category
        for category, skills in skills_data.items():
            # Format the skills as a comma-separated list
            skills_text = ", ".join(skills)
            
            # Use cvitem for each category
            content += f"\\cvitem{{{category}}}{{{skills_text}}}\n"
        
        return content
    
    def _generate_publications_section(self, publications_data: List[Dict[str, Any]]) -> str:
        """Generate LaTeX for the publications section"""
        if not publications_data:
            return ""
            
        content = self.latex_commands["section"].format("Publications")
        
        for pub in publications_data:
            if isinstance(pub, dict):
                # For structured publication entries
                title = pub.get("content", "")
                content += f"\\cvitem{{}}{{{title}}}\n"
            else:
                # For plain text publication entries
                content += f"\\cvitem{{}}{{{pub}}}\n"
        
        return content
    
    def _generate_awards_section(self, awards_data: List[Dict[str, Any]]) -> str:
        """Generate LaTeX for the awards section"""
        if not awards_data:
            return ""
            
        content = self.latex_commands["section"].format("Awards \\& Achievements")
        
        for award in awards_data:
            if isinstance(award, dict):
                # For structured award entries
                title = award.get("content", "")
                content += f"\\cvitem{{}}{{{title}}}\n"
            else:
                # For plain text award entries
                content += f"\\cvitem{{}}{{{award}}}\n"
        
        return content
    
    def _update_contact_info(self, template_content: str, contact_info: Dict[str, str]) -> str:
        """Update contact information in the LaTeX template"""
        modified_content = template_content
        
        # Update name
        if "name" in contact_info:
            name_parts = contact_info["name"].split(" ", 1)
            if len(name_parts) == 2:
                first_name, last_name = name_parts
                modified_content = re.sub(
                    r'\\name{.*?}{.*?}',
                    f'\\name{{{first_name}}}{{{last_name}}}',
                    modified_content
                )
            else:
                modified_content = re.sub(
                    r'\\name{.*?}{.*?}',
                    f'\\name{{{contact_info["name"]}}}{{}}',
                    modified_content
                )
        
        # Update email
        if "email" in contact_info:
            modified_content = re.sub(
                r'\\email{.*?}',
                f'\\email{{{contact_info["email"]}}}',
                modified_content
            )
        
        # Update phone
        if "phone" in contact_info:
            modified_content = re.sub(
                r'\\phone{.*?}',
                f'\\phone{{{contact_info["phone"]}}}',
                modified_content
            )
        
        # Update LinkedIn
        if "linkedin" in contact_info:
            modified_content = re.sub(
                r'\\social\[linkedin\]{.*?}',
                f'\\social[linkedin]{{{contact_info["linkedin"]}}}',
                modified_content
            )
        
        # Update GitHub
        if "github" in contact_info:
            modified_content = re.sub(
                r'\\social\[github\]{.*?}',
                f'\\social[github]{{{contact_info["github"]}}}',
                modified_content
            )
        
        return modified_content
