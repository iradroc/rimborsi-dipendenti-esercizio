"""Regole di validazione delle richieste di rimborso."""

from datetime import date, timedelta

from src import rules


def _intervallo(richiesta):
    """Intervallo di giorni [inizio, fine] coperto dalla richiesta."""
    inizio = date.fromisoformat(richiesta["data"])
    giorni = richiesta.get("giorni") or 1
    return inizio, inizio + timedelta(days=giorni - 1)


def _si_sovrappongono(richiesta_a, richiesta_b):
    a_inizio, a_fine = _intervallo(richiesta_a)
    b_inizio, b_fine = _intervallo(richiesta_b)
    return a_inizio <= b_fine and b_inizio <= a_fine


def _conflitto_agile_trasferta(richiesta, richieste_esistenti):
    """Cerca una richiesta valida incompatibile (lavoro agile ⇄ trasferta) sovrapposta.

    Vale solo dal 01/01/2026. Restituisce la motivazione di respingimento o "".
    """
    if date.fromisoformat(richiesta["data"]) < rules.DECORRENZA_2026:
        return ""
    categoria = richiesta["categoria"]
    if categoria == "lavoro_agile":
        opposte, motivazione = rules.CATEGORIE_TRASFERTA, "lavoro agile incompatibile con una trasferta sovrapposta"
    elif categoria in rules.CATEGORIE_TRASFERTA:
        opposte, motivazione = ("lavoro_agile",), "trasferta incompatibile con il lavoro agile sovrapposto"
    else:
        return ""
    for esistente in richieste_esistenti:
        if (
            esistente.get("stato") == "valida"
            and esistente.get("dipendente") == richiesta["dipendente"]
            and esistente.get("categoria") in opposte
            and _si_sovrappongono(richiesta, esistente)
        ):
            return motivazione
    return ""


def valida(richiesta, richieste_esistenti=()):
    """Restituisce (True, "") se la richiesta è valida, altrimenti (False, motivazione).

    `richieste_esistenti` è lo storico (richieste già registrate), usato per la
    verifica di incompatibilità lavoro agile / trasferta (dal 01/01/2026).
    """
    if not richiesta.get("dipendente"):
        return False, "dipendente mancante"

    categoria = richiesta.get("categoria")
    if categoria not in rules.CATEGORIE:
        return False, "categoria non riconosciuta"

    importo = richiesta.get("importo")
    if importo is None or importo <= 0:
        return False, "importo non positivo"

    try:
        date.fromisoformat(richiesta.get("data") or "")
    except ValueError:
        return False, "data mancante o non valida"

    if categoria not in rules.categorie_ammesse(richiesta["data"]):
        return False, "categoria non disponibile per la data della spesa"

    if categoria in rules.CATEGORIE_A_GIORNATE_ESTESE:
        giorni = richiesta.get("giorni")
        if not giorni or giorni <= 0:
            return False, "numero di giornate non valido"

    if categoria == "chilometrico":
        km = richiesta.get("km")
        if not km or km <= 0:
            return False, "numero di chilometri non valido"

    if categoria == "alloggio":
        notti = richiesta.get("notti")
        if not notti or notti <= 0:
            return False, "numero di notti non valido"

    conflitto = _conflitto_agile_trasferta(richiesta, richieste_esistenti)
    if conflitto:
        return False, conflitto

    return True, ""
