from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import PyPDF2
import docx
from .models import CandidateProfile, JobPosting, JobMatch
from .serializers import CandidateProfileSerializer, JobPostingSerializer, JobMatchSerializer
from .services import parse_resume, match_candidate_to_job, generate_cover_letter
import io
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        docx_file = io.BytesIO(file_content)
        doc = docx.Document(docx_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

# Create your views here.

class CandidateProfileViewSet(viewsets.ModelViewSet):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateProfileSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_resume(self, request):
        """Upload and process a resume file."""
        logger.info("Starting resume upload process")
        logger.info(f"Request files: {request.FILES}")
        logger.info(f"Request data: {request.data}")
        
        try:
            if 'resume' not in request.FILES:
                logger.error("No resume file found in request")
                return Response(
                    {'error': 'No resume file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            resume_file = request.FILES['resume']
            logger.info(f"Received file: {resume_file.name}, size: {resume_file.size} bytes")
            
            # Read file content
            try:
                file_content = resume_file.read()
                logger.info(f"Read {len(file_content)} bytes from file")
            except Exception as e:
                logger.error(f"Error reading file: {str(e)}")
                return Response(
                    {'error': f'Error reading file: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract text based on file type
            try:
                if resume_file.name.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(file_content)
                elif resume_file.name.lower().endswith('.docx'):
                    text = extract_text_from_docx(file_content)
                elif resume_file.name.lower().endswith('.txt'):
                    text = file_content.decode('utf-8')
                else:
                    logger.error(f"Unsupported file type: {resume_file.name}")
                    return Response(
                        {'error': 'Unsupported file type. Please upload PDF, DOCX, or TXT files.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                logger.info(f"Extracted text length: {len(text)} characters")
                if not text.strip():
                    logger.error("No text content extracted from file")
                    return Response(
                        {'error': 'No text content found in the file'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                logger.error(f"Error extracting text: {str(e)}")
                return Response(
                    {'error': f'Error extracting text: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse resume using LLM
            try:
                parsed_data = parse_resume(text)
                logger.info(f"Successfully parsed resume data: {json.dumps(parsed_data, indent=2)}")
            except Exception as e:
                logger.error(f"Error parsing resume: {str(e)}")
                return Response(
                    {'error': f'Error parsing resume: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create candidate profile
            try:
                serializer = self.get_serializer(data=parsed_data)
                if serializer.is_valid():
                    serializer.save()
                    logger.info(f"Successfully created candidate profile: {serializer.data}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"Serializer validation errors: {serializer.errors}")
                    return Response(
                        {'error': 'Invalid data format', 'details': serializer.errors}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                logger.error(f"Error creating candidate profile: {str(e)}")
                return Response(
                    {'error': f'Error creating profile: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in upload_resume: {str(e)}")
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer

class JobMatchViewSet(viewsets.ModelViewSet):
    queryset = JobMatch.objects.all()
    serializer_class = JobMatchSerializer

    @action(detail=False, methods=['post'])
    def match_candidate(self, request):
        """Match a candidate with a job posting."""
        logger.info("Starting candidate matching process")
        logger.info(f"Request data: {request.data}")
        
        try:
            candidate_id = request.data.get('candidate_id')
            job_id = request.data.get('job_id')
            
            if not candidate_id or not job_id:
                logger.error("Missing candidate_id or job_id in request")
                return Response(
                    {'error': 'Both candidate_id and job_id are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Looking up candidate {candidate_id} and job {job_id}")
            candidate = get_object_or_404(CandidateProfile, id=candidate_id)
            job = get_object_or_404(JobPosting, id=job_id)
            
            # Get match results using LLM
            logger.info("Getting match results from LLM")
            match_results = match_candidate_to_job(
                CandidateProfileSerializer(candidate).data,
                JobPostingSerializer(job).data
            )
            logger.info(f"Match results: {json.dumps(match_results, indent=2)}")
            
            # Create job match
            match_data = {
                'candidate': candidate.id,
                'job': job.id,
                'match_score': match_results['match_score'],
                'missing_skills': match_results['missing_skills'],
                'summary': match_results['summary']
            }
            
            logger.info(f"Creating job match with data: {json.dumps(match_data, indent=2)}")
            serializer = self.get_serializer(data=match_data)
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Successfully created job match: {json.dumps(serializer.data, indent=2)}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(
                    {'error': 'Invalid data format', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error in match_candidate: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def generate_cover_letter(self, request, pk=None):
        """Generate a cover letter for a job match."""
        try:
            logger.info(f"Starting cover letter generation for match {pk}")
            job_match = self.get_object()
            
            # Generate cover letter using LLM
            logger.info("Getting cover letter from LLM")
            cover_letter_data = generate_cover_letter(
                CandidateProfileSerializer(job_match.candidate).data,
                JobPostingSerializer(job_match.job).data
            )
            
            if not cover_letter_data or 'cover_letter' not in cover_letter_data:
                logger.error("Invalid cover letter data received from LLM")
                return Response(
                    {'error': 'Failed to generate cover letter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info("Successfully generated cover letter")
            return Response(cover_letter_data)
            
        except Exception as e:
            logger.error(f"Error in generate_cover_letter: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
