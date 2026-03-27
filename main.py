import logging
import sys
from typing import List

from config import OUTPUT_CSV_PATH, OUTPUT_JSON_PATH
from models.location import Location
from scraper.extractor import SubwayLocationExtractor
from scraper.fetcher import SubwayFetcher
from utils.csv_writer import write_locations_to_csv, write_locations_to_json
from utils.helpers import deduplicate_locations
from utils.logger import setup_logging


def run() -> int:
    setup_logging()
    logger = logging.getLogger(__name__)

    fetcher = SubwayFetcher()
    extractor = SubwayLocationExtractor()
    raw_locations: List[Location] = []

    try:
        urls = fetcher.discover_germany_urls()
        logger.info("Es wurden %s Deutschland-URLs gefunden.", len(urls))

        detail_urls = fetcher.filter_detail_urls(urls)
        logger.info("Es wurden %s Detailseiten erkannt.", len(detail_urls))

        for index, url in enumerate(detail_urls, start=1):
            logger.info("Verarbeite %s/%s: %s", index, len(detail_urls), url)
            html = fetcher.get_html(url)
            if not html:
                logger.warning("Leere Antwort fuer %s", url)
                continue

            location = extractor.extract_location(url=url, html=html)
            if location is None:
                logger.warning("Keine Filialdaten extrahiert: %s", url)
                continue

            raw_locations.append(location)

        unique_locations = deduplicate_locations(raw_locations)
        logger.info(
            "Extraktion abgeschlossen: %s Rohdaten, %s eindeutige Filialen.",
            len(raw_locations),
            len(unique_locations),
        )

        write_locations_to_csv(unique_locations, OUTPUT_CSV_PATH)
        write_locations_to_json(unique_locations, OUTPUT_JSON_PATH)

        logger.info("CSV geschrieben nach %s", OUTPUT_CSV_PATH)
        logger.info("JSON geschrieben nach %s", OUTPUT_JSON_PATH)
        return 0
    except KeyboardInterrupt:
        logger.warning("Abbruch durch Benutzer.")
        return 130
    except Exception:
        logger.exception("Unbehandelter Fehler beim Scraper-Lauf.")
        return 1


if __name__ == "__main__":
    sys.exit(run())
