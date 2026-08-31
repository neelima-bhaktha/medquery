import argparse
import logging
import os
import sys

# pyrefly: ignore [missing-import]
from src.config.settings import DEFAULT_OUTPUT_FILE, OUTPUT_DIR
# pyrefly: ignore [missing-import]
from src.config.validation import validate_config
# pyrefly: ignore [missing-import]
from src.crew import run_medical_crew

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")


def main():
    # Validate startup environment configuration first
    try:
        validate_config(strict=True)
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="MedQuery CrewAI Multi-Agent Medical Assistant")
    parser.add_argument(
        "--query",
        type=str,
        help="Medical query, drug name, or condition (e.g. 'ibuprofen dosage and side effects')",
    )
    args = parser.parse_args()

    query = args.query
    if not query:
        query = input("Enter medical query: ").strip()

    if not query:
        print("Error: No medical query provided. Exiting.")
        sys.exit(1)

    print("\n=======================================================")
    print("       MedQuery CrewAI Medical Research Assistant       ")
    print("=======================================================")
    print(f"Query: {query}\n")

    try:
        report = run_medical_crew(query)

        # Save generated report to outputs/ directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(DEFAULT_OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(report)

        print("\n=======================================================")
        print("               FINAL MEDICAL REPORT                   ")
        print("=======================================================\n")
        print(report)
        print(f"\nReport successfully saved to: {DEFAULT_OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
