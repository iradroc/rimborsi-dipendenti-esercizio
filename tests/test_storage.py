from src import storage


def _agile(dipendente, data, giorni, stato="valida"):
    return {
        "dipendente": dipendente,
        "data": data,
        "categoria": "lavoro_agile",
        "giorni": giorni,
        "stato": stato,
    }


def test_giornate_agile_somma_solo_valide_del_mese_e_dipendente():
    richieste = [
        _agile("Maria Rossi", "2026-03-04", 3),
        _agile("Maria Rossi", "2026-03-18", 2),
        _agile("Maria Rossi", "2026-03-25", 5, stato="respinta"),  # esclusa
        _agile("Maria Rossi", "2026-04-02", 4),  # altro mese
        _agile("Luca Bianchi", "2026-03-10", 6),  # altro dipendente
        {  # altra categoria, esclusa
            "dipendente": "Maria Rossi",
            "data": "2026-03-08",
            "categoria": "pasto",
            "giorni": 7,
            "stato": "valida",
        },
    ]
    assert (
        storage.giornate_agile_riconosciute_nel_mese(richieste, "Maria Rossi", "2026-03")
        == 5
    )


def test_giornate_agile_zero_se_nessuna_richiesta():
    assert storage.giornate_agile_riconosciute_nel_mese([], "Maria Rossi", "2026-03") == 0
