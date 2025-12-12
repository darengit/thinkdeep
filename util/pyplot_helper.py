import numpy as np
import matplotlib.pyplot as plt

def plot_sector_hist(df, sector="All", save_path=None):
    """
    Plot a histogram of Pct Change for a given sector
    and optionally save to an HTML file.
    """

    # --- Filter ---
    if sector != "All":
        df_filtered = df[df["Sector"] == sector]
    else:
        df_filtered = df

    if df_filtered.empty:
        print(f"No stocks found for sector: {sector}")
        return

    pct_values = df_filtered["Pct Change"] * 100

    # --- Create 5% bins ---
    min_val = np.floor(pct_values.min() / 5) * 5
    max_val = np.ceil(pct_values.max() / 5) * 5
    bins = np.arange(min_val, max_val + 5, 5)

    plt.figure(figsize=(10, 6))
    plt.hist(pct_values, bins=bins, edgecolor="black")

    plt.title(f"Histogram of Pct Change ({sector})")
    plt.xlabel("Pct Change (%)")
    plt.ylabel("Number of Stocks")
    plt.grid(axis="y", alpha=0.3)

    # --- Save to HTML if requested ---
    if save_path is not None:
        # Save image first
        png_path = save_path.replace(".html", ".png")
        plt.savefig(png_path, format="png", bbox_inches="tight")

        # Write simple HTML wrapper
        with open(save_path, "w") as f:
            f.write(f"""
            <html>
            <head><title>{sector} Histogram</title></head>
            <body>
                <h2>Histogram for Sector: {sector}</h2>
                <img src="{png_path}" style="max-width:100%;">
            </body>
            </html>
            """.strip())

        print(f"Saved {save_path}")

    plt.close()

