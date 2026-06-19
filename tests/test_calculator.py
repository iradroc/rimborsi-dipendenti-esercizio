from src import calculator


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


class TestMassimaleTeorico:
    def test_trasferta_italia(self):
        r = richiesta(categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 185.92

    def test_trasferta_estero(self):
        r = richiesta(categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 232.41

    def test_pasto(self):
        r = richiesta(categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 40.0

    def test_chilometrico(self):
        r = richiesta(categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 105.0

    def test_alloggio(self):
        r = richiesta(categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 300.0


class TestCalcola:
    def test_importo_sotto_massimale_tutto_esente(self):
        r = richiesta(categoria="pasto", giorni=5, importo=35.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 35.0
        assert imponibile == 0.0

    def test_importo_sopra_massimale_eccedenza_imponibile(self):
        r = richiesta(categoria="trasferta_italia", giorni=2, importo=120.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 92.96
        assert imponibile == 27.04

    def test_plafond_incapiente_limita_la_quota_esente(self):
        r = richiesta(categoria="alloggio", notti=2, importo=300.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert esente == 100.0
        assert imponibile == 200.0

    def test_plafond_esaurito_tutto_imponibile(self):
        r = richiesta(categoria="pasto", giorni=1, importo=8.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0
        assert imponibile == 8.0

    def test_dettaglio_del_calcolo(self):
        r = richiesta(categoria="trasferta_estero", giorni=2, importo=200.0)
        _, _, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert dettaglio == {
            "massimale_teorico": 154.94,
            "esente_teorica": 154.94,
            "capienza_plafond": 100.0,
        }


class TestMassimaleTeorico2026:
    """Massimali aggiornati dalla Circolare MEF 18/2026 (spese dal 01/01/2026)."""

    def test_trasferta_italia(self):
        r = richiesta(data="2026-02-10", categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 200.0

    def test_trasferta_estero(self):
        r = richiesta(data="2026-02-10", categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 255.0

    def test_pasto(self):
        r = richiesta(data="2026-02-10", categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 50.0

    def test_chilometrico(self):
        r = richiesta(data="2026-02-10", categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 112.5

    def test_alloggio(self):
        r = richiesta(data="2026-02-10", categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 340.0


class TestCalcola2026:
    """Calcolo col plafond mensile aggiornato a 1400,00 € (dal 01/01/2026)."""

    def test_plafond_incapiente_limita_la_quota_esente(self):
        r = richiesta(data="2026-02-10", categoria="alloggio", notti=2, importo=300.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1300.0)
        assert esente == 100.0
        assert imponibile == 200.0

    def test_plafond_esaurito_tutto_imponibile(self):
        r = richiesta(data="2026-02-10", categoria="pasto", giorni=1, importo=10.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1400.0)
        assert esente == 0.0
        assert imponibile == 10.0


class TestDecorrenza:
    """La data della spesa determina i parametri: confine 31/12/2025 → 01/01/2026."""

    def test_ultimo_giorno_2025_usa_massimali_previgenti(self):
        r = richiesta(data="2025-12-31", categoria="trasferta_italia", giorni=1)
        assert calculator.massimale_teorico(r) == 46.48

    def test_primo_giorno_2026_usa_massimali_aggiornati(self):
        r = richiesta(data="2026-01-01", categoria="trasferta_italia", giorni=1)
        assert calculator.massimale_teorico(r) == 50.0


class TestEsteroScaglioni:
    """Trasferte estere a scaglioni dal 2026 (85,00 / 76,50 / 68,00)."""

    def test_entro_cinque_giorni_massimale_pieno(self):
        r = richiesta(data="2026-02-10", categoria="trasferta_estero", giorni=5)
        assert calculator.massimale_teorico(r) == 425.0

    def test_sette_giorni_secondo_scaglione(self):
        r = richiesta(data="2026-02-10", categoria="trasferta_estero", giorni=7)
        # 5×85,00 + 2×76,50
        assert calculator.massimale_teorico(r) == 578.0

    def test_dodici_giorni_tre_scaglioni(self):
        r = richiesta(data="2026-02-10", categoria="trasferta_estero", giorni=12)
        # 5×85,00 + 5×76,50 + 2×68,00
        assert calculator.massimale_teorico(r) == 943.5

    def test_2025_resta_flat_senza_scaglioni(self):
        r = richiesta(data="2025-02-10", categoria="trasferta_estero", giorni=12)
        assert calculator.massimale_teorico(r) == round(77.47 * 12, 2)


class TestLavoroAgile:
    """Indennità lavoro agile: 3,50 €/g entro 12 giornate/mese (dal 2026)."""

    def test_entro_il_limite_tutte_le_giornate(self):
        r = richiesta(data="2026-02-10", categoria="lavoro_agile", giorni=3)
        assert calculator.massimale_teorico(r, giornate_agile_riconosciute=0) == 10.5

    def test_oltre_il_limite_solo_le_giornate_residue(self):
        r = richiesta(data="2026-02-10", categoria="lavoro_agile", giorni=5)
        # Già usate 10/12: ammesse solo 2 giornate → 2×3,50
        assert calculator.massimale_teorico(r, giornate_agile_riconosciute=10) == 7.0

    def test_limite_esaurito_nessuna_giornata_ammessa(self):
        r = richiesta(data="2026-02-10", categoria="lavoro_agile", giorni=2)
        assert calculator.massimale_teorico(r, giornate_agile_riconosciute=12) == 0.0

    def test_calcola_giornate_eccedenti_imponibili(self):
        r = richiesta(data="2026-02-10", categoria="lavoro_agile", giorni=4, importo=14.0)
        # Già usate 10/12 → ammesse 2 → esente teorica 7,00; le altre 2 giornate imponibili
        esente, imponibile, _ = calculator.calcola(
            r, esente_gia_riconosciuta=0.0, giornate_agile_riconosciute=10
        )
        assert esente == 7.0
        assert imponibile == 7.0
