from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys
from typing import List, Optional, Tuple

from config import OUTPUT_CSV_PATH, OUTPUT_JSON_PATH
from models.location import Location
from scraper.extractor import SubwayLocationExtractor
from scraper.fetcher import SubwayFetcher
from utils.csv_writer import write_locations_to_csv, write_locations_to_json
from utils.helpers import deduplicate_locations
from utils.logger import setup_logging


def process_detail_page(
    fetcher: SubwayFetcher,
    extractor: SubwayLocationExtractor,
    url: str,
) -> Tuple[str, Optional[Location]]:
    html = fetcher.get_html(url)
    if not html:
        return url, None
    return url, extractor.extract_location(url=url, html=html)


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

        max_workers = fetcher.recommended_worker_count(len(detail_urls))
        logger.info("Verarbeite Detailseiten mit bis zu %s parallelen Workern.", max_workers)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(process_detail_page, fetcher, extractor, url): url for url in detail_urls
            }

            for index, future in enumerate(as_completed(future_to_url), start=1):
                url = future_to_url[future]
                if index <= 10 or index % 25 == 0 or index == len(detail_urls):
                    logger.info("Abgeschlossen %s/%s: %s", index, len(detail_urls), url)

                try:
                    _, location = future.result()
                except Exception:
                    logger.exception("Fehler bei der Verarbeitung von %s", url)
                    continue

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
    finally:
        fetcher.close()


if __name__ == "__main__":
    sys.exit(run())
