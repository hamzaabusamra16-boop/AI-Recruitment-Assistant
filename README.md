# AI Recruitment Screening Assistant

An AI-powered recruitment assistant that automates the collection and initial processing of job applications, extracts structured information from resumes, and organizes job requirements for human review.

## Overview

The AI Recruitment Screening Assistant is a Python project designed to help simplify the initial recruitment screening workflow.

It connects to Gmail to retrieve application emails, downloads supported resume attachments, extracts text from PDF and DOCX files, and uses an AI model to convert resume content and job descriptions into structured JSON data.

The system is designed to support recruiters by organizing information. It does not make final hiring decisions.

## Features

- **Gmail Integration:** Connects to Gmail through the Gmail API using OAuth 2.0 authentication.
- **Email Processing:** Retrieves email messages and processes their attachments.
- **Resume Downloading:** Downloads supported PDF and DOCX attachments.
- **Text Extraction:** Extracts text from PDF and DOCX resume files.
- **AI-Powered Resume Extraction:** Extracts candidate information, including skills, education, experience, languages, and certificates.
- **Job Description Analysis:** Extracts job titles, required skills, education, languages, mandatory requirements, and optional qualifications.
- **Structured JSON Output:** Saves extracted candidate information and job requirements as JSON.
- **Duplicate Prevention:** Tracks processed email message IDs to reduce repeated processing.
- **Error Handling:** Handles certain processing errors and skips files with no readable text.

## Technologies Used

- Python
- Gmail API
- OAuth 2.0
- OpenRouter API
- OpenAI Python SDK
- PDF text extraction with `pypdf`
- DOCX text extraction with `python-docx`
- JSON
- Python virtual environments
- Git and GitHub

## Project Structure

```text
code/
├── AI.py
├── files.py
├── gmail.py
├── job_description.py
├── job_description.txt
├── main.py
├── test.py
├── test_job_description.py
├── .gitignore
└── results/
    ├── candidates.json
    └── job_requirements.json
```

Generated files, authentication tokens, API credentials, and private candidate data should remain excluded from version control.

## How It Works

1. Authenticate with Gmail through OAuth 2.0.
2. Retrieve application emails.
3. Find and download supported PDF and DOCX attachments.
4. Extract readable text from each resume.
5. Send resume text to an AI model for structured information extraction.
6. Analyze a job description using the AI model.
7. Save the extracted information as JSON for review.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/hamzaabusamra16-boop/AI-Recruitment-Assistant.git
cd AI-Recruitment-Assistant
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the Python packages required by the project:

```bash
pip install openai python-dotenv google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 pypdf python-docx
```

### 4. Configure environment variables

Create a `.env` file in the project directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_supported_model
```

Replace the example values with your own credentials and a model supported by your OpenRouter account.

**Security:** Never commit `.env`, `credentials.json`, `token.json`, or `token.pickle` to GitHub.

### 5. Configure Gmail API

- Create or select a project in Google Cloud.
- Enable the Gmail API.
- Configure OAuth consent and create OAuth credentials.
- Place the required `credentials.json` file in the project directory.
- Use the read-only Gmail scope required by the application.

The application may require browser-based authorization to create or refresh its local authentication token.

### 6. Run the application

```bash
python main.py
```

To test job description extraction:

```bash
python test_job_description.py
```

## Output

The application can generate structured JSON containing:

- Candidate contact information, when available in the resume.
- Skills, education, experience, languages, and certificates.
- Job titles and extracted job requirements.
- Mandatory and optional qualifications.
- Information that is missing from the source text.

Actual output depends on the content of the resume, job description, and AI model response.

## Limitations

- Extraction quality depends on the readability and formatting of the source documents.
- Scanned PDFs may require OCR support if they do not contain extractable text.
- Gmail API quota limits can interrupt processing.
- AI-extracted information should be reviewed for accuracy.
- The current project focuses on information extraction and organization, not automated candidate ranking or final hiring decisions.

## Privacy and Responsible Use

- Use appropriate authorization when accessing Gmail messages.
- Protect API keys, OAuth credentials, authentication tokens, and candidate information.
- Use synthetic or appropriately anonymized resumes for development and testing.
- Keep human reviewers responsible for recruitment decisions.

## Future Improvements

- More robust Gmail API quota handling and retries.
- Expanded automated tests for corrupted, empty, and unsupported files.
- Improved logging and recovery from partial processing failures.
- OCR support for scanned resumes.
- More comprehensive validation of extracted JSON data.

## Author

Hamza Abu Samra

GitHub: [hamzaabusamra16-boop](https://github.com/hamzaabusamra16-boop)
