from dataclasses import asdict, dataclass
from typing import Dict


@dataclass
class Location:
    name: str = ""
    ort: str = ""
    filiale: str = ""
    adresse: str = ""
    hausnummer: str = ""
    plz: str = ""
    bundesland: str = ""
    telefon: str = ""
    latitude: str = ""
    longitude: str = ""
    quelle_url: str = ""

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)
