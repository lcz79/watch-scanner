from pydantic import BaseModel


class Source(BaseModel):
    name: str
    url: str


class ComponentVariant(BaseModel):
    label: str                    # es. "Mark 1 — Floating"
    description: str
    year_from: int
    year_to: int
    confidence: str               # "alta" | "media" | "bassa"
    image_url: str | None = None  # immagine incorporata (di proprietà), se disponibile
    image_search: str = ""        # link a esempi reali (Google Immagini), sempre valido


class ComponentResult(BaseModel):
    component: str                # es. "Quadrante"
    icon: str                     # material symbol per il frontend
    coeval: list[ComponentVariant]      # varianti coeve con l'anno stimato
    other_variants: list[ComponentVariant]  # le altre (contesto)
    note: str | None = None
    sources: list[Source] = []


class SerialEstimate(BaseModel):
    serial: str
    letter: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    sequential: bool = True
    note: str


class CoevalityResult(BaseModel):
    reference: str
    model: str
    production_from: int
    production_to: int
    serial_estimate: SerialEstimate
    components: list[ComponentResult]
    disclaimer: str
