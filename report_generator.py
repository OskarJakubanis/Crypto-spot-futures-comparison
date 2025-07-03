# report_generator.py

import pandas as pd
import matplotlib.pyplot as plt

def save_report(top_up, top_down, output_path="basis_report.csv", chart_path="basis_chart.png"):
    """
    Zapisuje top 3 dodatnie i ujemne basis do CSV oraz generuje wykres.
    """
    report_df = pd.concat([top_up.assign(type="positive"), top_down.assign(type="negative")])
    report_df.to_csv(output_path, index=False)

    # Wykres
    plt.figure(figsize=(10, 6))
    colors = ['green' if x >= 0 else 'red' for x in report_df["basis"]]
    plt.bar(report_df["symbol"], report_df["basis"], color=colors)
    plt.title("Top 3 dodatnie i ujemne odchylenia (basis) %")
    plt.xlabel("Symbol")
    plt.ylabel("Basis (%)")
    plt.grid(True)
    plt.savefig(chart_path)
    plt.close()

    print(f"✅ Zapisano raport: {output_path}")
    print(f"✅ Wygenerowano wykres: {chart_path}")

if __name__ == "__main__":
    # Przykład testowy — zakłada, że plik basis.csv już istnieje
    df = pd.read_csv("basis.csv")
    top_up = df[df["basis"] > 0].nlargest(3, "basis")
    top_down = df[df["basis"] < 0].nsmallest(3, "basis")
    save_report(top_up, top_down)
