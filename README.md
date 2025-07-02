# crypto-futures-basis-analysis

## Opis projektu

Projekt ma na celu analizę różnic (basis) między cenami spot a futures wybranych kryptowalut na giełdzie Binance. Celem jest identyfikacja top 3 największych dodatnich i ujemnych odchyleń, co pozwala na ocenę rynkowych anomalii i potencjalnych strategii tradingowych.

Projekt łączy w sobie narzędzia i praktyki DataOps oraz DevOps:

- **Apache Airflow** do orkiestracji zadań i automatyzacji pipeline’u danych,
- **Azure Data Factory** jako alternatywna platforma orkiestracji chmurowej,
- **GitHub Actions** do CI/CD i automatyzacji procesu wdrażania,
- Pobieranie danych z Binance Futures API oraz Binance Spot API,
- Przetwarzanie i analiza danych w Pythonie,
- Raportowanie wyników i wizualizacja trendów.

## Cel biznesowy

- Monitorowanie i szybka identyfikacja anomalii cenowych na rynku kryptowalut,
- Dostarczenie narzędzia do oceny odchyleń między rynkiem spot i futures,
- Automatyzacja procesu analizy z zapewnieniem ciągłej aktualizacji danych.

## Główne komponenty

1. **Pobieranie danych** – automatyczne pobieranie aktualnych cen spot i futures z Binance API,
2. **Przetwarzanie danych** – czyszczenie, łączenie i obliczanie basis (różnicy procentowej między futures a spot),
3. **Analiza** – wyliczenie top 3 pozycji z największymi dodatnimi i ujemnymi odchyleniami,
4. **Orkiestracja** – zarządzanie pipeline’em za pomocą Airflow oraz Azure Data Factory,
5. **CI/CD** – automatyczne testy, walidacje i wdrażanie pipeline’u przy pomocy GitHub Actions,
6. **Raportowanie** – generowanie raportów oraz dashboardów do monitoringu trendów.

## Wymagania

- Python 3.8+
- Apache Airflow
- Azure Data Factory (konto i konfiguracja)
- GitHub Actions (repozytorium GitHub)
- Dostęp do Binance API (klucz API dla futures i spot)
- Biblioteki Python: `requests`, `pandas`, `apache-airflow`, `azure-identity`, `pyyaml` itp.

## Instrukcja uruchomienia

1. Skonfiguruj połączenie z Binance API i ustaw odpowiednie zmienne środowiskowe z kluczami API,
2. Skonfiguruj Apache Airflow oraz Azure Data Factory z podanymi DAG-ami i pipeline’ami,
3. Skonfiguruj GitHub Actions w repozytorium, aby automatyzować wdrożenia,
4. Uruchom pipeline w Airflow lub Azure Data Factory,
5. Monitoruj wyniki i raporty w przygotowanym dashboardzie.

## Struktura projektu
