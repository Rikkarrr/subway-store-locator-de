from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
TESTS_DIR = PROJECT_ROOT / "tests"

BASE_URL = "https://restaurants.subway.com"
COUNTRY_PATH = "/germany"
COUNTRY_URL = f"{BASE_URL}{COUNTRY_PATH}"
SITEMAP_INDEX_URL = f"{BASE_URL}/sitemap.xml"

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
REQUEST_DELAY_SECONDS = 0.2
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/134.0.0.0 Safari/537.36"
)

OUTPUT_CSV_PATH = OUTPUT_DIR / "subway_deutschland_filialen.csv"
OUTPUT_JSON_PATH = OUTPUT_DIR / "subway_deutschland_filialen_raw.json"
LOG_FILE_PATH = OUTPUT_DIR / "scraper.log"

CSV_HEADERS = [
    "name",
    "ort",
    "filiale",
    "adresse",
    "hausnummer",
    "plz",
    "bundesland",
    "telefon",
    "latitude",
    "longitude",
    "quelle_url",
]

REGION_MAP = {
    "BB": "Brandenburg",
    "BE": "Berlin",
    "BW": "Baden-W\u00fcrttemberg",
    "BY": "Bayern",
    "HB": "Bremen",
    "HE": "Hessen",
    "HH": "Hamburg",
    "MV": "Mecklenburg-Vorpommern",
    "NI": "Niedersachsen",
    "NW": "Nordrhein-Westfalen",
    "RP": "Rheinland-Pfalz",
    "SH": "Schleswig-Holstein",
    "SL": "Saarland",
    "SN": "Sachsen",
    "ST": "Sachsen-Anhalt",
    "TH": "Th\u00fcringen",
}
