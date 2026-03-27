import unittest

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


if __name__ == "__main__":
    unittest.main()
