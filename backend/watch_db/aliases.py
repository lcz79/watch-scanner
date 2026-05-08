"""
Alias map: reference canonica → lista di nomi colloquiali / varianti
con cui un orologio compare negli annunci reali.

Usato da resolver.py per mappare query non strutturate alla referenza canonica.
"""

# Format: "REFERENCE_NORM": ["alias1", "alias2", ...]
# REFERENCE_NORM = reference.upper().replace(" ", "").replace("/", "").replace("-", "")

ALIAS_MAP: dict[str, list[str]] = {

    # ── ROLEX SUBMARINER ──────────────────────────────────────────────────────
    "116610LN": [
        "submariner", "sub date", "sub 116610", "116610", "submariner date",
        "sub nero", "sub black", "submariner black", "sub acciaio",
    ],
    "116610LV": [
        "hulk", "sub verde", "sub green", "submariner green", "hulk rolex",
        "116610lv", "submariner hulk", "green sub",
    ],
    "126610LN": [
        "submariner 41", "sub 41", "126610", "nuova sub", "new sub",
        "submariner 2020", "sub date 41",
    ],
    "126610LV": [
        "starbucks", "kermit 41", "submariner verde 41", "126610lv",
    ],
    "14060M": [
        "sub no date", "submariner no date", "sub senza data", "14060",
        "nodate sub", "submariner nd",
    ],
    "124060": [
        "sub no date 41", "124060", "submariner nd 41",
    ],
    "16610": [
        "sub vintage", "old sub", "16610", "submariner 16610",
    ],
    "16610LV": [
        "kermit", "kermit rolex", "sub verde vintage", "16610lv",
    ],

    # ── ROLEX GMT-MASTER II ──────────────────────────────────────────────────
    "116710LN": [
        "gmt black", "gmt batman", "batman", "116710", "gmt master black",
        "gmt acciaio nero", "batman rolex",
    ],
    "116710BLNR": [
        "batman", "gmt batman", "116710blnr", "gmt blue black",
        "batman gmt", "rolex batman",
    ],
    "126710BLNR": [
        "batman 40", "nuovo batman", "126710blnr", "gmt 2020 batman",
    ],
    "126711CHNR": [
        "sprite", "gmt sprite", "rolex sprite", "126711", "gmt verde rosso",
    ],
    "126720VTNR": [
        "sprite left hand", "destrosso", "gmt left hand crown",
    ],
    "116719BLRO": [
        "pepsi gold", "gmt oro pepsi", "116719", "gmt white gold pepsi",
    ],
    "126710BLRO": [
        "pepsi", "gmt pepsi", "rolex pepsi", "126710blro", "pepsi acciaio",
        "blu rosso gmt", "pepsi steel",
    ],
    "116700LN": [
        "gmt coke", "coke gmt", "116700", "gmt nero rosso",
    ],

    # ── ROLEX DAYTONA ────────────────────────────────────────────────────────
    "116500LN": [
        "daytona", "daytona bianco", "daytona black", "116500",
        "cosmograph daytona", "daytona ceramica", "daytona acciaio",
        "daytona steel", "daytona ceramic",
    ],
    "116520": [
        "daytona old", "daytona vintage", "116520", "daytona pre ceramic",
        "daytona 2000", "daytona acciaio vecchia",
    ],
    "116523": [
        "daytona bicolore", "daytona rolesor", "116523", "daytona gold steel",
    ],
    "116503": [
        "daytona rolesor nuovo", "116503",
    ],
    "116508": [
        "daytona oro giallo", "daytona yellow gold", "116508",
    ],
    "126500LN": [
        "nuova daytona", "daytona 2023", "126500", "daytona new",
    ],

    # ── ROLEX DATEJUST ───────────────────────────────────────────────────────
    "126334": [
        "datejust 41", "dj41", "datejust acciaio oro", "126334",
    ],
    "126300": [
        "datejust 41 acciaio", "dj 41 steel", "126300",
    ],
    "126231": [
        "datejust 36 bicolore", "126231",
    ],
    "126200": [
        "datejust 36 acciaio", "dj36", "126200",
    ],

    # ── ROLEX DAY-DATE ───────────────────────────────────────────────────────
    "228235": [
        "day date 40", "president oro rosa", "228235", "day date rosa",
    ],
    "228238": [
        "day date 40 oro giallo", "president oro", "228238",
    ],
    "118238": [
        "day date 36 oro", "president", "118238",
    ],

    # ── ROLEX EXPLORER / MILGAUSS ────────────────────────────────────────────
    "214270": [
        "explorer 39", "214270", "explorer ii", "explorer acciaio",
    ],
    "224270": [
        "explorer 36 nuovo", "explorer 2021", "224270",
    ],
    "116400GV": [
        "milgauss", "milgauss verde", "milgauss green glass", "116400",
    ],

    # ── ROLEX SEA-DWELLER ────────────────────────────────────────────────────
    "126600": [
        "sea dweller", "sd 43", "126600", "sea-dweller rosso",
        "red sea dweller", "sea dweller red writing",
    ],
    "126660": [
        "deepsea", "deep sea", "126660", "sea dweller deep",
        "deepsea black", "deepsea james cameron",
    ],

    # ── ROLEX YACHT-MASTER ───────────────────────────────────────────────────
    "126622": [
        "yacht master 40", "ym40", "126622", "yacht master acciaio",
    ],
    "116655": [
        "yacht master oysterflex", "ym rubber", "116655",
    ],

    # ── PATEK PHILIPPE NAUTILUS ──────────────────────────────────────────────
    "57111A": [
        "nautilus", "patek nautilus", "5711", "57111a", "nautilus acciaio",
        "nautilus steel", "5711a", "nautilus blu", "nautilus blue",
        "nautilus 40", "pp nautilus",
    ],
    "57261A": [
        "nautilus moonphase", "5726", "57261a", "nautilus fase di luna",
    ],
    "57191A": [
        "nautilus chrono", "5719", "57191a", "nautilus cronografo",
    ],
    "57111G": [
        "nautilus oro bianco", "57111g", "nautilus white gold",
    ],
    "57111R": [
        "nautilus oro rosa", "57111r", "nautilus rose gold",
    ],
    "57261R": [
        "nautilus moonphase rosa", "57261r",
    ],

    # ── PATEK PHILIPPE AQUANAUT ──────────────────────────────────────────────
    "52671A": [
        "aquanaut", "patek aquanaut", "5267", "52671a", "aquanaut acciaio",
        "aquanaut brown", "aquanaut marrone",
    ],
    "52681A": [
        "aquanaut chrono", "52681a", "aquanaut cronografo",
    ],

    # ── PATEK PHILIPPE CALATRAVA / COMPLICATIONS ─────────────────────────────
    "57271G": [
        "patek perpetual", "5727", "57271g", "annual calendar",
    ],
    "51461G": [
        "patek tourbillon", "5146", "tourbillon patek",
    ],

    # ── AUDEMARS PIGUET ROYAL OAK ────────────────────────────────────────────
    "150500ST": [
        "royal oak", "ap royal oak", "royal oak 41", "150500st",
        "15050", "royal oak acciaio", "royal oak steel",
        "royal oak blue", "royal oak blu", "royal oak azzurro",
    ],
    "150510ST": [
        "royal oak 36", "150510st", "royal oak piccolo",
    ],
    "150520ST": [
        "royal oak 37", "150520st",
    ],
    "260410OR": [
        "royal oak chrono", "26041", "royal oak cronografo",
        "260410or", "royal oak chrono oro",
    ],
    "263200ST": [
        "royal oak offshore", "offshore", "ap offshore", "26320",
        "royal oak offshore steel",
    ],
    "263000ST": [
        "offshore diver", "26300", "ap offshore diver",
    ],

    # ── OMEGA SPEEDMASTER ────────────────────────────────────────────────────
    "31030425001001": [
        "speedmaster moonwatch", "speedy", "speedmaster", "moonwatch",
        "omega moonwatch", "speedmaster professional", "speedy pro",
        "speedmaster moonphase", "speedy acciaio", "speedy professional",
        "311.30.42.30.01.005", "31130423001005",
    ],
    "31130423001005": [
        "speedmaster reduced", "speedy reduced", "speedmaster automatic",
    ],

    # ── OMEGA SEAMASTER ──────────────────────────────────────────────────────
    "21030422003001": [
        "seamaster 300m", "seamaster diver", "omega seamaster",
        "seamaster james bond", "seamaster 300", "seamaster blue",
        "seamaster acciaio", "seamaster blu",
    ],
    "23330422101001": [
        "seamaster planet ocean", "planet ocean", "po 600m",
        "seamaster po",
    ],

    # ── IWC ──────────────────────────────────────────────────────────────────
    "IW327001": [
        "pilot mark", "iwc pilot", "mark xviii", "iw327001",
        "iwc mark 18", "pilots watch mark",
    ],
    "IW500401": [
        "portugieser", "iwc portugieser", "iw500401", "portugese",
        "iwc porto", "portuguese chronograph",
    ],
    "IW371438": [
        "ingenieur", "iwc ingenieur", "iw371438",
    ],

    # ── TUDOR ────────────────────────────────────────────────────────────────
    "79230N": [
        "tudor black bay", "bb58", "black bay 58", "tudor bb",
        "tudor submariner", "black bay steel", "79230",
        "black bay nero", "tudor bb58",
    ],
    "79090": [
        "tudor pelagos", "pelagos", "tudor diver pro",
    ],
    "M79360N": [
        "tudor chrono", "tudor black bay chrono", "bb chrono", "m79360",
    ],

    # ── PANERAI ──────────────────────────────────────────────────────────────
    "PAM00111": [
        "panerai 111", "pam111", "luminor marina", "panerai luminor",
        "pam 111",
    ],
    "PAM00372": [
        "panerai luminor 1950", "pam372", "luminor 1950 3 days",
    ],
    "PAM00688": [
        "panerai submersible", "pam688", "submersible",
    ],

    # ── CARTIER ──────────────────────────────────────────────────────────────
    "WSBB0026": [
        "santos", "cartier santos", "santos acciaio", "santos medium",
    ],
    "W6920042": [
        "tank", "cartier tank", "tank solo", "tank francaise",
    ],
    "W7100014": [
        "ballon bleu", "cartier ballon", "bb cartier",
    ],
}
