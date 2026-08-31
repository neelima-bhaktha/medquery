import logging
from typing import Dict
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger(__name__)

# Trusted medical domains list
TRUSTED_DOMAINS = {
    "medlineplus.gov",
    "fda.gov",
    "labels.fda.gov",
    "api.fda.gov",
    "ncbi.nlm.nih.gov",
    "europepmc.org",
    "ebi.ac.uk",
    "cdc.gov",
    "who.int",
    "mayoclinic.org",
    "nih.gov",
}

# Cache of RobotFileParser instances per scheme+domain
_ROBOTS_CACHE: Dict[str, RobotFileParser] = {}


def get_domain(url: str) -> str:
    """
    Extract netloc domain from a URL.
    """
    parsed = urlparse(url)
    return parsed.netloc.lower()


def is_trusted_domain(url: str) -> bool:
    """
    Check if URL domain is in the trusted medical domains whitelist.
    """
    domain = get_domain(url)
    return any(domain == trusted or domain.endswith("." + trusted) for trusted in TRUSTED_DOMAINS)


def can_fetch(url: str, user_agent: str = "MedQueryMedicalCrew/1.0", enforce_trusted: bool = False) -> bool:
    """
    Check if robots.txt allows crawling the given URL for user_agent.
    Optionally enforces that domain is in trusted domains list.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False

    if enforce_trusted and not is_trusted_domain(url):
        logger.info(f"URL domain '{parsed.netloc}' is not in trusted whitelist.")
        return False

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    if base_url not in _ROBOTS_CACHE:
        parser = RobotFileParser()
        robots_url = f"{base_url}/robots.txt"
        parser.set_url(robots_url)
        try:
            parser.read()
        except Exception as e:
            logger.debug(f"Failed to read robots.txt from '{robots_url}': {e}")
        _ROBOTS_CACHE[base_url] = parser

    rfp = _ROBOTS_CACHE[base_url]
    allowed = rfp.can_fetch(user_agent, url)
    return allowed if allowed is not None else True
