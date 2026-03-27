import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from config import REGION_MAP
from models.location import Location


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def combine_address_lines(*parts: str) -> str:
    cleaned = [clean_text(part) for part in parts if clean_text(part)]
    return ", ".join(cleaned)


def split_street_and_house_number(address: str) -> Tuple[str, str]:
    address = clean_text(address)
    if not address:
        return "", ""

    match = re.match(r"^(.*?)(\d+[A-Za-z]?(?:[-/]\d+[A-Za-z]?)?)$", address)
    if not match:
        return address, ""

    street = clean_text(match.group(1).rstrip(","))
    house_number = clean_text(match.group(2))
    return street, house_number


def map_region_to_bundesland(region_code: str) -> str:
    code = clean_text(region_code).upper()
    return REGION_MAP.get(code, code)


def extract_coordinates(profile: Dict[str, object]) -> Tuple[str, str]:
    coordinate_candidates = [
        profile.get("yextRoutableCoordinate"),
        profile.get("yextDisplayCoordinate"),
        profile.get("geocodedCoordinate"),
        profile.get("cityCoordinate"),
    ]

    for coords in coordinate_candidates:
        if not isinstance(coords, dict):
            continue
        lat = coords.get("lat")
        lon = coords.get("long")
        if lat is None or lon is None:
            continue
        return str(lat), str(lon)

    return "", ""


def build_deduplication_key(location: Location) -> str:
    parts = [
        location.name.lower(),
        location.ort.lower(),
        location.adresse.lower(),
        location.hausnummer.lower(),
        location.plz.lower(),
        location.latitude.lower(),
        location.longitude.lower(),
    ]
    return "|".join(clean_text(part) for part in parts)


def deduplicate_locations(locations: Iterable[Location]) -> List[Location]:
    unique: Dict[str, Location] = {}

    for location in locations:
        key = build_deduplication_key(location)
        if key and key not in unique:
            unique[key] = location

    return sorted(unique.values(), key=lambda item: (item.bundesland, item.ort, item.adresse, item.hausnummer))
