import unittest

from scraper.extractor import SubwayLocationExtractor


HTML_SAMPLE = """
<html>
  <body>
    <script type="text/data">
      {
        "config": {"mapId": "dir-map"},
        "entities": [
          {
            "profile": {
              "name": "Subway",
              "geomodifier": "Gladbecker Str. 18",
              "address": {
                "line1": "Gladbecker Strasse 18",
                "postalCode": "45141",
                "city": "Essen",
                "region": "NW"
              },
              "mainPhone": {
                "display": "0201 94671414"
              },
              "yextDisplayCoordinate": {
                "lat": 51.4649602,
                "long": 7.0097264
              },
              "c_yextPagesURL": "https://restaurants.subway.com/germany/nw/essen/gladbecker-strasse-18"
            }
          }
        ]
      }
    </script>
  </body>
</html>
"""


class ExtractorTests(unittest.TestCase):
    def test_extract_location_from_embedded_json(self) -> None:
        extractor = SubwayLocationExtractor()
        location = extractor.extract_location(
            url="https://restaurants.subway.com/germany/nw/essen/gladbecker-strasse-18",
            html=HTML_SAMPLE,
        )

        self.assertIsNotNone(location)
        assert location is not None
        self.assertEqual(location.name, "Subway")
        self.assertEqual(location.ort, "Essen")
        self.assertEqual(location.adresse, "Gladbecker Strasse")
        self.assertEqual(location.hausnummer, "18")
        self.assertEqual(location.plz, "45141")
        self.assertEqual(location.bundesland, "Nordrhein-Westfalen")
        self.assertEqual(location.telefon, "0201 94671414")
        self.assertEqual(location.latitude, "51.4649602")
        self.assertEqual(location.longitude, "7.0097264")


if __name__ == "__main__":
    unittest.main()
