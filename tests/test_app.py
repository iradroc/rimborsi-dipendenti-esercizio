import pytest

from src import storage
from src.app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "PERCORSO_DATI", tmp_path / "richieste.json")
    app.config["TESTING"] = True
    return app.test_client()


def nuova_richiesta_pasto(client, **campi):
    dati = {
        "dipendente": "Maria Rossi",
        "data": "2025-10-06",
        "categoria": "pasto",
        "importo": "24.00",
        "giorni": "3",
    }
    dati.update(campi)
    return client.post("/nuova", data=dati)


def test_home_reindirizza_a_elenco(client):
    risposta = client.get("/")
    assert risposta.status_code == 302
    assert "/richieste" in risposta.headers["Location"]


def test_pagine_principali_raggiungibili(client):
    for percorso in ("/richieste", "/nuova", "/riepilogo", "/normativa"):
        assert client.get(percorso).status_code == 200


def test_registrazione_richiesta_valida(client):
    risposta = nuova_richiesta_pasto(client)
    assert risposta.status_code == 200
    assert "registrata" in risposta.get_data(as_text=True)

    richieste = storage.carica()
    assert len(richieste) == 1
    assert richieste[0]["stato"] == "valida"
    assert richieste[0]["quota_esente"] == 24.0
    assert richieste[0]["quota_imponibile"] == 0.0


def test_registrazione_richiesta_respinta(client):
    risposta = nuova_richiesta_pasto(client, importo="-10")
    assert "respinta" in risposta.get_data(as_text=True)
    assert "importo non positivo" in risposta.get_data(as_text=True)

    richieste = storage.carica()
    assert richieste[0]["stato"] == "respinta"
    assert richieste[0]["quota_esente"] == 0.0


def test_eccedenza_oltre_massimale_diventa_imponibile(client):
    nuova_richiesta_pasto(client, importo="30.00", giorni="3")
    richieste = storage.carica()
    assert richieste[0]["quota_esente"] == 24.0
    assert richieste[0]["quota_imponibile"] == 6.0


def test_plafond_mensile_condiviso_tra_richieste(client):
    nuova_richiesta_pasto(
        client, categoria="alloggio", notti="8", importo="1150.00", giorni=""
    )
    nuova_richiesta_pasto(client, importo="80.00", giorni="10")
    richieste = storage.carica()
    assert richieste[0]["quota_esente"] == 1150.0
    # Capienza residua: 1200 - 1150 = 50, quindi del pasto sono esenti solo 50.
    assert richieste[1]["quota_esente"] == 50.0
    assert richieste[1]["quota_imponibile"] == 30.0


def test_elenco_filtra_per_dipendente(client):
    nuova_richiesta_pasto(client, dipendente="Maria Rossi")
    nuova_richiesta_pasto(client, dipendente="Luca Bianchi")
    testo = client.get("/richieste?dipendente=Luca+Bianchi").get_data(as_text=True)
    assert "Luca Bianchi" in testo
    assert "Maria Rossi" not in testo.split("</thead>")[1].split("Clicca")[0]


def test_riepilogo_mostra_totali(client):
    nuova_richiesta_pasto(client)
    nuova_richiesta_pasto(client, importo="16.00", giorni="2")
    testo = client.get("/riepilogo").get_data(as_text=True)
    assert "Maria Rossi" in testo
    assert "40.00" in testo


def test_normativa_mostra_massimali_vigenti(client):
    testo = client.get("/normativa").get_data(as_text=True)
    assert "46.48" in testo
    assert "77.47" in testo
    assert "1200.00" in testo


def test_normativa_mostra_anche_massimali_2026(client):
    testo = client.get("/normativa").get_data(as_text=True)
    assert "50.00" in testo
    assert "85.00" in testo
    assert "1400.00" in testo


def test_richiesta_2026_usa_nuovi_massimali(client):
    # Pasto 3 giorni, 30 €: col massimale 2026 (10 €/g → 30 €) è tutto esente.
    nuova_richiesta_pasto(client, data="2026-02-10", importo="30.00", giorni="3")
    richieste = storage.carica()
    assert richieste[0]["quota_esente"] == 30.0
    assert richieste[0]["quota_imponibile"] == 0.0


def test_regime_transitorio_spesa_2025_mantiene_massimali_previgenti(client):
    # Stessa spesa ma datata 2025: massimale 2025 (8 €/g → 24 €), eccedenza imponibile.
    nuova_richiesta_pasto(client, data="2025-12-15", importo="30.00", giorni="3")
    richieste = storage.carica()
    assert richieste[0]["quota_esente"] == 24.0
    assert richieste[0]["quota_imponibile"] == 6.0


def test_trasferta_estero_a_scaglioni(client):
    nuova_richiesta_pasto(
        client, data="2026-04-01", categoria="trasferta_estero", importo="600.00", giorni="7"
    )
    richieste = storage.carica()
    # 5×85,00 + 2×76,50 = 578,00 esente; 600 − 578 = 22 imponibile.
    assert richieste[0]["quota_esente"] == 578.0
    assert richieste[0]["quota_imponibile"] == 22.0


def test_lavoro_agile_limite_mensile_tra_richieste(client):
    # Prime 8 giornate: tutte coperte (3,50 €/g → 28 €).
    nuova_richiesta_pasto(
        client, data="2026-03-05", categoria="lavoro_agile", importo="28.00", giorni="8"
    )
    # Altre 8 giornate nel mese: residue solo 4 (12 − 8) → coperte 14 €, il resto imponibile.
    nuova_richiesta_pasto(
        client, data="2026-03-20", categoria="lavoro_agile", importo="28.00", giorni="8"
    )
    richieste = storage.carica()
    assert richieste[0]["quota_esente"] == 28.0
    assert richieste[1]["quota_esente"] == 14.0
    assert richieste[1]["quota_imponibile"] == 14.0


def test_incompatibilita_agile_trasferta_respinge(client):
    nuova_richiesta_pasto(
        client, data="2026-03-10", categoria="trasferta_italia", importo="80.00", giorni="2"
    )
    risposta = nuova_richiesta_pasto(
        client, data="2026-03-11", categoria="lavoro_agile", importo="3.50", giorni="1"
    )
    assert "respinta" in risposta.get_data(as_text=True)
    richieste = storage.carica()
    assert richieste[1]["stato"] == "respinta"
    assert richieste[1]["motivazione"] == "lavoro agile incompatibile con una trasferta sovrapposta"
