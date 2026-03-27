import logging
import time
import xml.etree.ElementTree as ET
from collections import deque
from typing import Iterable, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    BASE_URL,
    COUNTRY_PATH,
    COUNTRY_URL,
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    SITEMAP_INDEX_URL,
    USER_AGENT,
)

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - Umgebung abhaengig
    PlaywrightTimeoutError = Exception
    sync_playwright = None


class SubwayFetcher:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            read=MAX_RETRIES,
            connect=MAX_RETRIES,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
            }
        )
        return session

    def discover_germany_urls(self) -> List[str]:
        urls = self.fetch_germany_urls_from_sitemap()
        if urls:
            return urls

        self.logger.warning(
            "Sitemap lieferte keine Deutschland-URLs. Wechsle auf Hierarchie-Crawl."
        )
        return self.crawl_germany_hierarchy()

    def fetch_germany_urls_from_sitemap(self) -> List[str]:
        try:
            xml_text = self.fetch_text(SITEMAP_INDEX_URL)
            if not xml_text:
                return []

            root = ET.fromstring(xml_text)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_urls = [node.text for node in root.findall(".//sm:loc", ns) if node.text]

            germany_urls: Set[str] = set()
            for sitemap_url in sitemap_urls:
                chunk_xml = self.fetch_text(sitemap_url)
                if not chunk_xml:
                    continue

                chunk_root = ET.fromstring(chunk_xml)
                locs = [
                    node.text
                    for node in chunk_root.findall(".//sm:loc", ns)
                    if node.text and f"{BASE_URL}{COUNTRY_PATH}" in node.text
                ]
                germany_urls.update(locs)

            return sorted(germany_urls)
        except Exception:
            self.logger.exception("Fehler beim Lesen der Sitemap.")
            return []

    def crawl_germany_hierarchy(self) -> List[str]:
        visited: Set[str] = set()
        discovered: Set[str] = set()
        queue = deque([COUNTRY_URL])

        while queue:
            url = queue.popleft()
            if url in visited:
                continue

            visited.add(url)
            html = self.get_html(url)
            if not html:
                continue

            discovered.add(url)
            for link in self.extract_germany_links(html=html, source_url=url):
                if link not in visited:
                    queue.append(link)

        return sorted(discovered)

    def filter_detail_urls(self, urls: Iterable[str]) -> List[str]:
        detail_urls: List[str] = []
        for url in sorted(set(urls)):
            path = urlparse(url).path.rstrip("/")
            if not path.startswith(COUNTRY_PATH):
                continue

            segment_count = len([part for part in path.split("/") if part])
            if segment_count >= 4:
                detail_urls.append(url)

        return detail_urls

    def get_html(self, url: str) -> Optional[str]:
        html = self.fetch_text(url)
        if not html:
            return self.fetch_with_playwright(url)

        if self._contains_embedded_data(html):
            return html

        self.logger.info("Keine eingebetteten Daten erkannt, versuche Browser-Fallback: %s", url)
        return self.fetch_with_playwright(url) or html

    def fetch_text(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY_SECONDS)
            return response.text
        except requests.RequestException:
            self.logger.exception("HTTP-Fehler bei %s", url)
            return None

    def fetch_with_playwright(self, url: str) -> Optional[str]:
        if sync_playwright is None:
            self.logger.warning(
                "Playwright ist nicht installiert. Browser-Fallback wird fuer %s uebersprungen.",
                url,
            )
            return None

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=45000)
                content = page.content()
                browser.close()
                return content
        except PlaywrightTimeoutError:
            self.logger.exception("Playwright-Timeout bei %s", url)
        except Exception:
            self.logger.exception("Playwright-Fehler bei %s", url)
        return None

    def extract_germany_links(self, html: str, source_url: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: Set[str] = set()

        for anchor in soup.select("a[href]"):
            href = (anchor.get("href") or "").strip()
            if not href:
                continue

            absolute_url = urljoin(source_url, href)
            parsed = urlparse(absolute_url)
            if parsed.netloc != urlparse(BASE_URL).netloc:
                continue
            if not parsed.path.startswith(COUNTRY_PATH):
                continue
            if "/index.html" in parsed.path:
                continue

            cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
            links.add(cleaned)

        return sorted(links)

    @staticmethod
    def _contains_embedded_data(html: str) -> bool:
        return '"entities": [' in html or '"profile": {' in html
