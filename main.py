
import json
from pathlib import Path

from pypdf import PdfReader
from docx import Document

from gmail_and_files.files import get_messages, get_attachments
from gmail_and_files.gmail import get_gmail_service
from AI.AI import screen_candidate
import hashlib
BASE_DIR = Path(__file__).resolve().parent
RESUMES_DIR = BASE_DIR / "resumes"
RESULTS_DIR = BASE_DIR / "results"


ENV_DIR = BASE_DIR / ".env_"
ENV_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_FILE = ENV_DIR / "candidates.json"
PROCESSED_FILE = ENV_DIR / "processed_ids.json"
JOB_DESCRIPTION_FILE = BASE_DIR / "sample_data" / "job_description.txt"
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_json(file_path, default):
    """Load JSON data, or return a default if the file is missing."""

    if not file_path.exists():
        return default

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    """Save data as readable UTF-8 JSON."""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def calculate_file_hash(file_path):
    """Return the SHA-256 hash of a file's contents."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

def read_resume_text(file_path):
    """Extract text from a supported resume file."""

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if suffix == ".docx":
        document = Document(str(file_path))
        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    return None


def main():
    # Load previous results and processed message IDs.
    all_candidates = load_json(RESULTS_FILE, [])
    processed_ids = set(load_json(PROCESSED_FILE, []))

    if not JOB_DESCRIPTION_FILE.exists():
        raise FileNotFoundError(
            f"Job description file not found: {JOB_DESCRIPTION_FILE}"
        )

    job_description = JOB_DESCRIPTION_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not job_description:
        raise ValueError("The job description file is empty.")

    existing_candidates = {
        (item["message_id"], item["resume_file"])
        for item in all_candidates
        if "message_id" in item and "resume_file" in item
    }

    existing_hashes = {
        item["file_hash"]
        for item in all_candidates
        if item.get("file_hash")
    }

    print("Connecting to Gmail...")
    service = get_gmail_service()
    print("Gmail connected successfully.")

    print("Fetching Gmail messages...")
    result = get_messages(service, "me")

    if not result:
        print("Could not retrieve Gmail messages.")
        return

    messages = result.get("messages", [])
    print(f"Found {len(messages)} messages.")

    if not messages:
        print("No messages found.")
        return

    new_candidates = 0
    skipped_messages = 0

    for index, message in enumerate(messages, start=1):
        message_id = message["id"]

        if message_id in processed_ids:
            skipped_messages += 1
            print(f"\nSkipping previously processed message: {message_id}")
            continue

        message_dir = RESUMES_DIR / message_id

        print(
            f"\n[{index}/{len(messages)}] "
            f"Processing message: {message_id}"
        )

        try:
            get_attachments(
                service,
                "me",
                message_id,
                str(message_dir),
            )

            if not message_dir.exists():
                print("No attachment folder was created.")
                continue

            resume_files = [
                path
                for path in message_dir.rglob("*")
                if path.is_file()
                and path.suffix.lower() in {".pdf", ".docx"}
            ]

            if not resume_files:
                print("No supported PDF or DOCX attachments.")
                continue

            message_succeeded = True

            for resume_path in resume_files:

                candidate_key = (message_id, resume_path.name)
                file_hash = calculate_file_hash(resume_path)

                if candidate_key in existing_candidates:
                    print(f"Already extracted: {resume_path.name}")
                    continue

                if file_hash in existing_hashes:
                    print(f"Duplicate resume content: {resume_path.name}")
                    continue
                print(f"Reading resume: {resume_path.name}")

                try:
                    resume_text = read_resume_text(resume_path)

                    if not resume_text or not resume_text.strip():
                        print("No readable text found. Skipping.")
                        message_succeeded = False
                        continue


                    screening_result = screen_candidate(
                        resume_text,
                        job_description
                    )

                    all_candidates.append({
                        "message_id": message_id,
                        "resume_file": resume_path.name,
                        "candidate": screening_result["candidate"],
                        "job_requirements": screening_result["job_requirements"],
                        "comparison": screening_result["comparison"],
                        "semantic_similarity": screening_result["semantic_similarity"],
                        "must_have": screening_result["must_have"],
                        "file_hash": file_hash,
                    })

                    existing_candidates.add(candidate_key)
                    existing_hashes.add(file_hash)
                    new_candidates += 1
                    save_json(RESULTS_FILE, all_candidates)

                    print(
                        "Candidate screened:",
                        screening_result["candidate"].get("name") or "Name not found",
                    )

                except Exception as error:
                    print(
                        f"Failed to process {resume_path.name}: {error}"
                    )
                    message_succeeded = False

            if message_succeeded:
                processed_ids.add(message_id)
                save_json(PROCESSED_FILE, sorted(processed_ids))

        except Exception as error:
            print(f"Failed to process message {message_id}: {error}")

    print("\nProcessing completed.")
    print(f"New candidates extracted: {new_candidates}")
    print(f"Previously processed messages skipped: {skipped_messages}")
    print(f"Total candidates saved: {len(all_candidates)}")
    print(f"Results saved to: {RESULTS_FILE}")
    print(f"Processed IDs saved to: {PROCESSED_FILE}")


if __name__ == "__main__":
    main()
