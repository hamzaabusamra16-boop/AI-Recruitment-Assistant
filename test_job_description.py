
import json
from pathlib import Path
from AI import extract_job_requirements

# Get the directory containing this Python file
BASE_DIR = Path(__file__).resolve().parent

# Define input and output paths
JOB_DESCRIPTION_FILE = BASE_DIR / "job_description.txt"
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_FILE = RESULTS_DIR / "job_requirements.json"


def main():
    # Check whether the job description file exists
    if not JOB_DESCRIPTION_FILE.exists():
        raise FileNotFoundError(
            f"Job description file not found: {JOB_DESCRIPTION_FILE}"
        )

    # Read the job description
    job_description = JOB_DESCRIPTION_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not job_description:
        raise ValueError("The job description file is empty.")

    # Extract structured job requirements using AI
    requirements = extract_job_requirements(job_description)

    # Create the results directory if needed
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save the extracted requirements as JSON
    OUTPUT_FILE.write_text(
        json.dumps(requirements, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Job requirements extracted successfully.")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(json.dumps(requirements, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
