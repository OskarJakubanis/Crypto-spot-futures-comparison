# basis_analysis.py

import pandas as pd

def calculate_basis(futures_df, spot_df):
    """
    Oblicz odchylenie między ceną futures a spot.
    Zwraca dataframe z kolumną 'basis' jako różnicą procentową.
    """
    merged = pd.merge(futures_df, spot_df, on="symbol", suffixes=("_futures", "_spot"))
    merged["basis"] = ((merged["price_futures"] - merged["price_spot"]) / merged["price_spot"]) * 100
    return merged.sort_values("basis", ascending=False)

def get_top_movers(basis_df, top_n=3):
    """
    Zwraca top N dodatnich i ujemnych odchyleń (w procentach).
    """
    top_positive = basis_df.head(top_n)
    top_negative = basis_df.tail(top_n).sort_values("basis")
    return top_positive, top_negative

if __name__ == "__main__":
    # Przykład lokalny (do testów)
    futures_data = pd.read_csv("data/futures_prices.csv")
    spot_data = pd.read_csv("data/spot_prices.csv")

    basis_df = calculate_basis(futures_data, spot_data)
    top_up, top_down = get_top_movers(basis_df)

    print("\nTop 3 dodatnie odchylenia:")
    print(top_up[["symbol", "basis"]])

    print("\nTop 3 ujemne odchylenia:")
    print(top_down[["symbol", "basis"]])
