import re
import json
import os
from typing import Dict, List, Union, Optional

def extract_experience(latex_content: str) -> str:
    """Extract experience sections from a LaTeX resume.

    Args:
        latex_content (str): The LaTeX content of the resume.

    Returns:
        str: JSON string containing extracted experience information.
    """
    print(f"--- Tool: extract_experience called ---") # Log tool execution
    
    if not latex_content:
        return json.dumps({
            "status": "error",
            "error_message": "No LaTeX content provided"
        })
    
    try:
        # Extract experience section using regex
        experience_data = []
        
        # Try to find the Experience section in the LaTeX document
        experience_section = re.search(r'\\section{\s*(?:Experience|Work Experience|Professional Experience)\s*}([\s\S]*?)(?:\\section{|\\end{document})', latex_content)
        
        if not experience_section:
            return json.dumps({
                "status": "error",
                "error_message": "Could not find Experience section in the LaTeX content"
            })
            
        experience_text = experience_section.group(1)
        print(f"Found Experience section with {len(experience_text)} characters")
        
        # Extract content between resumeSubHeadingListStart and resumeSubHeadingListEnd
        if "\\resumeSubHeadingListStart" in experience_text:
            experience_list_match = re.search(r'\\resumeSubHeadingListStart\s*([\s\S]*?)\\resumeSubHeadingListEnd', experience_text)
            if experience_list_match:
                experience_text = experience_list_match.group(1)
                print("Found content between resumeSubHeadingListStart and resumeSubHeadingListEnd")
        
        # Use the successful pattern from our debug script
        job_matches = re.finditer(r'\\resumeSubheading[\s\S]*?{([^}]*)}[\s\S]*?{([^}]*)}[\s\S]*?{([^}]*)}[\s\S]*?{([^}]*)}', experience_text)
        
        job_count = 0
        for job in job_matches:
            job_count += 1
            position = job.group(1).strip()
            date = job.group(2).strip()
            company = job.group(3).strip()
            location = job.group(4).strip()
            
            print(f"Found job #{job_count}: {position} at {company}")
            
            # Find content between this job and the next one (or end)
            match_start = job.end()
            next_match_start = experience_text.find("\\resumeSubheading", match_start)
            if next_match_start == -1:
                job_section = experience_text[match_start:]
            else:
                job_section = experience_text[match_start:next_match_start]
                
            # Extract bullet points
            bullet_points = []
            if "\\resumeItemListStart" in job_section and "\\resumeItemListEnd" in job_section:
                # Get text between resumeItemListStart and resumeItemListEnd
                bullet_section = re.search(r'\\resumeItemListStart\s*([\s\S]*?)\\resumeItemListEnd', job_section)
                if bullet_section:
                    bullet_content = bullet_section.group(1)
                    
                    # Use approach that worked in debug script
                    for line in bullet_content.split("\\resumeItem{"):
                        if line.strip():
                            # Find the closing brace, accounting for nested braces
                            depth = 0
                            closing_pos = -1
                            for i, char in enumerate(line):
                                if char == '{':
                                    depth += 1
                                elif char == '}':
                                    if depth == 0:
                                        closing_pos = i
                                        break
                                    depth -= 1
                            
                            if closing_pos != -1:
                                bullet_text = line[:closing_pos].strip()
                            else:
                                bullet_text = line.strip()
                                
                            if bullet_text:
                                # Clean up LaTeX commands
                                bullet_text = re.sub(r'\\textbf{([^}]+)}', r'\1', bullet_text)
                                bullet_text = re.sub(r'\\emph{([^}]+)}', r'\1', bullet_text)
                                bullet_text = re.sub(r'\\%', '%', bullet_text)
                                bullet_text = re.sub(r'\\&', '&', bullet_text)
                                bullet_points.append(bullet_text)
            
            # Add to experience data
            experience_data.append({
                "position": position,
                "date": date,
                "company": company, 
                "location": location,
                "bullet_points": bullet_points
            })
        
        # Return the structured experience data as JSON
        return json.dumps({
            "status": "success",
            "experience_count": len(experience_data),
            "experience_entries": experience_data
        })
        
    except Exception as e:
        print(f"Error extracting experience: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_message": f"Error parsing LaTeX experience section: {str(e)}"
        })


def get_latex_content(directory_path: str = "", file_name: str = "") -> str:
    """
    Find LaTeX files in the specified directory and return their content.
    If a specific file name is provided, only that file will be read.
    
    Args:
        directory_path (str): Path to the directory to search for LaTeX files.
                             If empty, uses the current working directory.
        file_name (str): Optional specific LaTeX file to read (without the directory path).
                        If provided, only this file will be read.
    
    Returns:
        str: JSON string containing LaTeX content and file information.
    """
    print(f"--- Tool: get_latex_content called ---") # Log tool execution
    
    try:
        # Use current working directory if no directory path provided
        if not directory_path:
            directory_path = os.getcwd()
        
        # Ensure the directory path exists
        if not os.path.isdir(directory_path):
            return json.dumps({
                "status": "error", 
                "error_message": f"Directory not found: {directory_path}"
            })
            
        latex_files = []
        latex_contents = {}
        
        # If specific file name provided, check only that file
        if file_name:
            file_path = os.path.join(directory_path, file_name)
            if not os.path.isfile(file_path):
                return json.dumps({
                    "status": "error",
                    "error_message": f"File not found: {file_path}"
                })
            
            if not file_name.endswith('.tex'):
                return json.dumps({
                    "status": "error",
                    "error_message": f"File is not a LaTeX file: {file_path}"
                })
                
            latex_files = [file_path]
        else:
            # Find all .tex files in the directory
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.tex'):
                        latex_files.append(os.path.join(root, file))
        
        if not latex_files:
            return json.dumps({
                "status": "error",
                "error_message": f"No LaTeX files found in {directory_path}"
            })
        
        # Read the content of each LaTeX file
        for file_path in latex_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Store both the relative path and content
                    rel_path = os.path.relpath(file_path, directory_path)
                    latex_contents[rel_path] = {
                        "file_path": file_path,
                        "content": content,
                        "size": len(content)
                    }
            except Exception as e:
                print(f"Error reading LaTeX file {file_path}: {str(e)}")
        
        # Return the LaTeX content as JSON
        return json.dumps({
            "status": "success",
            "file_count": len(latex_contents),
            "latex_files": latex_contents
        })
        
    except Exception as e:
        print(f"Error in get_latex_content: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_message": f"Error getting LaTeX content: {str(e)}"
        })

                