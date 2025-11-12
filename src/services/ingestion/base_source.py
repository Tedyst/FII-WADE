"""Base interface for vulnerability data sources.

All data sources (NVD, EUVD, future sources) implement this interface
for extensibility per constitution's modular design principle.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from models.vulnerability import Vulnerability


class BaseSource(ABC):
    """Abstract base class for vulnerability data sources.

    Per research.md: Define BaseSource abstract class with methods for
    fetch_vulnerabilities, parse_record, get_software_class.
    """

    @abstractmethod
    async def fetch_vulnerabilities(
        self,
        limit: Optional[int] = None,
        modified_since: Optional[str] = None,
    ) -> AsyncIterator[dict]:
        """Fetch raw vulnerability records from the data source.

        Args:
            limit: Maximum number of records to fetch
            modified_since: ISO date string to fetch only recent updates

        Yields:
            Raw vulnerability records as dictionaries
        """
        pass

    @abstractmethod
    def parse_record(self, raw: dict) -> Vulnerability:
        """Parse a raw record into a Vulnerability model.

        Args:
            raw: Raw vulnerability record from the data source

        Returns:
            Parsed Vulnerability instance
        """
        pass

    @abstractmethod
    def get_software_class(self, vulnerability: Vulnerability) -> Optional[str]:
        """Determine software class (CMS, Framework, etc.) from vulnerability.

        Args:
            vulnerability: Vulnerability instance

        Returns:
            Software class string or None if undetermined

        Per research.md: Use CPE URI parsing + heuristic classification
        """
        pass
