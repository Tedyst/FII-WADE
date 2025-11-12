"""CPE (Common Platform Enumeration) to software class classifier.

Per research.md: Use CPE URI parsing + heuristic classification based on keyword matching.
"""

import logging
import re
from typing import Optional

from lib.config import load_yaml_config

logger = logging.getLogger(__name__)

# Load software class mappings from config
_software_classes: Optional[dict] = None


def get_software_classes() -> dict:
    """Load software class mappings from configuration.

    Returns:
        Dictionary mapping class names to product keywords
    """
    global _software_classes

    if _software_classes is None:
        config = load_yaml_config("config/settings.yaml")
        _software_classes = config.get("software_classes", {})

    return _software_classes


def parse_cpe(cpe_uri: str) -> Optional[dict]:
    """Parse CPE 2.3 URI into components.

    Args:
        cpe_uri: CPE URI string (e.g., cpe:2.3:a:wordpress:wordpress:5.0:*:*:*:*:*:*:*)

    Returns:
        Dictionary with part, vendor, product, version or None if invalid
    """
    # CPE 2.3 format: cpe:2.3:part:vendor:product:version:...
    pattern = r"cpe:2\.3:([ahow]):([^:]+):([^:]+):([^:]+)"
    match = re.match(pattern, cpe_uri)

    if not match:
        return None

    return {
        "part": match.group(1),  # a=application, h=hardware, o=OS, w=web
        "vendor": match.group(2),
        "product": match.group(3),
        "version": match.group(4),
    }


def classify_software(cpe_uri: str) -> Optional[str]:
    """Classify software by CPE URI into categories (CMS, Framework, etc.).

    Args:
        cpe_uri: CPE URI string

    Returns:
        Software class string (cms, framework, shopping_cart, module) or None

    Per research.md: Match product name against keyword list from config/settings.yaml
    """
    cpe = parse_cpe(cpe_uri)
    if not cpe or cpe["part"] != "a":  # Only applications
        return None

    product = cpe["product"].lower()
    classes = get_software_classes()

    for class_name, keywords in classes.items():
        if any(keyword in product for keyword in keywords):
            logger.debug(f"Classified '{product}' as '{class_name}'")
            return class_name

    return None
