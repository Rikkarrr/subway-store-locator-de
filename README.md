# Subway Deutschland Scraper

Ein kleines, sauber strukturiertes Python-Projekt zum Erfassen der öffentlich gelisteten Subway-Filialen in Deutschland.

Die Daten werden von der offiziellen Locator-Seite bezogen:

- `https://restaurants.subway.com/germany`
- `https://restaurants.subway.com/sitemap.xml`

Der Scraper extrahiert pro Filiale, soweit verfügbar:

- Name
- Ort
- Filialbezeichnung
- Strasse
- Hausnummer
- PLZ
- Bundesland
- Telefon
- Latitude
- Longitude
- Quelle-URL

## Ansatz

Das Projekt versucht bewusst zuerst die leichtgewichtigen und stabileren Wege:

1. Deutschland-URLs aus der öffentlichen Sitemap laden
2. Falls die Sitemap nicht ausreicht, die Locator-Struktur hierarchisch crawlen
3. Pro Detailseite eingebettete JSON-Daten aus dem HTML lesen
4. Nur wenn nötig, Playwright als Browser-Fallback verwenden
5. Ergebnisse deduplizieren und als CSV und JSON speichern

Das ist absichtlich kein großes Framework, sondern ein übersichtliches Scraper-Projekt mit klar getrennten Verantwortlichkeiten.

## Schnellstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Optional für dynamische Seiten:

```bash
python -m playwright install chromium
```

## Ausgabe

Nach einem Lauf liegen die Dateien in `output/`:

- `subway_deutschland_filialen.csv`
- `subway_deutschland_filialen_raw.json`
- `scraper.log`


## Projektstruktur

```text
subway_scraper/
    main.py
    config.py
    requirements.txt
    README.md
    /scraper
        __init__.py
        fetcher.py
        parser.py
        extractor.py
    /models
        __init__.py
        location.py
    /utils
        __init__.py
        csv_writer.py
        logger.py
        helpers.py
    /output
    /tests
```

## Grenzen

Der Scraper erfasst die Filialen, die im offiziellen öffentlichen Locator von Subway sichtbar sind. Wenn eine Filiale dort noch nicht gelistet ist oder temporär fehlt, kann sie nicht mitgescraped werden.

Mit anderen Worten: Das Ziel ist nicht eine theoretische Vollständigkeit über alle real existierenden Filialen, sondern eine möglichst vollständige Erfassung aller öffentlich veröffentlichten deutschen Standorte.

## Tests

```bash
python -m unittest discover -s tests
```

## Lizenz

MIT
