import streamlit as st
import requests
import json
import os
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints
API_BASE_URL = "http://127.0.0.1:8000/api"

def check_api_connection():
    """Check if the Django API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def upload_resume(file):
    """Upload resume and get candidate profile"""
    try:
        logger.info(f"Preparing to upload file: {file.name}, size: {file.size} bytes")
        
        # Prepare the file for upload
        files = {'resume': file}
        
        # Send request to API
        logger.info("Sending request to API...")
        response = requests.post(f"{API_BASE_URL}/candidates/upload_resume/", files=files)
        
        # Log response details
        logger.info(f"API Response Status: {response.status_code}")
        logger.info(f"API Response Headers: {response.headers}")
        
        if response.status_code == 201:
            logger.info("Resume uploaded successfully")
            return response.json()
        else:
            logger.error(f"Error uploading resume: {response.text}")
            error_msg = f"Error uploading resume: {response.text}"
            st.error(error_msg)
            return None
            
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to the server. Please make sure the Django server is running."
        logger.error(error_msg)
        st.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"Error uploading resume: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

def get_jobs():
    """Get all job postings"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        st.error(f"Error fetching jobs: {str(e)}")
        return []

def match_candidate(candidate_id, job_id):
    """Match candidate with job"""
    try:
        logger.info(f"Matching candidate {candidate_id} with job {job_id}")
        data = {
            'candidate_id': candidate_id,
            'job_id': job_id
        }
        response = requests.post(f"{API_BASE_URL}/matches/match_candidate/", json=data)
        response.raise_for_status()
        logger.info(f"Match response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error matching candidate: {str(e)}")
        st.error(f"Error matching candidate: {str(e)}")
        return None

def generate_cover_letter(match_id):
    """Generate cover letter for a match"""
    try:
        logger.info(f"Generating cover letter for match {match_id}")
        response = requests.post(f"{API_BASE_URL}/matches/{match_id}/generate_cover_letter/")
        response.raise_for_status()
        logger.info(f"Cover letter response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        st.error(f"Error generating cover letter: {str(e)}")
        return None

def main():
    st.title("AI Resume & Job Matcher")
    
    # Initialize session state
    if 'candidate_data' not in st.session_state:
        st.session_state.candidate_data = None
    if 'processed_resume' not in st.session_state:
        st.session_state.processed_resume = False
    if 'current_match' not in st.session_state:
        st.session_state.current_match = None
    if 'current_job' not in st.session_state:
        st.session_state.current_job = None
    if 'current_match_id' not in st.session_state:
        st.session_state.current_match_id = None
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Cannot connect to the backend API. Please make sure the Django server is running.")
        st.info("To start the Django server, run: `python manage.py runserver` in a terminal")
        return

    # File uploader for resume
    st.header("Upload Your Resume")
    st.write("Supported formats: PDF, DOCX, or TXT")
    uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file is not None and not st.session_state.processed_resume:
        # Show file details
        st.write("File details:")
        st.write(f"- Name: {uploaded_file.name}")
        st.write(f"- Type: {uploaded_file.type}")
        st.write(f"- Size: {uploaded_file.size} bytes")
        
        if st.button("Process Resume"):
            with st.spinner("Processing your resume..."):
                try:
                    # Create an expandable section for debug info
                    with st.expander("Debug Information"):
                        st.write("File Information:")
                        st.json({
                            "name": uploaded_file.name,
                            "type": uploaded_file.type,
                            "size": uploaded_file.size
                        })
                    
                    candidate_data = upload_resume(uploaded_file)
                    if candidate_data:
                        st.session_state.candidate_data = candidate_data
                        st.session_state.processed_resume = True
                        st.success("✅ Resume processed successfully!")
                        
                        # Display parsed data in a more organized way
                        st.subheader("Extracted Information")
                        st.write("**Name:**", candidate_data.get('name', 'N/A'))
                        
                        st.write("**Skills:**")
                        st.write(", ".join(candidate_data.get('skills', [])), sep=', ')
                        
                        st.write("**Education:**")
                        for edu in candidate_data.get('education', []):
                            st.write(f"- {edu.get('degree')} from {edu.get('institution')} ({edu.get('year')})")
                        
                        st.write("**Work Experience:**")
                        for exp in candidate_data.get('work_experience', []):
                            st.write(f"- {exp.get('position')} at {exp.get('company')}")
                            st.write(f"  Duration: {exp.get('duration')}")
                            st.write(f"  {exp.get('description')}")
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Please make sure your resume is in a supported format and contains readable text.")
                    
                    # Show technical details in an expandable section
                    with st.expander("Technical Details"):
                        st.error("Error Details:")
                        st.code(str(e))
                        
                        if hasattr(e, '__cause__') and e.__cause__:
                            st.write("Caused by:")
                            st.code(str(e.__cause__))
    
    # Display stored candidate data if available
    if st.session_state.candidate_data:
        st.subheader("Your Profile")
        candidate_data = st.session_state.candidate_data
        st.write("**Name:**", candidate_data.get('name', 'N/A'))
        st.write("**Skills:**")
        st.write(", ".join(candidate_data.get('skills', [])), sep=', ')
    
    # Job listings
    st.header("Available Jobs")
    jobs = get_jobs()
    
    if jobs and st.session_state.candidate_data:
        for job in jobs:
            with st.expander(f"{job['title']} at {job['company']}"):
                st.write("**Required Skills:**")
                for skill in job['required_skills']:
                    st.write(f"- {skill}")
                st.write("**Description:**")
                st.write(job['description'])
                
                if st.button(f"Match with {job['title']}", key=f"match_{job['id']}"):
                    with st.spinner("Matching your profile with the job..."):
                        match_data = match_candidate(st.session_state.candidate_data['id'], job['id'])
                        if match_data:
                            st.session_state.current_match = match_data
                            st.session_state.current_job = job
                            st.session_state.current_match_id = match_data['id']
                            st.success("Match completed!")
                            
                            # Display match results in a more organized way
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Match Score", f"{match_data['match_score']}%")
                            
                            st.write("**Missing Skills:**")
                            for skill in match_data['missing_skills']:
                                st.write(f"- {skill}")
                            
                            st.write("**Summary:**")
                            st.write(match_data['summary'])
                            
                            # Add a separate section for cover letter generation
                            # st.markdown("---")
                            # st.subheader("Cover Letter")
                            # if st.button("Generate Cover Letter", key="generate_cover"):
                            #     with st.spinner("Generating cover letter..."):
                            #         try:
                            #             cover_letter = generate_cover_letter(st.session_state.current_match_id)
                            #             if cover_letter and 'cover_letter' in cover_letter:
                            #                 st.success("Cover letter generated successfully!")
                                            
                            #                 # Display cover letter in a text area
                            #                 st.text_area("Cover Letter", cover_letter['cover_letter'], height=300)
                                            
                            #                 # Add download button for cover letter
                            #                 st.download_button(
                            #                     "Download Cover Letter",
                            #                     cover_letter['cover_letter'],
                            #                     file_name=f"cover_letter_{st.session_state.current_job['title'].lower().replace(' ', '_')}.txt",
                            #                     mime="text/plain"
                            #                 )
                            #             else:
                            #                 st.error("Failed to generate cover letter. Please try again.")
                            #         except Exception as e:
                            #             st.error(f"Error generating cover letter: {str(e)}")
                            #             logger.error(f"Error generating cover letter: {str(e)}")
    elif jobs:
        st.info("Please upload and process your resume first to see job matches.")
    else:
        st.info("No jobs available. Please add some jobs through the admin interface.")
        st.markdown("[Go to Admin Interface](http://127.0.0.1:8000/admin)")

    # Add a separate section for cover letter if there's a current match
    if st.session_state.current_match:
        st.markdown("---")
        st.subheader("Cover Letter")
        if st.button("Generate Cover Letter", key="generate_cover_global"):
            with st.spinner("Generating cover letter..."):
                try:
                    cover_letter = generate_cover_letter(st.session_state.current_match_id)
                    if cover_letter and 'cover_letter' in cover_letter:
                        st.success("Cover letter generated successfully!")
                        
                        # Display cover letter in a text area
                        st.text_area("Cover Letter", cover_letter['cover_letter'], height=300)
                        
                        # Add download button for cover letter
                        st.download_button(
                            "Download Cover Letter",
                            cover_letter['cover_letter'],
                            file_name=f"cover_letter_{st.session_state.current_job['title'].lower().replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Failed to generate cover letter. Please try again.")
                except Exception as e:
                    st.error(f"Error generating cover letter: {str(e)}")
                    logger.error(f"Error generating cover letter: {str(e)}")

if __name__ == "__main__":
    main() 