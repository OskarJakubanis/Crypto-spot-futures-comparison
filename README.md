# crypto-futures-basis-analysis

Projekt łączy Apache Airflow, Azure Data Factory i GitHub Actions w celu automatycznej analizy różnic pomiędzy cenami Spot a Futures kryptowalut. Celem jest identyfikacja potencjalnych baniek i sygnałów short squeeze poprzez śledzenie top 3 największych dodatnich i ujemnych różnic (tzw. basis).

## 🔍 Cel analizy

Na rynku krypto różnica pomiędzy ceną spot a futures może sugerować:
- Spekulację (bańka) — futures > spot
- Panikę / short squeeze — futures < spot

Codziennie analizujemy:
- Top 3 największe dodatnie różnice (potencjalne bańki)
- Top 3 największe ujemne różnice (potencjalne short squeeze)

## ⚙️ Stack technologiczny

- **Apache Airflow** — harmonogram pobierania danych i orkiestracja zadań
- **Azure Data Factory** — alternatywny potok chmurowy ETL
- **GitHub Actions** — CI/CD (testy, update danych, push do repo)
- **Python** — pobieranie i czyszczenie danych z CoinGecko
- **Jupyter Notebook** — analiza i wykresy
- **CSV / JSON** — przechowywanie danych

## 📦 Jak to działa?

1. GitHub Action uruchamia workflow codziennie o 7:00
2. Airflow DAG pobiera dane z CoinGecko API (spot + futures)
3. Porównuje ceny i tworzy ranking odchyleń
4. Zapisuje wyniki do pliku CSV
5. Azure Data Factory może alternatywnie pobierać dane i zapisywać do blob storage
6. Jupyter Notebook prezentuje analizę z plików CSV

## 📈 Przykładowy wynik

| Token | Spot Price | Futures Price | Difference (%) |
|-------|------------|---------------|----------------|
| BTC   | 31,000     | 32,200        | +3.87%         |
| ETH   | 2,100      | 1,980         | -5.71%         |

## 📁 Foldery

- `dags/` — skrypty Airflow
- `data/` — automatycznie aktualizowane pliki .csv
- `notebooks/` — analiza danych
- `reports/` — końcowe wyniki
- `.github/workflows/` — CI/CD z GitHub Actions

## ✅ Status

🟢 Wersja MVP ukończona. Codzienne pobieranie i analiza działają automatycznie.

## 📌 Do zrobienia

- Integracja z Azure Blob Storage (opcjonalnie)
- Automatyczne generowanie wykresów
- Dashboard w Power BI lub Streamlit
