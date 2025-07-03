# main.py

from fetch_data import fetch_spot_prices, fetch_futures_prices
from fetch_and_compare_prices import calculate_basis
from report_generator import save_report

def main():
    print("📡 Pobieranie danych z Binance API...")

    spot_data = fetch_spot_prices()
    futures_data = fetch_futures_prices()

    print("🔍 Obliczanie różnic (basis) między spot a futures...")
    basis_df = calculate_basis(spot_data, futures_data)

    print("📊 Tworzenie raportu...")
    top_up = basis_df[basis_df["basis"] > 0].nlargest(3, "basis")
    top_down = basis_df[basis_df["basis"] < 0].nsmallest(3, "basis")

    save_report(top_up, top_down)

    print("✅ Proces zakończony pomyślnie!")

if __name__ == "__main__":
    main()
