
from pathlib import Path
import pandas as pd

# 1. FILE PATH
folder = Path(
    r"C:\Users\costa\Desktop\Master_TUM\Electricity Market Economics\Essay"
)

file = folder / "GUI_ENERGY_PRICES_202512312300-202612312300.csv"


# 2. LOAD CSV
# Automatically detect separator
df = pd.read_csv(file, sep=None, engine="python", encoding="utf-8-sig")

# 3. BASIC INFORMATION
print("\n========== DATASET INFORMATION ==========")
print("Shape (rows, columns):", df.shape)

print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

print("\n========== FIRST 10 ROWS ==========")
print(df.head(10).to_string(index=False))

print("\n========== LAST 10 ROWS ==========")
print(df.tail(10).to_string(index=False))

# 4. DATA TYPES
print("\n========== DATA TYPES ==========")
print(df.dtypes)

# 5. MISSING VALUES
print("\n========== MISSING VALUES ==========")
print(df.isna().sum())

# 6. STATISTICAL SUMMARY
print("\n========== NUMERICAL STATISTICS ==========")
print(df.describe(include="all").to_string())

# 7. UNIQUE VALUES PER COLUMN
print("\n========== UNIQUE VALUES ==========")
for col in df.columns:
    print(f"{col}: {df[col].nunique()} unique values")

# 8. CHECK POSSIBLE DATE AND PRICE COLUMNS
print("\n========== POSSIBLE DATE/PRICE COLUMNS ==========")
for col in df.columns:
    if any(word in col.lower() for word in
           ["date", "time", "price", "preis", "start", "end"]):
        print(f"\nColumn: {col}")
        print(df[col].head(5).tolist())

# 9. FILE SIZE
print("\n========== FILE SIZE ==========")
print("Size (MB):", round(file.stat().st_size / 1e6, 2))
