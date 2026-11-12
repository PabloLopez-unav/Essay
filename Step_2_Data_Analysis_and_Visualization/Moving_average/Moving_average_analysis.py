
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --------------------------------------------------
# 1. FILES AND PARAMETERS
# --------------------------------------------------

folder = Path(
    r"C:\Users\costa\Desktop\Master_TUM\Electricity Market Economics\Essay\Step_2_Data_Analysis_and_Visualization\Moving_average"
)

input_file = folder / "combined_BZN_DE_LU_Clean.csv"
output_folder = folder
output_folder.mkdir(parents=True, exist_ok=True)

WINDOWS = [3, 5, 7]

plt.style.use("seaborn-v0_8-whitegrid")

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

df = pd.read_csv(input_file)

df["Date"] = pd.to_datetime(
    df["MTU (CET/CEST)"].str.split(" - ", n=1).str[0],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)

df["Price"] = pd.to_numeric(
    df["Day-ahead Price (EUR/MWh)"],
    errors="coerce"
)

df = df[
    df["Area"].isin(["BZN|DE-LU", "BZN|DE-AT-LU"])
    & df["Date"].dt.year.between(2016, 2025)
].copy()

if df.empty:
    raise ValueError("No data found for 2016-2025.")

# --------------------------------------------------
# 3. DAILY MINIMUM, MAXIMUM AND SPREAD
# --------------------------------------------------

daily = (
    df.groupby(df["Date"].dt.normalize())["Price"]
    .agg(Min="min", Max="max")
    .sort_index()
)

# Include missing calendar dates explicitly
daily = daily.asfreq("D")

daily["Spread"] = daily["Max"] - daily["Min"]

# Signed logarithmic transformation
def signed_log(x):
    return np.sign(x) * np.log1p(np.abs(x))

# --------------------------------------------------
# 4. CALCULATE MOVING AVERAGES
# --------------------------------------------------

for window in WINDOWS:

    for variable in ["Min", "Max", "Spread"]:

        daily[f"{variable}_MA{window}"] = (
            daily[variable]
            .rolling(
                window=window,
                center=True,
                min_periods=window
            )
            .mean()
        )

        daily[f"Log_{variable}_MA{window}"] = signed_log(
            daily[f"{variable}_MA{window}"]
        )

# --------------------------------------------------
# 5. EXPORT CSV
# --------------------------------------------------

daily["Day"] = daily.index.day
daily["Month"] = daily.index.month
daily["Year"] = daily.index.year

columns = ["Day", "Month", "Year", "Min", "Max", "Spread"]

for window in WINDOWS:
    for variable in ["Min", "Max", "Spread"]:
        columns.append(f"{variable}_MA{window}")
        columns.append(f"Log_{variable}_MA{window}")

daily[columns].to_csv(
    output_folder / "daily_spreads_moving_averages.csv",
    index=False
)

# --------------------------------------------------
# 6. FIGURE 1: HISTORICAL EVOLUTION
# --------------------------------------------------

for window in WINDOWS:

    for logarithmic in [False, True]:

        prefix = "Log_" if logarithmic else ""
        suffix = "_log" if logarithmic else ""

        fig, ax = plt.subplots(figsize=(13, 5.5))

        ax.plot(
            daily.index,
            daily[f"{prefix}Min_MA{window}"],
            label="Daily minimum",
            linewidth=0.8
        )

        ax.plot(
            daily.index,
            daily[f"{prefix}Max_MA{window}"],
            label="Daily maximum",
            linewidth=0.8
        )

        ax.plot(
            daily.index,
            daily[f"{prefix}Spread_MA{window}"],
            label="Daily spread",
            linewidth=1.0
        )

        ax.set(
            title=f"German Day-Ahead Prices - {window}-Day Moving Average",
            xlabel="Year",
            ylabel=(
                "Signed log transformed price"
                if logarithmic else "EUR/MWh"
            )
        )

        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        ax.legend(ncol=3)
        fig.tight_layout()

        filename = f"historical_MA{window}{suffix}"

        fig.savefig(
            output_folder / f"{filename}.png",
            dpi=300,
            bbox_inches="tight"
        )

        fig.savefig(
            output_folder / f"{filename}.pdf",
            bbox_inches="tight"
        )

        plt.close(fig)

# --------------------------------------------------
# 7. FIGURE 2: YEARLY OVERLAY
# --------------------------------------------------

overlay = daily.loc[
    ~((daily.index.month == 2) & (daily.index.day == 29))
].copy()

overlay["CalendarDay"] = pd.to_datetime(
    "2001-" + overlay.index.strftime("%m-%d"),
    format="%Y-%m-%d"
)

overlay["Year"] = overlay.index.year

for window in WINDOWS:

    for logarithmic in [False, True]:

        prefix = "Log_" if logarithmic else ""
        suffix = "_log" if logarithmic else ""

        column = f"{prefix}Spread_MA{window}"

        fig, ax = plt.subplots(figsize=(13, 5.5))

        for year, data in overlay.groupby("Year"):

            ax.plot(
                data["CalendarDay"],
                data[column],
                label=str(year),
                linewidth=1.0,
                alpha=0.8
            )

        ax.set(
            title=f"Daily Price Spread by Year - {window}-Day Moving Average",
            xlabel="Month",
            ylabel=(
                "Signed log transformed spread"
                if logarithmic else "Daily spread (EUR/MWh)"
            )
        )

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

        ax.set_xlim(
            pd.Timestamp("2001-01-01"),
            pd.Timestamp("2001-12-31")
        )

        ax.legend(
            title="Year",
            ncol=2,
            fontsize=9
        )

        fig.tight_layout()

        filename = f"yearly_overlay_MA{window}{suffix}"

        fig.savefig(
            output_folder / f"{filename}.png",
            dpi=300,
            bbox_inches="tight"
        )

        fig.savefig(
            output_folder / f"{filename}.pdf",
            bbox_inches="tight"
        )

        plt.close(fig)

print("Analysis completed.")
print("Files saved in:", output_folder)
