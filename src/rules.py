"""Parametri normativi per il calcolo dei rimborsi spese.

I parametri dipendono dalla data di sostenimento della spesa:
- fino al 31/12/2025: Circolare MEF n. 41/2024 (disciplina previgente);
- dal 01/01/2026: Circolare MEF n. 18/2026 (massimali e plafond aggiornati).

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
        "riferimento": "Circolare MEF n. 18/2026",
    },
}

CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto")


def parametri(data):
    """Parametri normativi applicabili a una spesa sostenuta in `data`.

    `data` è una stringa ISO (AAAA-MM-GG) o un oggetto `date`.
    """
    giorno = data if isinstance(data, date) else date.fromisoformat(data)
    return PARAMETRI[2026] if giorno >= DECORRENZA_2026 else PARAMETRI[2025]
