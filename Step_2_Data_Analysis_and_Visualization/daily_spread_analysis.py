from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --------------------------------------------------
# 1. FILES
# --------------------------------------------------
folder = Path(r"C:\Users\costa\Desktop\Master_TUM\Electricity Market Economics\Essay\Step_2_Data_Analysis_and_Visualization")
input_file = folder / "combined_BZN_DE_LU_Clean.csv"  # Change to your actual CSV filename
output_folder = folder
output_folder.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD AND PREPARE DATA
# --------------------------------------------------
df = pd.read_csv(input_file)

# The first timestamp is the beginning of each ENTSO-E interval.
start = df["MTU (CET/CEST)"].str.split(" - ", n=1).str[0]
df["Date"] = pd.to_datetime(df["MTU (CET/CEST)"].str.split(" - ").str[0], format="%d/%m/%Y %H:%M:%S", errors="coerce")
df["Price"] = pd.to_numeric(df["Day-ahead Price (EUR/MWh)"], errors="coerce")

# If there are multiple areas in the input, keep the German one only.
if "Area" in df.columns:
    df = df[df["Area"].isin(["BZN|DE-LU", "BZN|DE-AT-LU"])].copy()

# Retain the research period only.
df = df[df["Date"].dt.year.between(2016, 2025)].copy()
if df.empty:
    raise ValueError("No price data found for 2016–2025. Check the input file and dates.")

# --------------------------------------------------
# 3. DAILY MINIMUM, MAXIMUM AND SPREAD
# --------------------------------------------------
daily = (
    df.groupby(df["Date"].dt.normalize())["Price"]
      .agg(Min="min", Max="max", Observations="count")
      .reset_index()
)
daily = daily.rename(columns={"Date": "Date"})
daily["Spread"] = daily["Max"] - daily["Min"]

# Check for partial days / missing data (92 or 100 quarter-hours are
# normal at daylight-saving transitions; 24/23/25 rows if hourly).
print("Days per year:")
print(daily.groupby(daily["Date"].dt.year).size())
print("\nNumber of price observations per day:")
print(daily["Observations"].value_counts().sort_index())

result = pd.DataFrame({
    "Day": daily["Date"].dt.day,
    "Month": daily["Date"].dt.month,
    "Year": daily["Date"].dt.year,
    "Min (EUR/MWh)": daily["Min"],
    "Max (EUR/MWh)": daily["Max"],
    "Spread (EUR/MWh)": daily["Spread"],
})

result.to_csv(output_folder / "daily_spreads_2016_2025.csv", index=False)
print("\nFirst rows:")
print(result.head(10).to_string(index=False))

# --------------------------------------------------
# 4. FIGURE 1: FULL DAILY TIME SERIES
# --------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(13, 5.5))
ax.plot(daily["Date"], daily["Min"], label="Daily minimum", linewidth=0.7, alpha=0.8)
ax.plot(daily["Date"], daily["Max"], label="Daily maximum", linewidth=0.7, alpha=0.8)
ax.plot(daily["Date"], daily["Spread"], label="Daily spread", linewidth=0.9, alpha=0.9)
ax.set(title="German Day-Ahead Electricity Prices and Daily Spread (2016–2025)",
       xlabel="Year", ylabel="EUR/MWh")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(ncol=3)
fig.tight_layout()
fig.savefig(output_folder / "daily_min_max_spread.png", dpi=300, bbox_inches="tight")
fig.savefig(output_folder / "daily_min_max_spread.pdf", bbox_inches="tight")
plt.close(fig)

# --------------------------------------------------
# 5. FIGURE 2: OVERLAY YEARS ON ONE CALENDAR
# --------------------------------------------------
overlay = daily.loc[~((daily["Date"].dt.month == 2) &
                      (daily["Date"].dt.day == 29))].copy()
# Map month/day to a common non-leap reference year for perfect alignment.
overlay["CalendarDay"] = pd.to_datetime(
    "2001-" + overlay["Date"].dt.strftime("%m-%d"),
    format="%Y-%m-%d"
)
overlay["Year"] = overlay["Date"].dt.year

fig, ax = plt.subplots(figsize=(13, 5.5))
for year, data in overlay.groupby("Year"):
    ax.plot(data["CalendarDay"], data["Spread"],
            label=str(year), linewidth=0.9, alpha=0.8)

ax.set(title="Daily Day-Ahead Price Spread by Year (2016–2025)",
       xlabel="Month", ylabel="Daily spread (EUR/MWh)")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.set_xlim(pd.Timestamp("2001-01-01"), pd.Timestamp("2001-12-31"))
ax.legend(title="Year", ncol=2, fontsize=9)
fig.tight_layout()
fig.savefig(output_folder / "daily_spread_year_overlay.png", dpi=300, bbox_inches="tight")
fig.savefig(output_folder / "daily_spread_year_overlay.pdf", bbox_inches="tight")
plt.close(fig)

print("\nFiles saved in:", output_folder)
