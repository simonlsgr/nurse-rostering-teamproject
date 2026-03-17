import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("./output/gap_instance_13_20260317_200324.csv")

# Convert columns to numeric, handling missing values
df["time"] = pd.to_numeric(df["time"], errors="coerce")
df["objective"] = pd.to_numeric(df["objective"], errors="coerce")
df["bound"] = pd.to_numeric(df["bound"], errors="coerce")

# Plot
plt.figure(figsize=(12, 6))

# Assign one color per solver
colors = plt.cm.tab10.colors  # 10 distinct colors
solvers = df["solver"].unique()

for i, solver in enumerate(solvers):
    solver_df = df[df["solver"] == solver]
    color = colors[i % len(colors)]
    
    # Objective as solid line
    plt.plot(solver_df["time"], solver_df["objective"], label=f"{solver} obj", color=color, linestyle="-")
    
    # Bound as dashed line with same color
    plt.plot(solver_df["time"], solver_df["bound"], label=f"{solver} bound", color=color, linestyle="--")

plt.xlabel("Time (s)")
plt.ylabel("Value")
plt.title("Solver Objective and Bound over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()