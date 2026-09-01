import logging
from src.crew import run_medical_crew

logging.basicConfig(level=logging.INFO)

query = "paracetamol"
sources_context = "Paracetamol (acetaminophen) is a widely used over-the-counter pain reliever and fever reducer."

print("Running live medical crew with model 'groq/qwen/qwen3.6-27b'...")
report = run_medical_crew(query, llm="groq/qwen/qwen3.6-27b", sources_context=sources_context)

print("\n--- LIVE GENERATED MEDICAL REPORT ---")
print(report.encode("ascii", "ignore").decode("ascii"))
