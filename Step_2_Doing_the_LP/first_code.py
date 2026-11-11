
import pandas as pd
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

# ==========================================
# 1. LOAD DATA
# ==========================================

file = r"Step_2_Doing_the_LP\combined_BZN_DE_LU_Clean.csv"

df = pd.read_csv(file)

# Extract prices directly
prices = df["Day-ahead Price (EUR/MWh)"].to_numpy(dtype=float)
T = len(prices)

print("Number of intervals:", T)
print(df.head())

# ==========================================
# 2. BATTERY PARAMETERS
# ==========================================

P_max = 1.0          # MW
E_max = 2.0          # MWh
eta = np.sqrt(0.90) # Charge/discharge efficiency
dt = 0.25           # 15 minutes

# ==========================================
# 3. OBJECTIVE FUNCTION
# ==========================================

# Variables:
# x = [charge(0:T), discharge(T:2T), energy(2T:3T)]

# scipy minimizes, so we minimize negative profit
c = np.concatenate([
    prices * dt,       # Charging cost
    -prices * dt,      # Discharging revenue
    np.zeros(T)        # Stored energy
])

# ==========================================
# 4. ENERGY BALANCE CONSTRAINTS
# ==========================================

A_eq = lil_matrix((T + 1, 3*T))
b_eq = np.zeros(T + 1)

for t in range(T):

    # E_t - E_(t-1) - eta*charge*dt
    # + discharge*dt/eta = 0

    A_eq[t, 2*T + t] = 1
    A_eq[t, t] = -eta * dt
    A_eq[t, T + t] = dt / eta

    if t > 0:
        A_eq[t, 2*T + t-1] = -1

# Final state of charge = 0
A_eq[T, 3*T-1] = 1

# ==========================================
# 5. VARIABLE BOUNDS
# ==========================================

bounds = (
    [(0, P_max)] * T +  # Charging power
    [(0, P_max)] * T +  # Discharging power
    [(0, E_max)] * T    # Stored energy
)

# ==========================================
# 6. SOLVE LP
# ==========================================

result = linprog(
    c,
    A_eq=A_eq.tocsr(),
    b_eq=b_eq,
    bounds=bounds,
    method="highs"
)

if not result.success:
    raise RuntimeError(result.message)

# ==========================================
# 7. RESULTS
# ==========================================

df["Charge (MW)"] = result.x[:T]
df["Discharge (MW)"] = result.x[T:2*T]
df["Energy (MWh)"] = result.x[2*T:]

df["Profit (EUR)"] = (
    df["Discharge (MW)"] - df["Charge (MW)"]
) * prices * dt

total_profit = df["Profit (EUR)"].sum()

print("\n========== RESULTS ==========")
print(f"Total arbitrage revenue: {total_profit:,.2f} EUR")
print(f"Revenue per kW: {total_profit/1000:.2f} EUR/kW")

# Save results
df.to_csv("battery_results.csv", index=False)

print("\nResults saved to battery_results.csv")
