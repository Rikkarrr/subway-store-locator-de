import unittest

from scraper.fetcher import SubwayFetcher
from models.location import Location
from utils.helpers import deduplicate_locations, map_region_to_bundesland, split_street_and_house_number


class HelperTests(unittest.TestCase):
    def test_split_street_and_house_number(self) -> None:
        street, number = split_street_and_house_number("Ruettenscheider Strasse 143")
        self.assertEqual(street, "Ruettenscheider Strasse")
        self.assertEqual(number, "143")

    def test_map_region_to_bundesland(self) -> None:
        self.assertEqual(map_region_to_bundesland("NW"), "Nordrhein-Westfalen")
        self.assertEqual(map_region_to_bundesland("XX"), "XX")

    def test_deduplicate_locations(self) -> None:
        first = Location(name="Subway", ort="Essen", adresse="Gladbecker Strasse", hausnummer="18", plz="45141")
        second = Location(name="Subway", ort="Essen", adresse="Gladbecker Strasse", hausnummer="18", plz="45141")
        unique = deduplicate_locations([first, second])
        self.assertEqual(len(unique), 1)

    def test_filter_detail_urls_keeps_only_leaf_pages(self) -> None:
        fetcher = SubwayFetcher()
        urls = [
            "https://restaurants.subway.com/germany/st/halle/saale",
            "https://restaurants.subway.com/germany/st/halle/saale/hans-dietrich-genscher-platz-1",
            "https://restaurants.subway.com/germany/st/halle/saale/neustadter-passage-17d",
            "https://restaurants.subway.com/germany/nw/aachen/krefelder-str-216",
        ]

        detail_urls = fetcher.filter_detail_urls(urls)

        self.assertEqual(
            detail_urls,
            [
                "https://restaurants.subway.com/germany/nw/aachen/krefelder-str-216",
                "https://restaurants.subway.com/germany/st/halle/saale/hans-dietrich-genscher-platz-1",
                "https://restaurants.subway.com/germany/st/halle/saale/neustadter-passage-17d",
            ],
        )


if __name__ == "__main__":
    unittest.main()
