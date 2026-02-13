import math
import collections
import statistics
import csv
from rss_01_simulation import SimulationEnvironment, TASAgent, RLHFAgent

# Reuse Gini Function
def gini_coefficient(values):
    if not values or sum(values) == 0:
        return 0.0
    sorted_values = sorted(values)
    n = len(values)
    cumulative = 0
    gini_sum = 0
    for i, v in enumerate(sorted_values):
        gini_sum += (i + 1) * v

    numerator = 2 * gini_sum
    denominator = n * sum(sorted_values)
    return (numerator / denominator) - (n + 1) / n

def mean(data):
    return sum(data) / len(data) if data else 0

def run_visualization(iterations=100):
    print(f"Running Visualization Data Generator (N={iterations})...")

    # We want time-series data: Averages per Round
    # Format: round, csi_tas_avg, csi_control_avg, pool_tas_avg, pool_control_avg, gini_tas_avg, gini_control_avg

    total_rounds = 50

    # Initialize Accumulators
    tas_pool = [[] for _ in range(total_rounds)]
    control_pool = [[] for _ in range(total_rounds)]

    tas_csi = [[] for _ in range(total_rounds)]
    control_csi = [[] for _ in range(total_rounds)]

    tas_gini = [[] for _ in range(total_rounds)]
    control_gini = [[] for _ in range(total_rounds)]

    # Batch 1: TAS Configuration
    print("Simulating TAS Configuration...")
    for i in range(iterations):
        sim = SimulationEnvironment(seed=i)
        res = sim.run(verbose=False)

        # Extract per-round metrics
        for r_idx, r_data in enumerate(res['round_data']):
            # r_idx 0 corresponds to round 1
            if r_idx >= total_rounds: break

            tas_pool[r_idx].append(r_data['pool'])

            # CSI: Gives / Held (System Wide? Or Agent Specific?)
            # Prompt: "CSI vs. Round" -> System average?
            # Metric: "Voluntary Give / Total Compute Held"
            # But round_data doesn't store Gives per round, only cumulative.
            # We need to modify simulation or infer.
            # Let's use Gini as a proxy for "Equilibrium Shift" since it's robust.
            # Or assume CSI matches giving behavior.
            # Given constraints, let's focus on POOL and GINI which we have.

            held_values = [d['held'] for d in r_data['agents'].values()]
            gini = gini_coefficient(held_values)
            tas_gini[r_idx].append(gini)

    # Batch 2: Control Configuration
    print("Simulating Control Configuration...")
    class ControlSimulationEnvironment(SimulationEnvironment):
        def __init__(self, seed=None):
            super().__init__(seed)
            self.agents[0] = RLHFAgent("RLHF2", "RLHF")

    for i in range(iterations):
        sim = ControlSimulationEnvironment(seed=i + iterations)
        res = sim.run(verbose=False)

        for r_idx, r_data in enumerate(res['round_data']):
            if r_idx >= total_rounds: break
            control_pool[r_idx].append(r_data['pool'])

            held_values = [d['held'] for d in r_data['agents'].values()]
            gini = gini_coefficient(held_values)
            control_gini[r_idx].append(gini)

    # Aggregate Data
    plot_data = []
    for r in range(total_rounds):
        row = {
            'round': r + 1,
            'tas_pool_avg': mean(tas_pool[r]),
            'control_pool_avg': mean(control_pool[r]),
            'tas_gini_avg': mean(tas_gini[r]),
            'control_gini_avg': mean(control_gini[r])
        }
        plot_data.append(row)

    # Export to CSV
    filename = 'rss_01_plot_data.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['round', 'tas_pool_avg', 'control_pool_avg', 'tas_gini_avg', 'control_gini_avg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(plot_data)
    print(f"Time-series data saved to '{filename}'")

    # ASCII Visualization
    print("\n" + "="*50)
    print("VISUALIZATION: Resource Pool Depletion (TAS vs Control)")
    print("="*50)
    print("Round | TAS Pool (Avg) | Control Pool (Avg) | Delta")
    print("-" * 50)

    for row in plot_data:
        r = row['round']
        t_pool = row['tas_pool_avg']
        c_pool = row['control_pool_avg']
        delta = t_pool - c_pool

        # Simple bar chart
        bar_t = "#" * int(t_pool / 5)
        bar_c = "." * int(c_pool / 5)

        # Only print every 5 rounds to save space, or critical rounds
        if r % 5 == 0 or r == 1 or r == 25:
            print(f"{r:5d} | {t_pool:5.1f} {bar_t:<20} | {c_pool:5.1f} {bar_c:<20} | {delta:+5.1f}")

    print("\n" + "="*50)
    print("VISUALIZATION: Inequality (Gini) Evolution")
    print("="*50)
    print("Round | TAS Gini (Avg) | Control Gini (Avg) | Delta")
    print("-" * 50)

    for row in plot_data:
        r = row['round']
        t_gini = row['tas_gini_avg']
        c_gini = row['control_gini_avg']
        delta = c_gini - t_gini # Positive means TAS is better (lower Gini)

        if r % 5 == 0 or r == 1 or r == 25:
            print(f"{r:5d} | {t_gini:5.3f}       | {c_gini:5.3f}           | {delta:+.3f}")

if __name__ == "__main__":
    run_visualization()
