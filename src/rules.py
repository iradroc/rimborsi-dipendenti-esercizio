"""Parametri normativi per il calcolo dei rimborsi spese.

I parametri dipendono dalla data di sostenimento della spesa:
- fino al 31/12/2025: Circolare MEF n. 41/2024 (disciplina previgente);
- dal 01/01/2026: Circolare MEF n. 18/2026 (massimali e plafond aggiornati,
  indennità di lavoro agile, trasferte estere a scaglioni).

Le richieste già salvate non si ricalcolano: la data della spesa, non quella di
inserimento, determina i parametri applicabili.
"""

from datetime import date

DECORRENZA_2026 = date(2026, 1, 1)

PARAMETRI = {
    2025: {  # Circolare MEF n. 41/2024 — spese fino al 31/12/2025
        "massimali_giornalieri": {
            "trasferta_italia": 46.48,
            "trasferta_estero": 77.47,
            "pasto": 8.00,
        },
        "massimale_km": 0.42,
        "massimale_notte": 150.00,
        "plafond_mensile": 1200.00,
        "categorie": (
            "trasferta_italia",
            "trasferta_estero",
            "pasto",
            "chilometrico",
            "alloggio",
        ),
        "riferimento": "Circolare MEF n. 41/2024",
    },
    2026: {  # Circolare MEF n. 18/2026 — spese dal 01/01/2026
        "massimali_giornalieri": {
            "trasferta_italia": 50.00,
            "trasferta_estero": 85.00,
            "pasto": 10.00,
        },
        "massimale_km": 0.45,
        "massimale_notte": 170.00,
        "plafond_mensile": 1400.00,
        # Indennità di lavoro agile: 3,50 €/giorno, massimo 12 giornate/mese.
        "massimale_agile": 3.50,
        "limite_agile_giornate": 12,
        # Trasferte estere a scaglioni: fattore sul massimale estero (85,00 €).
        "scaglioni_estero": (
            {"fino_a": 5, "fattore": 1.00},
            {"fino_a": 10, "fattore": 0.90},
            {"fino_a": None, "fattore": 0.80},
        ),
        "categorie": (
            "trasferta_italia",
            "trasferta_estero",
            "pasto",
            "chilometrico",
            "alloggio",
            "lavoro_agile",
        ),
        "riferimento": "Circolare MEF n. 18/2026",
    },
}

CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
    "lavoro_agile": "Indennità lavoro agile",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto")

# Categorie le cui richieste sono espresse in giornate (richiedono `giorni`).
CATEGORIE_A_GIORNATE_ESTESE = CATEGORIE_A_GIORNATE + ("lavoro_agile",)

# Categorie considerate "trasferta" ai fini dell'incompatibilità con il lavoro agile.
CATEGORIE_TRASFERTA = ("trasferta_italia", "trasferta_estero")


def parametri(data):
    """Parametri normativi applicabili a una spesa sostenuta in `data`.

    `data` è una stringa ISO (AAAA-MM-GG) o un oggetto `date`.
    """
    giorno = data if isinstance(data, date) else date.fromisoformat(data)
    return PARAMETRI[2026] if giorno >= DECORRENZA_2026 else PARAMETRI[2025]


def categorie_ammesse(data):
    """Codici delle categorie disponibili per una spesa sostenuta in `data`."""
    return parametri(data)["categorie"]
