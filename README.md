# AI Recruitment Screening Assistant

An AI-powered recruitment assistant built with Python to help HR teams organize job applications, extract structured information from resumes, analyze job requirements, and support evidence-based candidate screening.

The system is designed to assist human reviewers rather than make final hiring decisions.

## 1. Project Overview

Recruitment teams often receive large numbers of CVs for a single job opening. Manually reviewing each application can be time-consuming and makes it difficult to compare candidates consistently.

The AI Recruitment Screening Assistant aims to simplify this process by combining email and document processing, Large Language Models (LLMs), semantic similarity, rule-based comparison, and a user interface for HR review.

The intended workflow is:

**Create a Job → Extract Requirements → Review Must-Have Criteria → Collect CVs → Extract Candidate Information → Match Requirements → Filter and Rank Candidates → HR Review**

The project is organized into separate components for document processing, AI operations, backend services, and the user interface.

## 2. Project Objectives

- Reduce repetitive manual work during initial CV screening.
- Extract structured information from resumes and job descriptions.
- Compare candidate qualifications against individual job requirements.
- Identify missing or insufficient evidence.
- Separate mandatory criteria from preferred qualifications.
- Organize candidate results for easier HR review.
- Provide a clear interface for reviewing results and recording decisions.
- Keep final recruitment decisions under human control.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Gmail API | Accessing recruitment emails and attachments |
| Google Cloud | Configuring Gmail API access |
| OAuth 2.0 | Authorizing Gmail access |
| OpenRouter API | Accessing a compatible language model |
| OpenAI Python SDK | Sending requests to the configured OpenRouter endpoint |
| pypdf | Extracting text from PDF files |
| python-docx | Extracting text from DOCX files |
| Hugging Face Sentence Transformers | Generating text embeddings, where implemented |
| Cosine Similarity | Measuring semantic similarity, where implemented |
| FastAPI | Building backend HTTP endpoints |
| Pydantic | Validating API requests and responses |
| Uvicorn | Running the FastAPI application |
| Streamlit | Building the HR interface |
| Requests | Communicating between the frontend and backend |
| Pandas | Organizing candidate results in tables |
| JSON | Representing structured information and screening results |
| python-dotenv | Loading configuration from environment variables, where used |
| Git and GitHub | Version control and project hosting |

## 4. Project Structure

The following structure represents the intended organization of the complete project. Adjust filenames to match the files actually present in the submitted repository.

```text
AI-Recruitment-Assistant/
│
├── AI/
│   ├── AI.py
│   ├── comparison.py
│   ├── similarity.py
│   └── ranking.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   └── services.py
│
├── frontend/
│   └── app.py
│
├── gmail_and_files/
│   ├── gmail.py
│   └── files.py
│
├── code/
│   ├── AI.py
│   ├── files.py
│   ├── gmail.py
│   ├── job_description.py
│   ├── job_description.txt
│   ├── main.py
│   ├── test.py
│   └── test_job_description.py
│
├── main.py
├── rank_results.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

**Note:** The `code/` directory represents the original processing implementation described in this project documentation. Avoid duplicating files in the repository if they have already been moved into the newer module structure.

### Main Components

- **AI:** AI-based information extraction, requirement comparison, similarity calculations, and ranking logic.
- **backend:** FastAPI endpoints, data validation, and application services.
- **frontend:** Streamlit pages for job management, candidate screening, and HR review.
- **gmail_and_files:** Gmail integration, attachment handling, and document extraction.
- **code:** Original processing scripts and tests, if retained.
- **rank_results.py:** Entry point for ranking operations, if implemented in this script.

## 5. Project Setup

The project uses Python and a virtual environment to isolate its dependencies.

### Prerequisites

- Python 3.
- Git.
- Visual Studio Code or another Python IDE.
- Gmail API credentials, if Gmail integration is used.
- An OpenRouter API key and a supported model, if using the OpenRouter-based implementation.
- Dependencies for FastAPI and Streamlit if those components are included in the submitted version.

### Create a Virtual Environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install the project's dependencies:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include all packages required by the final implementation.

## 6. Gmail Integration

The Gmail integration is intended to retrieve recruitment emails and identify candidate CV attachments.

The integration uses the Gmail API and OAuth 2.0 authorization.

The setup process includes:

1. Creating a Google Cloud project.
2. Enabling the Gmail API.
3. Configuring OAuth consent and credentials.
4. Authorizing the application to access the HR Gmail account.
5. Using the appropriate read-only permission when only reading emails and attachments is required.
6. Retrieving relevant email messages and their metadata.

OAuth tokens should be stored locally and protected from unauthorized access.

The application must not request unnecessary Gmail permissions or expose credentials in source code.

## 7. Email Processing and CV Attachments

The email-processing stage identifies relevant application messages and prepares supported attachments for document extraction.

The intended process includes:

1. Searching for recruitment emails using Gmail search operators.
2. Reading message identifiers, senders, subjects, and attachment metadata.
3. Identifying PDF and DOCX attachments.
4. Downloading supported attachments.
5. Decoding attachment content.
6. Skipping unsupported or unusable files.
7. Tracking processed message IDs to reduce duplicate processing.

The application should handle multiple attachments per message and continue processing other applications when an individual file fails.

The exact level of automation depends on the Gmail integration implemented in the submitted version.

## 8. CV Text Extraction

The application extracts text from supported CV documents before passing their contents to the AI processing stage.

### Supported Formats

- PDF using `pypdf`.
- DOCX using `python-docx`.

The extraction stage should:

- Read document contents.
- Combine extracted text into a consistent string.
- Remove unnecessary whitespace.
- Detect empty or unreadable documents.
- Handle extraction errors.
- Preserve relevant candidate and source-file information.

Scanned PDF files may require OCR because `pypdf` does not automatically recognize text contained only in document images.

The extracted text becomes the input for candidate information extraction.

## 9. Job Description Preparation

A job description defines the qualifications and requirements associated with a position.

The system can use a text file or structured data to provide the job description to the AI component.

Relevant information includes:

- Job title.
- Required technical skills.
- Required experience.
- Education.
- Languages.
- Certifications.
- Mandatory qualifications.
- Preferred qualifications.

The extracted requirements should be organized into a consistent structure so they can be evaluated individually.

HR should be able to review the extracted requirements and identify which ones are mandatory before candidate screening begins.

## 10. AI-Based Information Extraction

The AI component transforms unstructured text into structured information that other parts of the application can process.

### Job Description Extraction

The model is instructed to identify:

- Job title.
- Required skills.
- Experience requirements.
- Education requirements.
- Languages.
- Certifications.
- Mandatory and preferred qualifications.

### Candidate Information Extraction

The model analyzes CV text to identify information such as:

- Name and contact details, when available.
- Technical skills.
- Work experience.
- Education.
- Languages.
- Certifications.

The information is organized into structured JSON data.

The application uses an AI model through the configured API integration. Extraction quality depends on the input text, the model, and the prompts used.

The system should not assume a candidate possesses a skill or qualification simply because the AI considers it likely. Missing information should be marked as unavailable or requiring review.

## 11. Initial CV-to-Job Matching

The matching component compares extracted candidate information with the requirements of a job.

Each requirement should be evaluated individually rather than relying only on a single overall similarity score.

### Rule-Based Comparison

Rule-based checks can evaluate explicit requirements, such as whether a specified certification or qualification is documented.

### Semantic Similarity

Where implemented, Sentence Transformers generate embeddings that represent the meaning of text.

An embedding model such as `sentence-transformers/all-MiniLM-L6-v2` can be used to compare job requirements with relevant candidate information.

Cosine similarity measures how similar two embedding vectors are.

Semantic similarity is useful when a CV expresses relevant experience using wording different from the job description.

However, semantic similarity alone cannot confirm that a requirement is satisfied. The result should be combined with structured information, appropriate rules, and supporting evidence.

### Matching Categories

The intended categories are:

- **Meets:** Sufficient evidence supports the requirement.
- **Partially Meets:** The evidence supports only part of the requirement.
- **Does Not Meet:** The available evidence does not establish that the requirement is satisfied.

The results should include relevant evidence from the CV whenever possible. Missing evidence should be distinguished from a confirmed absence of a qualification.

## 12. Candidate Filtering and Ranking

After evaluating candidate requirements, the system can organize the results to help HR prioritize applications.

### Must-Have Requirements

Mandatory requirements are evaluated separately from preferred qualifications.

Candidates who do not satisfy all mandatory requirements can be placed in a separate group for further review.

They should remain accessible to HR rather than being permanently discarded based solely on an automated assessment.

### Candidate Ranking

Candidates who satisfy the configured mandatory requirements can be ranked according to their results for preferred requirements and other relevant qualifications.

The ranking logic may combine:

- Requirement-level matching results.
- Structured candidate information.
- Rule-based checks.
- Semantic similarity measurements, where implemented.

Scoring weights should be documented and configurable where appropriate.

A similarity score or ranking position should not be presented as a probability of job performance or as a definitive measure of a candidate's value.

### Ranking Output

The intended output includes:

- Candidate information.
- Matching results.
- Available scores.
- Ranking categories.
- Missing requirements.
- Supporting evidence.

The purpose of ranking is to help HR organize reviews, not to automate the final hiring decision.

## 13. Organizing and Saving Results

The application organizes extracted information and screening results into structured data that can be retrieved by the interface.

Potential data fields include:

- Candidate information.
- Source email or message ID.
- Resume filename.
- Extracted skills and qualifications.
- Job requirements.
- Requirement-level matching results.
- Ranking scores and categories.
- HR decisions and notes.

JSON is suitable for structured data exchange and simple prototype storage. A database can provide stronger persistence as the application grows.

The implementation should avoid duplicate candidate records and preserve the relationship between a candidate, the relevant job, and the original application.

The exact storage mechanism depends on the current implementation. In-memory records, JSON files, and database-backed persistence have different durability characteristics and should not be treated as interchangeable.

## 14. Backend API and User Interface

### 14.1 FastAPI Backend

FastAPI provides the HTTP API used to connect the frontend with the application logic.

The backend is responsible for validating requests, invoking the appropriate processing operations, and returning structured responses.

Depending on the implemented endpoints, its responsibilities include:

- Retrieving available jobs.
- Creating or managing job descriptions.
- Screening CV text against a job description.
- Retrieving candidate records.
- Retrieving screening and ranking results.
- Retrieving saved HR decisions.
- Updating candidate decisions and notes.

Pydantic schemas define the expected request and response structures.

Uvicorn runs the FastAPI application.

If the application instance is named `app` in `backend/main.py`, the backend can be started with:

```bash
uvicorn backend.main:app --reload
```

The API documentation is then available at:

```text
http://127.0.0.1:8000/docs
```

The command and endpoints must match the actual backend files.

### 14.2 Streamlit Frontend

Streamlit provides the user interface for interacting with the recruitment assistant.

The interface is designed to organize the main recruitment tasks into accessible pages and sections.

#### Job Management

- Enter a job title and job description.
- Create a job using the available backend functionality.
- Retrieve available jobs.
- Review job information used for screening.

#### Candidate Screening

- View saved candidate records.
- Upload a PDF, DOCX, or TXT CV for individual screening, where supported.
- Select an available job description.
- Submit extracted CV text to the backend.
- Display the returned screening results.

#### Candidate Review

- Display candidate names and available contact information.
- Show available scores and ranking categories.
- Review extracted qualifications.
- Inspect matching information and missing evidence.
- Display a recorded resume filename when available.

#### HR Decisions

- Select a candidate.
- Record a decision as `Shortlist`, `Review Later`, or `Reject`.
- Add notes for future review.
- Retrieve previously saved decisions where supported.

The interface uses `requests` to send HTTP requests to FastAPI and Pandas to organize candidate information into tables.

### 14.3 Frontend-Backend Communication

The application follows a client-server architecture:

```text
HR User
   |
   v
Streamlit Frontend
   |
   | HTTP Requests
   v
FastAPI Backend
   |
   v
Application Services
   |
   v
AI Extraction / Matching / Ranking
   |
   v
Structured API Response
   |
   v
Streamlit Displays Results
```

This separation allows the user interface and application logic to be developed and tested independently.

### 14.4 Current Implementation Boundaries

The final submission should distinguish between working functionality and planned extensions.

Depending on the current code, the following areas may require additional integration:

- Completing automated Gmail ingestion through to candidate screening.
- Persisting all job and candidate records reliably.
- Saving individual screening results into the ranked-candidate collection.
- Providing an endpoint to retrieve or download original CV files.
- Ensuring that must-have filtering and ranking are connected to the user interface.
- Adding comprehensive API and end-to-end tests.

Only describe these features as completed when they have been implemented and tested.

## 15. Configuration

Create a local `.env` file if the application reads configuration from environment variables.

Example:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_supported_model
```

Replace the example values with the credentials and model identifier required by the implementation.

Gmail OAuth credentials may also be required, depending on the configuration.

**Never commit API keys, OAuth credentials, authentication tokens, private CVs, or other sensitive information to a public GitHub repository.**

A `.env.example` file can document required variable names without containing real secrets.

## 16. Running the Application

The commands below are examples and must match the actual entry points in the repository.

### Run the Original Processing Pipeline

```bash
python code/main.py
```

Use this command only if `code/main.py` is the entry point for the original processing pipeline.

### Run the Backend

```bash
uvicorn backend.main:app --reload
```

### Run the Frontend

If the Streamlit entry point is `frontend/app.py`:

```bash
streamlit run frontend/app.py
```

Start the backend before using frontend features that require API communication.

### Run Existing Tests

For example:

```bash
python code/test_job_description.py
```

Additional tests should be run according to the actual test files in the repository.

## 17. Testing

The project should be tested using different job descriptions and representative CV documents.

Important test cases include:

- Valid PDF and DOCX files.
- Empty or corrupted documents.
- Unsupported attachment formats.
- Documents containing little or no extractable text.
- Missing candidate information.
- Requirements expressed using different wording.
- Candidates with missing mandatory qualifications.
- Duplicate email messages.
- Invalid API requests.
- Backend connection failures.
- Saving and retrieving HR decisions.

Tests should verify that the application handles errors safely and that the results remain understandable to human reviewers.

## 18. Limitations

- AI extraction can produce incomplete or incorrect information.
- Semantic similarity does not prove that a candidate meets a qualification.
- Scanned PDFs may require OCR.
- Gmail API quotas and authentication problems can affect email retrieval.
- Ranking quality depends on the configured criteria and scoring logic.
- Complete automation requires the Gmail, extraction, matching, ranking, storage, and interface components to be integrated.
- Original CV downloads require appropriate backend support.
- Sensitive candidate information requires appropriate access controls and data protection.

## 19. Privacy and Responsible Use

The system is intended to assist HR teams, not replace their judgment.

The project should:

- Use authorized Gmail access.
- Protect credentials and authentication tokens.
- Restrict access to candidate information.
- Avoid exposing sensitive data in logs or public interfaces.
- Use synthetic or appropriately anonymized CVs during development.
- Provide supporting evidence for screening results.
- Allow human reviewers to inspect and challenge AI-generated assessments.
- Keep final hiring decisions with authorized human reviewers.

## 20. Future Improvements

Potential improvements include:

- Completing the end-to-end Gmail screening workflow.
- Adding database-backed persistence.
- Improving duplicate detection and recovery from processing errors.
- Supporting OCR for scanned resumes.
- Strengthening structured output validation.
- Improving evidence-based matching.
- Making ranking criteria configurable and transparent.
- Adding automated backend and end-to-end tests.
- Improving secure access controls and deployment.

## 21. Conclusion

The AI Recruitment Screening Assistant combines Python-based document processing, AI information extraction, requirement comparison, candidate organization, and a web interface to support recruitment screening.

Its architecture separates the AI logic, backend API, email and file processing, and user interface to make the project easier to test and extend.

The system aims to help HR teams review applications more efficiently while keeping screening results understandable and final hiring decisions under human control.

## Author

**Hamza Abu Samra**

GitHub: [hamzaabusamra16-boop](https://github.com/hamzaabusamra16-boop)

Project Repository: [AI-Recruitment-Assistant](https://github.com/hamzaabusamra16-boop/AI-Recruitment-Assistant)

