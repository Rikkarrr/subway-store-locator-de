import logging
import re
from typing import Any, Dict, Optional

from models.location import Location
from scraper.parser import SubwayParser
from utils.helpers import (
    clean_text,
    combine_address_lines,
    extract_coordinates,
    map_region_to_bundesland,
    split_street_and_house_number,
)


class SubwayLocationExtractor:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.parser = SubwayParser()

    def extract_location(self, url: str, html: str) -> Optional[Location]:
        entities = self.parser.extract_entity_payloads(html)
        if entities:
            return self._build_location_from_entity(entities[0], url)

        visible_text = self.parser.extract_visible_text(html)
        if "Subway" not in visible_text:
            return None
        if not self._looks_like_detail_page(visible_text):
            return None

        return self._build_location_from_text(url=url, text=visible_text)

    @staticmethod
    def _looks_like_detail_page(visible_text: str) -> bool:
        markers = ("Main Number", "Get Directions", "Contact", "Order Delivery", "Store Hours")
        marker_hits = sum(1 for marker in markers if marker in visible_text)
        return marker_hits >= 2

    def _build_location_from_entity(self, entity: Dict[str, Any], source_url: str) -> Location:
        profile = entity.get("profile", {})
        address = profile.get("address", {}) if isinstance(profile, dict) else {}
        line1 = clean_text(address.get("line1"))
        line2 = clean_text(address.get("line2"))
        full_address = combine_address_lines(line1, line2)
        street, house_number = split_street_and_house_number(full_address)
        latitude, longitude = extract_coordinates(profile)

        city = clean_text(address.get("city"))
        region_code = clean_text(address.get("region")).upper()
        branch_name = clean_text(profile.get("geomodifier")) or street

        return Location(
            name=clean_text(profile.get("name")) or "Subway",
            ort=city,
            filiale=branch_name,
            adresse=street,
            hausnummer=house_number,
            plz=clean_text(address.get("postalCode")),
            bundesland=map_region_to_bundesland(region_code),
            telefon=clean_text((profile.get("mainPhone") or {}).get("display")),
            latitude=latitude,
            longitude=longitude,
            quelle_url=clean_text(profile.get("c_yextPagesURL")) or source_url,
        )

    def _build_location_from_text(self, url: str, text: str) -> Optional[Location]:
        address_match = re.search(
            r"(.+?\d+[A-Za-z]?)\s+(\d{5})\s+(.+?)\s+([A-Z]{2})",
            text,
        )
        phone_match = re.search(r"(\+?\d[\d /()-]{6,})", text)

        if not address_match:
            self.logger.debug("Fallback-Textparser konnte keine Adresse finden: %s", url)
            return None

        full_address = clean_text(address_match.group(1))
        street, house_number = split_street_and_house_number(full_address)
        city = clean_text(address_match.group(3))
        region_code = clean_text(address_match.group(4)).upper()

        return Location(
            name="Subway",
            ort=city,
            filiale=street,
            adresse=street,
            hausnummer=house_number,
            plz=clean_text(address_match.group(2)),
            bundesland=map_region_to_bundesland(region_code),
            telefon=clean_text(phone_match.group(1) if phone_match else ""),
            latitude="",
            longitude="",
            quelle_url=url,
        )
