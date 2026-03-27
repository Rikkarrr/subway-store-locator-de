import json
import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup


class SubwayParser:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def extract_entity_payloads(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        payloads: List[Dict[str, Any]] = []

        for script in soup.find_all("script", type="text/data"):
            raw_text = script.get_text(strip=True)
            if not raw_text or '"entities"' not in raw_text:
                continue

            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                self.logger.debug("Ungueltiges JSON in text/data Script gefunden.")
                continue

            entities = data.get("entities")
            if isinstance(entities, list) and entities:
                payloads.extend(entity for entity in entities if isinstance(entity, dict))

        return payloads

    def extract_visible_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)
