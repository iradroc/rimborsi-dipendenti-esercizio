"""Calcolo della quota esente e della quota imponibile di una richiesta."""

from src import rules


def _massimale_estero(parametri, giorni):
    """Massimale per trasferta estera, eventualmente a scaglioni (dal 2026)."""
    base = parametri["massimali_giornalieri"]["trasferta_estero"]
    scaglioni = parametri.get("scaglioni_estero")
    if not scaglioni:
        return round(base * giorni, 2)
    totale = 0.0
    precedente = 0
    for scaglione in scaglioni:
        limite = scaglione["fino_a"] if scaglione["fino_a"] is not None else giorni
        giorni_scaglione = max(0, min(giorni, limite) - precedente)
        totale += giorni_scaglione * base * scaglione["fattore"]
        precedente = limite
        if giorni <= limite:
            break
    return round(totale, 2)


def _massimale_agile(parametri, giorni, giornate_agile_riconosciute):
    """Massimale dell'indennità di lavoro agile, entro il limite mensile di giornate.

    Le giornate oltre il limite mensile non sono coperte dal massimale, quindi la
    loro quota risulta imponibile nel flusso di `calcola`.
    """
    limite = parametri["limite_agile_giornate"]
    ammessi = max(0, min(giorni, limite - giornate_agile_riconosciute))
    return round(parametri["massimale_agile"] * ammessi, 2)


def massimale_teorico(richiesta, giornate_agile_riconosciute=0):
    """Massimale di esenzione applicabile alla richiesta, in base alla categoria.

    `giornate_agile_riconosciute` è il numero di giornate di lavoro agile già
    riconosciute al dipendente nel mese, rilevante solo per la categoria agile.
    """
    parametri = rules.parametri(richiesta["data"])
    categoria = richiesta["categoria"]
    if categoria == "trasferta_estero":
        return _massimale_estero(parametri, richiesta["giorni"])
    if categoria == "lavoro_agile":
        return _massimale_agile(parametri, richiesta["giorni"], giornate_agile_riconosciute)
    if categoria in rules.CATEGORIE_A_GIORNATE:
        return round(parametri["massimali_giornalieri"][categoria] * richiesta["giorni"], 2)
    if categoria == "chilometrico":
        return round(parametri["massimale_km"] * richiesta["km"], 2)
    if categoria == "alloggio":
        return round(parametri["massimale_notte"] * richiesta["notti"], 2)
    raise ValueError(f"categoria non gestita: {categoria}")


def calcola(richiesta, esente_gia_riconosciuta, giornate_agile_riconosciute=0):
    """Restituisce (quota_esente, quota_imponibile, dettaglio).

    `esente_gia_riconosciuta` è la quota esente già riconosciuta al dipendente
    nel mese della richiesta, ai fini del plafond mensile.
    `giornate_agile_riconosciute` è il numero di giornate di lavoro agile già
    riconosciute al dipendente nel mese, ai fini del limite mensile agile.
    """
    parametri = rules.parametri(richiesta["data"])
    importo = richiesta["importo"]
    teorico = massimale_teorico(richiesta, giornate_agile_riconosciute)
    esente_teorica = min(importo, teorico)
    capienza = max(parametri["plafond_mensile"] - esente_gia_riconosciuta, 0.0)
    esente = round(min(esente_teorica, capienza), 2)
    imponibile = round(importo - esente, 2)
    dettaglio = {
        "massimale_teorico": teorico,
        "esente_teorica": round(esente_teorica, 2),
        "capienza_plafond": round(capienza, 2),
    }
    return esente, imponibile, dettaglio
