import logging
from src.crew import run_medical_crew

logging.basicConfig(level=logging.INFO)

try:
    print("Testing direct run_medical_crew...")
    res = run_medical_crew("paracetamol", sources_context="Paracetamol is a common analgesic used to treat pain and fever.")
    print("\nSUCCESS OUTPUT:\n", res)
except Exception as e:
    print("\nFAILED WITH ERROR:\n", repr(e))
