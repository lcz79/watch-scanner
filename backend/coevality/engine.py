"""Motore di coevità: stima l'anno dal seriale e filtra i componenti coevi."""
from urllib.parse import quote_plus

from .data import SERIAL_YEAR, SERIAL_NEVER_USED, REFERENCES, SOURCES
from .models import (
    Source, ComponentVariant, ComponentResult, SerialEstimate, CoevalityResult,
)

_DISCLAIMER = (
    "Stima indicativa basata sul consenso dei collezionisti: il numero di serie "
    "fornisce un anno con tolleranza di ±1-2 anni (i componenti potevano essere "
    "a magazzino). Non sostituisce l'esame di un esperto. La coevità si applica "
    "ai Rolex con seriale sequenziale (fino a ~2010); i seriali moderni casuali "
    "non sono databili."
)


def estimate_year(serial: str) -> SerialEstimate:
    s = (serial or "").strip().upper()
    letter = next((c for c in s if c.isalpha()), None)
    if not letter:
        return SerialEstimate(
            serial=s, sequential=False,
            note="Nessun prefisso-lettera riconosciuto. I Rolex moderni (post ~2010) "
                 "hanno seriali casuali e non databili dal numero.",
        )
    if letter in SERIAL_NEVER_USED:
        return SerialEstimate(
            serial=s, letter=letter, sequential=False,
            note=f"La lettera '{letter}' non è usata da Rolex per i seriali: verificare il numero.",
        )
    rng = SERIAL_YEAR.get(letter)
    if not rng:
        return SerialEstimate(
            serial=s, letter=letter, sequential=False,
            note=f"Prefisso '{letter}' fuori dal periodo coperto (1987-2001) o seriale casuale: anno non stimabile.",
        )
    span = f"{rng[0]}" if rng[0] == rng[1] else f"{rng[0]}-{rng[1]}"
    return SerialEstimate(
        serial=s, letter=letter, year_from=rng[0], year_to=rng[1], sequential=True,
        note=f"Prefisso '{letter}' → circa {span} (consenso collezionisti, ±1-2 anni).",
    )


def _overlaps(v: dict, yf: int, yt: int) -> bool:
    return v["year_from"] <= yt and v["year_to"] >= yf


def _sources(keys: list[str]) -> list[Source]:
    return [Source(**SOURCES[k]) for k in keys if k in SOURCES]


_COMPONENT_EN = {
    "Quadrante": "dial",
    "Ghiera (scala tachimetrica)": "bezel",
    "Bracciale": "bracelet",
    "Terminali (end links)": "end links",
    "Materiale luminescente": "lume",
    "Calibro": "movement caliber",
    "Fondello (marcatura interna)": "caseback",
    "Garanzia / Documenti": "guarantee papers",
    "Scatola e controscatola": "box set",
}


def _mk_variant(v: dict, reference: str, component: str) -> ComponentVariant:
    """Costruisce la variante e genera il link a esempi reali (Google Immagini).
    Query in inglese per risultati più rilevanti tra i collezionisti."""
    label = v["label"].split("—")[-1].strip() if "—" in v["label"] else v["label"]
    en = _COMPONENT_EN.get(component, "")
    q = f"Rolex {reference} {label} {en}".replace("(", " ").replace(")", " ")
    q = " ".join(q.split())
    image_search = "https://www.google.com/search?tbm=isch&q=" + quote_plus(q)
    return ComponentVariant(
        label=v["label"], description=v["description"],
        year_from=v["year_from"], year_to=v["year_to"], confidence=v["confidence"],
        image_url=v.get("image_url"), image_search=image_search,
    )


def check_coevality(serial: str, reference: str) -> CoevalityResult | None:
    ref = (reference or "").strip().upper().replace(" ", "")
    data = REFERENCES.get(ref)
    if not data:
        return None

    est = estimate_year(serial)
    components: list[ComponentResult] = []
    for c in data["components"]:
        variants = c["variants"]
        if est.year_from is not None and est.year_to is not None:
            coeval = [v for v in variants if _overlaps(v, est.year_from, est.year_to)]
            others = [v for v in variants if not _overlaps(v, est.year_from, est.year_to)]
        else:
            coeval, others = [], variants
        components.append(ComponentResult(
            component=c["component"],
            icon=c["icon"],
            coeval=[_mk_variant(v, ref, c["component"]) for v in coeval],
            other_variants=[_mk_variant(v, ref, c["component"]) for v in others],
            note=c.get("note"),
            sources=_sources(c.get("sources", [])),
        ))

    return CoevalityResult(
        reference=ref,
        model=data["model"],
        production_from=data["production_from"],
        production_to=data["production_to"],
        serial_estimate=est,
        components=components,
        disclaimer=_DISCLAIMER,
    )


def list_references() -> list[dict]:
    return [
        {
            "reference": k,
            "model": v["model"],
            "production_from": v["production_from"],
            "production_to": v["production_to"],
        }
        for k, v in REFERENCES.items()
    ]
