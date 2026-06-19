from datetime import date

from src import rules


def test_spesa_2025_usa_parametri_previgenti():
    p = rules.parametri("2025-12-31")
    assert p["plafond_mensile"] == 1200.0
    assert p["massimali_giornalieri"]["trasferta_italia"] == 46.48
    assert p["riferimento"] == "Circolare MEF n. 41/2024"


def test_spesa_2026_usa_parametri_aggiornati():
    p = rules.parametri("2026-01-01")
    assert p["plafond_mensile"] == 1400.0
    assert p["massimali_giornalieri"]["trasferta_italia"] == 50.0
    assert p["riferimento"] == "Circolare MEF n. 18/2026"


def test_accetta_anche_oggetto_date():
    assert rules.parametri(date(2026, 6, 19))["plafond_mensile"] == 1400.0
    assert rules.parametri(date(2025, 6, 19))["plafond_mensile"] == 1200.0
