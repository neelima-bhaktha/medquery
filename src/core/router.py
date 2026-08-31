import re
from typing import List

# Common drug suffixes & names for deterministic classification
DRUG_PATTERNS = [
    r"\b(drug|medication|pill|tablet|capsule|dose|dosage|side effect|side-effect|adverse|interaction|prescription)\b",
    r"\b(ibuprofen|acetaminophen|paracetamol|aspirin|metformin|amoxicillin|prednisone|omeprazole|atorvastatin|lisinopril|levothyroxine|albuterol|gabapentin|losartan|simvastatin|ozempic|wegovy|adderall)\b",
    r"\b\w+(cillin|mycin|statin|olol|pril|sartan|zole|prazole|tidine|mab|vir|bam|pam)\b",
]

# Research / Scientific inquiry patterns
RESEARCH_PATTERNS = [
    r"\b(evidence for|clinical trial|randomized|meta-analysis|systematic review|study|cohort|efficacy of|in vitro|mechanism of action|pubmed|doi|journal|abstract|findings|author)\b",
]

# Symptoms & conditions patterns
CONDITION_PATTERNS = [
    r"\b(symptom|symptoms|pain|syndrome|disease|condition|fever|cough|infection|inflammation|diagnosis|treatment|therapy|cause|prevention|recovery|disorder|cancer|diabetes|hypertension|asthma|flu|covid)\b",
]


def classify_query(query: str) -> List[str]:
    """
    Classify query using deterministic rules to select medical sources.

    Rules:
    - Drug/Medication query -> ['openfda', 'medlineplus']
    - Research phrasing -> ['europepmc']
    - Condition/Symptom query -> ['medlineplus', 'europepmc']
    - Fallback -> ['medlineplus', 'europepmc', 'openfda']
    """
    q_lower = query.lower().strip()
    sources = set()

    # Check Research patterns
    for pattern in RESEARCH_PATTERNS:
        if re.search(pattern, q_lower):
            sources.add("europepmc")

    # Check Drug patterns
    is_drug = False
    for pattern in DRUG_PATTERNS:
        if re.search(pattern, q_lower):
            is_drug = True
            sources.add("openfda")
            sources.add("medlineplus")
            break

    # Check Condition/Symptom patterns
    is_condition = False
    for pattern in CONDITION_PATTERNS:
        if re.search(pattern, q_lower):
            is_condition = True
            sources.add("medlineplus")
            sources.add("europepmc")
            break

    # If research phrasing is detected exclusively
    if "europepmc" in sources and not is_drug and not is_condition and len(sources) == 1:
        return ["europepmc"]

    # Order sources logically
    ordered_sources = []
    for s in ["openfda", "medlineplus", "europepmc"]:
        if s in sources:
            ordered_sources.append(s)

    # Fallback to all three sources if no specific rule matched
    if not ordered_sources:
        return ["medlineplus", "europepmc", "openfda"]

    return ordered_sources
