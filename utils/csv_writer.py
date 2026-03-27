import csv
import json
from pathlib import Path
from typing import Iterable

from config import CSV_HEADERS
from models.location import Location
from utils.helpers import ensure_directory


def write_locations_to_csv(locations: Iterable[Location], output_path: Path) -> None:
    ensure_directory(output_path.parent)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for location in locations:
            writer.writerow(location.to_dict())


def write_locations_to_json(locations: Iterable[Location], output_path: Path) -> None:
    ensure_directory(output_path.parent)
    payload = [location.to_dict() for location in locations]
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
