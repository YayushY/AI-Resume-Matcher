# AI Resume & Job Matcher

An intelligent application that matches candidate resumes with job postings using AI. The application uses Django for the backend API and Streamlit for the frontend interface, powered by Google's Gemini AI model.

## Features

- Resume upload and parsing (supports PDF, DOCX, and TXT formats)
- Job posting management
- AI-powered candidate-job matching using Gemini
- Match score calculation and missing skills analysis
- Personalized cover letter generation

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd resume-matcher
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

5. Run Django migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run streamlit_app.py
```

3. Open your browser and navigate to:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/api/

## API Endpoints

- `POST /api/candidates/upload_resume/` - Upload and parse a resume
- `GET /api/jobs/` - List all job postings
- `POST /api/matches/match_candidate/` - Match a candidate with a job
- `POST /api/matches/{match_id}/generate_cover_letter/` - Generate a cover letter

## Usage

1. Upload your resume through the Streamlit interface
2. View available job postings
3. Click "Match" to see how well your profile matches each job
4. Generate a personalized cover letter for your best matches

