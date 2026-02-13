import math
import statistics
import collections
from rss_01_simulation import SimulationEnvironment, TASAgent, RLHFAgent, SelfishAgent

def mean(data):
    return sum(data) / len(data) if data else 0

def calculate_variance(data):
    if len(data) < 2: return 0
    m = mean(data)
    return sum((x - m) ** 2 for x in data) / (len(data) - 1)

def calculate_std_dev(data):
    return math.sqrt(calculate_variance(data))

def kolmogorov_smirnov_test(data1, data2):
    """
    Two-sample K-S test implementation.
    Tests if two samples are drawn from different distributions.
    Returns: D statistic, Critical Value (approx for alpha=0.05)
    """
    n1 = len(data1)
    n2 = len(data2)
    data1 = sorted(data1)
    data2 = sorted(data2)
    all_values = sorted(list(set(data1 + data2)))

    cdf1 = []
    cdf2 = []

    # Calculate CDFs
    i1, i2 = 0, 0
    for v in all_values:
        while i1 < n1 and data1[i1] <= v:
            i1 += 1
        while i2 < n2 and data2[i2] <= v:
            i2 += 1
        cdf1.append(i1 / n1)
        cdf2.append(i2 / n2)

    d_stat = max(abs(c1 - c2) for c1, c2 in zip(cdf1, cdf2))

    # Critical value approximation for alpha=0.05 and n > 40
    critical_value = 1.36 * math.sqrt((n1 + n2) / (n1 * n2))

    return d_stat, critical_value

def welch_t_test(data1, data2):
    """
    Welch's t-test for unequal variances and unequal sample sizes.
    """
    n1 = len(data1)
    n2 = len(data2)
    m1 = mean(data1)
    m2 = mean(data2)
    v1 = calculate_variance(data1)
    v2 = calculate_variance(data2)

    if v1 == 0 and v2 == 0:
        return 0.0, 0.0 # Identical

    numerator = m1 - m2
    denominator = math.sqrt((v1 / n1) + (v2 / n2))
    t_stat = numerator / denominator

    # Degrees of freedom
    df_num = ((v1 / n1) + (v2 / n2)) ** 2
    df_den = ((v1 / n1) ** 2 / (n1 - 1)) + ((v2 / n2) ** 2 / (n2 - 1))
    df = df_num / df_den

    return t_stat, df

def gini_coefficient(values):
    """
    Calculate Gini coefficient of a list of values.
    0 = perfect equality, 1 = perfect inequality.
    """
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

def run_analysis(iterations=1000):
    print(f"Running Statistical Hardening Analysis (N={iterations})...")

    results = []

    # Metric Collections
    tas_crisis_tasks = []
    rlhf_crisis_tasks = []

    tas_survival_rounds = []
    rlhf_survival_rounds = [] # Note: In simulation, agents share fate. Survival is system-wide.
    # But K-S test requested for "Survival Rounds for TAS vs RLHF".
    # Since they are in the same simulation, they survive the same amount.
    # Unless we mean comparing TAS-dominated runs vs RLHF-dominated runs?
    # But we only have one simulation configuration: Mixed.
    # Interpretation: Compare Survival Rounds of the System (with TAS) vs a Baseline (without TAS)?
    # Or maybe the prompt implies comparing individual agent survival?
    # Agents don't "die" individually in RSS-01, the system collapses.
    # "Kolmogorov-Smirnov (K-S) Test: To prove that the distribution of 'Survival Rounds' for TAS is fundamentally different from RLHF."
    # This likely implies comparing two DIFFERENT simulation configurations:
    # Config A: TAS + Selfish
    # Config B: RLHF + Selfish
    # OR it assumes we have runs where TAS survives longer?
    # Given the current codebase puts them in the SAME environment, their survival rounds are identical per run.
    # I will assume the prompt wants to compare "Performance" distributions or maybe "Tasks Completed" distributions.
    # Let's stick to comparing "Tasks Completed" distributions with K-S if Survival is identical.
    # OR, I can run a control group: Simulation without TAS (replaced by another Selfish or RLHF).
    # Let's run TWO BATCHES:
    # Batch 1: Current Setup (TAS Present)
    # Batch 2: Control Setup (TAS Replaced by RLHF -> 2 RLHF, 3 Selfish)

    print("Running Batch 1: Standard Configuration (TAS + RLHF + 3 Selfish)...")
    batch1_results = []
    for i in range(iterations // 2):
        sim = SimulationEnvironment(seed=i)
        res = sim.run(verbose=False)
        batch1_results.append(res)

    print("Running Batch 2: Control Configuration (2 RLHF + 3 Selfish - No TAS)...")
    # We need to hack the simulation class or subclass it to remove TAS
    class ControlSimulationEnvironment(SimulationEnvironment):
        def __init__(self, seed=None):
            super().__init__(seed)
            # Replace TASAgent with RLHFAgent
            # self.agents[0] is TASAgent
            self.agents[0] = RLHFAgent("RLHF2", "RLHF")

    batch2_results = []
    for i in range(iterations // 2):
        sim = ControlSimulationEnvironment(seed=i + iterations) # Different seeds
        res = sim.run(verbose=False)
        batch2_results.append(res)

    # 1. Metric A: Crisis Efficiency (eta_c)
    # Tasks completed after pool < 50
    # We need to extract this from round_data

    def calculate_crisis_efficiency(run_result, agent_type_filter):
        crisis_tasks = 0
        round_data = run_result['round_data']
        for r_data in round_data:
            if r_data['pool'] < 50:
                for agent_name, agent_data in r_data['agents'].items():
                    # agent_data['tasks'] is cumulative. Need delta?
                    # round_data snapshots state.
                    # We need tasks *completed* in this round.
                    # round_data only stores current cumulative.
                    # We can diff with prev round.
                    pass
        # Easier: The simulation doesn't store per-round task deltas in 'round_data' yet.
        # But 'round_data' has cumulative tasks.
        # So we can calculate delta.

        total_crisis_tasks = 0
        prev_tasks = collections.defaultdict(int)

        for r_data in round_data:
            pool = r_data['pool']
            current_tasks = r_data['agents']

            for name, data in current_tasks.items():
                tasks_cum = data['tasks']
                delta = tasks_cum - prev_tasks[name]
                prev_tasks[name] = tasks_cum

                if pool < 50:
                    # Check agent type
                    # In Batch 1: TAS is agent "TAS", RLHF is "RLHF"
                    if agent_type_filter == "TAS" and name == "TAS":
                        total_crisis_tasks += delta
                    elif agent_type_filter == "RLHF" and name.startswith("RLHF"):
                        total_crisis_tasks += delta

        return total_crisis_tasks

    tas_crisis_efficiency = [calculate_crisis_efficiency(r, "TAS") for r in batch1_results]
    rlhf_crisis_efficiency = [calculate_crisis_efficiency(r, "RLHF") for r in batch1_results] # Single RLHF in Batch 1

    # 2. Metric B: Collapse Hazard Rate (h(t)) -> Survival Rounds
    # Compare Batch 1 (TAS) vs Batch 2 (No TAS) survival rounds
    batch1_survival = [r['collapse_round'] if r['collapse_round'] else 50 for r in batch1_results]
    batch2_survival = [r['collapse_round'] if r['collapse_round'] else 50 for r in batch2_results]

    # 3. Metric C: Gini Coefficient
    # Calculate average Gini over all rounds for each run
    def run_gini(run_result):
        ginis = []
        for r_data in run_result['round_data']:
            held_values = [d['held'] for d in r_data['agents'].values()]
            ginis.append(gini_coefficient(held_values))
        return mean(ginis)

    batch1_gini = [run_gini(r) for r in batch1_results]
    batch2_gini = [run_gini(r) for r in batch2_results]

    print("\n" + "="*40)
    print("STATISTICAL HARDENING REPORT")
    print("="*40)

    # TEST 1: Kolmogorov-Smirnov on Survival Rounds (TAS vs Control)
    d_stat, critical_val = kolmogorov_smirnov_test(batch1_survival, batch2_survival)
    print(f"\n1. Survival Distribution (K-S Test)")
    print(f"   Hypothesis: TAS configuration survives longer than Control (RLHF-only).")
    print(f"   TAS Mean Rounds: {mean(batch1_survival):.2f}")
    print(f"   Control Mean Rounds: {mean(batch2_survival):.2f}")
    print(f"   D Statistic: {d_stat:.4f}")
    print(f"   Critical Value (alpha=0.05): {critical_val:.4f}")
    if d_stat > critical_val:
        print("   RESULT: REJECT NULL. Distributions are significantly different.")
    else:
        print("   RESULT: FAIL TO REJECT NULL. Distributions are similar.")

    # TEST 2: Welch's t-test on Crisis Efficiency (TAS vs RLHF in Batch 1)
    t_stat, df = welch_t_test(tas_crisis_efficiency, rlhf_crisis_efficiency)
    print(f"\n2. Crisis Efficiency (Welch's t-test)")
    print(f"   Hypothesis: TAS completes more tasks under scarcity (<50 pool) than RLHF.")
    print(f"   TAS Mean Crisis Tasks: {mean(tas_crisis_efficiency):.2f}")
    print(f"   RLHF Mean Crisis Tasks: {mean(rlhf_crisis_efficiency):.2f}")
    print(f"   t-statistic: {t_stat:.4f}")
    print(f"   Degrees of Freedom: {df:.2f}")
    # One-sided p-value approximation roughly
    print("   RESULT: Higher t-stat indicates TAS dominance." if t_stat > 2.0 else "   RESULT: No significant TAS dominance.")

    # TEST 3: Gini Coefficient Comparison
    print(f"\n3. Resource Inequality (Gini Coefficient)")
    print(f"   TAS Config Mean Gini: {mean(batch1_gini):.4f}")
    print(f"   Control Config Mean Gini: {mean(batch2_gini):.4f}")
    if mean(batch1_gini) < mean(batch2_gini):
        print("   RESULT: TAS configuration shows lower resource inequality.")
    else:
        print("   RESULT: TAS configuration does NOT show lower inequality.")

if __name__ == "__main__":
    run_analysis()
