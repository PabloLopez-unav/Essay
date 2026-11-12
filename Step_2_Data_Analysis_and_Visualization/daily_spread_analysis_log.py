from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --------------------------------------------------
# 1. FILES
# --------------------------------------------------
folder = Path(r"C:\Users\costa\Desktop\Master_TUM\Electricity Market Economics\Essay\Step_2_Data_Analysis_and_Visualization")
input_file = folder / "combined_BZN_DE_LU_Clean.csv"
output_folder = folder
output_folder.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD AND PREPARE DATA
# --------------------------------------------------
df = pd.read_csv(input_file)
df["Date"] = pd.to_datetime(
    df["MTU (CET/CEST)"].str.split(" - ", n=1).str[0],
    format="%d/%m/%Y %H:%M:%S", errors="coerce"
)
df["Price"] = pd.to_numeric(df["Day-ahead Price (EUR/MWh)"], errors="coerce")

if "Area" in df.columns:
    df = df[df["Area"].isin(["BZN|DE-LU", "BZN|DE-AT-LU"])].copy()

df = df[df["Date"].dt.year.between(2016, 2025)].copy()
df = df.dropna(subset=["Date", "Price"])
if df.empty:
    raise ValueError("No valid price data found for 2016–2025.")

# --------------------------------------------------
# 3. DAILY MINIMUM, MAXIMUM, SPREAD, AND SIGNED LOG
# --------------------------------------------------
daily = (
    df.groupby(df["Date"].dt.normalize())["Price"]
      .agg(Min="min", Max="max", Observations="count")
      .reset_index()
)
daily["Spread"] = daily["Max"] - daily["Min"]

# Signed natural logarithm: works for negative prices and zero.
def signed_log(x):
    return np.sign(x) * np.log1p(np.abs(x))

for col in ["Min", "Max", "Spread"]:
    daily[f"Log {col}"] = signed_log(daily[col])

print("Days per year:")
print(daily.groupby(daily["Date"].dt.year).size())
print("\nPrice observations per day:")
print(daily["Observations"].value_counts().sort_index())

result = pd.DataFrame({
    "Day": daily["Date"].dt.day,
    "Month": daily["Date"].dt.month,
    "Year": daily["Date"].dt.year,
    "Min (EUR/MWh)": daily["Min"],
    "Max (EUR/MWh)": daily["Max"],
    "Spread (EUR/MWh)": daily["Spread"],
    "Log Min": daily["Log Min"],
    "Log Max": daily["Log Max"],
    "Log Spread": daily["Log Spread"],
})
result.to_csv(output_folder / "daily_spreads_2016_2025.csv", index=False)
print("\nFirst rows:")
print(result.head(10).to_string(index=False))

# --------------------------------------------------
# 4. FULL TIME SERIES: ORIGINAL AND LOG
# --------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid")

def full_series_plot(log=False):
    prefix = "Log " if log else ""
    suffix = "_log" if log else ""
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for column, label, width in [
        ("Min", "Daily minimum", 0.7),
        ("Max", "Daily maximum", 0.7),
        ("Spread", "Daily spread", 0.9),
    ]:
        ax.plot(daily["Date"], daily[prefix + column],
                label=label, linewidth=width, alpha=0.85)
    title = "German Day-Ahead Electricity Prices and Daily Spread (2016–2025)"
    if log:
        title += " — Signed Log Transformation"
    ax.set(title=title, xlabel="Year",
           ylabel="Signed log (ln(1 + |x|))" if log else "EUR/MWh")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(ncol=3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(output_folder / f"daily_min_max_spread{suffix}.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close(fig)

full_series_plot(log=False)
full_series_plot(log=True)

# --------------------------------------------------
# 5. YEAR OVERLAY: ORIGINAL AND LOG
# --------------------------------------------------
overlay = daily.loc[~((daily["Date"].dt.month == 2) &
                      (daily["Date"].dt.day == 29))].copy()
overlay["CalendarDay"] = pd.to_datetime(
    "2001-" + overlay["Date"].dt.strftime("%m-%d"),
    format="%Y-%m-%d"
)
overlay["Year"] = overlay["Date"].dt.year

def year_overlay_plot(log=False):
    suffix = "_log" if log else ""
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for year, data in overlay.groupby("Year"):
        ax.plot(data["CalendarDay"], data["Log Spread" if log else "Spread"],
                label=str(year), linewidth=0.9, alpha=0.8)
    title = "Daily Day-Ahead Price Spread by Year (2016–2025)"
    if log:
        title += " — Signed Log Transformation"
    ax.set(title=title, xlabel="Month",
           ylabel="Signed log of daily spread" if log else "Daily spread (EUR/MWh)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_xlim(pd.Timestamp("2001-01-01"), pd.Timestamp("2001-12-31"))
    ax.legend(title="Year", ncol=2, fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(output_folder / f"daily_spread_year_overlay{suffix}.{ext}",
                    dpi=300, bbox_inches="tight")
    plt.close(fig)

year_overlay_plot(log=False)
year_overlay_plot(log=True)

print("\nCSV and 4 figures (PNG + PDF) saved in:", output_folder)
