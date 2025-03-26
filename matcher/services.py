import json
from typing import Dict, List, Optional
import google.generativeai as genai
from django.conf import settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def parse_resume(text: str) -> Dict:
    """Parse resume text using Gemini to extract structured data."""
    try:
        if not text or len(text.strip()) == 0:
            raise ValueError("Empty resume text provided")

        prompt = f"""Parse this resume text into structured JSON with the following format:
        {{
            "name": "string",
            "skills": ["string"],
            "education": [
                {{
                    "degree": "string",
                    "institution": "string",
                    "year": "string"
                }}
            ],
            "work_experience": [
                {{
                    "company": "string",
                    "position": "string",
                    "duration": "string",
                    "description": "string"
                }}
            ]
        }}

        Resume text:
        {text}

        Return only the JSON object, no additional text or explanation."""

        response = model.generate_content(prompt)
        print("Raw response from Gemini:", response.text)  # Debug log
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
            
        # Try to clean the response text if needed
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            parsed_data = json.loads(response_text)
            # Validate required fields
            required_fields = ['name', 'skills', 'education', 'work_experience']
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Missing required field: {field}")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text that failed to parse: {response_text}")
            raise Exception(f"Failed to parse JSON response: {str(e)}")
            
    except Exception as e:
        print(f"Error in parse_resume: {str(e)}")  # Debug log
        raise Exception(f"Error parsing resume: {str(e)}")

def match_candidate_to_job(candidate_data: Dict, job_data: Dict) -> Dict:
    """Match candidate profile with job posting using Gemini."""
    try:
        prompt = f"""Analyze this candidate profile against the job requirements and return a JSON object with:
        {{
            "match_score": integer (0-100),
            "missing_skills": ["string"],
            "summary": "string"
        }}

        Candidate Profile:
        {json.dumps(candidate_data, indent=2)}

        Job Posting:
        {json.dumps(job_data, indent=2)}

        Return only the JSON object, no additional text or explanation."""

        response = model.generate_content(prompt)
        print("Raw response from Gemini (match):", response.text)  # Debug log
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
            
        # Try to clean the response text if needed
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            parsed_data = json.loads(response_text)
            # Validate required fields
            required_fields = ['match_score', 'missing_skills', 'summary']
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Missing required field: {field}")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text that failed to parse: {response_text}")
            raise Exception(f"Failed to parse JSON response: {str(e)}")
            
    except Exception as e:
        print(f"Error in match_candidate_to_job: {str(e)}")  # Debug log
        raise Exception(f"Error matching candidate to job: {str(e)}")

def generate_cover_letter(candidate_data: Dict, job_data: Dict) -> Dict:
    """Generate a personalized cover letter using Gemini."""
    try:
        prompt = f"""Generate a professional cover letter based on this candidate profile and job posting.
        Return a JSON object with:
        {{
            "cover_letter": "string"
        }}

        Candidate Profile:
        {json.dumps(candidate_data, indent=2)}

        Job Posting:
        {json.dumps(job_data, indent=2)}

        Return only the JSON object, no additional text or explanation."""

        response = model.generate_content(prompt)
        print("Raw response from Gemini (cover letter):", response.text)  # Debug log
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
            
        # Try to clean the response text if needed
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            parsed_data = json.loads(response_text)
            # Validate required fields
            if 'cover_letter' not in parsed_data:
                raise ValueError("Missing cover_letter field in response")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text that failed to parse: {response_text}")
            raise Exception(f"Failed to parse JSON response: {str(e)}")
            
    except Exception as e:
        print(f"Error in generate_cover_letter: {str(e)}")  # Debug log
        raise Exception(f"Error generating cover letter: {str(e)}") 