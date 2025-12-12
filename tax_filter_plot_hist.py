# main.py


import pandas as pd
from util.pyplot_helper import plot_sector_hist


df = pd.read_csv("output.csv")


# Get unique sectors
sectors = sorted(df["Sector"].unique())

# Include "All" at beginning
sectors_to_plot = ["All"] + sectors

for sector in sectors_to_plot:
    filename = f"hist_{sector.replace(' ', '_')}.html"
    plot_sector_hist(df, sector=sector, save_path=filename)

