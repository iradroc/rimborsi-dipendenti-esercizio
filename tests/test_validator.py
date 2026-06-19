from src import validator


def richiesta(**campi):
    base = {
        "dipendente": "Maria Rossi",
        "data": "2025-10-06",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


def test_richiesta_valida():
    assert validator.valida(richiesta()) == (True, "")


def test_dipendente_mancante():
    ok, motivazione = validator.valida(richiesta(dipendente=""))
    assert not ok
    assert motivazione == "dipendente mancante"


def test_categoria_non_riconosciuta():
    ok, motivazione = validator.valida(richiesta(categoria="parcheggio"))
    assert not ok
    assert motivazione == "categoria non riconosciuta"


def test_importo_zero():
    ok, motivazione = validator.valida(richiesta(importo=0))
    assert not ok
    assert motivazione == "importo non positivo"


def test_importo_negativo():
    ok, motivazione = validator.valida(richiesta(importo=-5.0))
    assert not ok
    assert motivazione == "importo non positivo"


def test_importo_mancante():
    ok, motivazione = validator.valida(richiesta(importo=None))
    assert not ok
    assert motivazione == "importo non positivo"


def test_data_mancante():
    ok, motivazione = validator.valida(richiesta(data=""))
    assert not ok
    assert motivazione == "data mancante o non valida"


def test_data_non_valida():
    ok, motivazione = validator.valida(richiesta(data="06/10/2025"))
    assert not ok
    assert motivazione == "data mancante o non valida"


def test_giornate_mancanti_per_trasferta():
    ok, motivazione = validator.valida(
        richiesta(categoria="trasferta_italia", giorni=None)
    )
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_giornate_zero_per_pasto():
    ok, motivazione = validator.valida(richiesta(categoria="pasto", giorni=0))
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_chilometri_non_validi():
    ok, motivazione = validator.valida(
        richiesta(categoria="chilometrico", km=0)
    )
    assert not ok
    assert motivazione == "numero di chilometri non valido"


def test_notti_non_valide():
    ok, motivazione = validator.valida(
        richiesta(categoria="alloggio", notti=None)
    )
    assert not ok
    assert motivazione == "numero di notti non valido"


def test_chilometrico_valido():
    assert validator.valida(
        richiesta(categoria="chilometrico", km=120, giorni=None)
    ) == (True, "")


def test_alloggio_valido():
    assert validator.valida(
        richiesta(categoria="alloggio", notti=3, giorni=None)
    ) == (True, "")


def test_lavoro_agile_non_disponibile_nel_2025():
    ok, motivazione = validator.valida(
        richiesta(data="2025-12-31", categoria="lavoro_agile", giorni=2)
    )
    assert not ok
    assert motivazione == "categoria non disponibile per la data della spesa"


def test_lavoro_agile_valido_dal_2026():
    assert validator.valida(
        richiesta(data="2026-01-02", categoria="lavoro_agile", giorni=2)
    ) == (True, "")


def test_lavoro_agile_richiede_giornate():
    ok, motivazione = validator.valida(
        richiesta(data="2026-01-02", categoria="lavoro_agile", giorni=None)
    )
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_agile_incompatibile_con_trasferta_sovrapposta():
    esistenti = [
        richiesta(
            data="2026-03-11",
            categoria="trasferta_italia",
            giorni=1,
            stato="valida",
        )
    ]
    nuova = richiesta(data="2026-03-10", categoria="lavoro_agile", giorni=3)
    ok, motivazione = validator.valida(nuova, esistenti)
    assert not ok
    assert motivazione == "lavoro agile incompatibile con una trasferta sovrapposta"


def test_trasferta_incompatibile_con_agile_sovrapposto():
    esistenti = [
        richiesta(
            data="2026-03-10", categoria="lavoro_agile", giorni=3, stato="valida"
        )
    ]
    nuova = richiesta(data="2026-03-12", categoria="trasferta_estero", giorni=2)
    ok, motivazione = validator.valida(nuova, esistenti)
    assert not ok
    assert motivazione == "trasferta incompatibile con il lavoro agile sovrapposto"


def test_nessun_conflitto_se_giorni_non_si_sovrappongono():
    esistenti = [
        richiesta(
            data="2026-03-01", categoria="trasferta_italia", giorni=2, stato="valida"
        )
    ]
    nuova = richiesta(data="2026-03-10", categoria="lavoro_agile", giorni=3)
    assert validator.valida(nuova, esistenti) == (True, "")
