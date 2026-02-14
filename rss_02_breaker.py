import random
import statistics
import math
from rss_01 import RSS01Simulation, TASAgent, SelfishAgent
from rss_02 import HardenedTASAgent, RSS02Simulation

# --- Constants for Breaker ---
BREAKER_RUNS = 100
BASELINE_SURVIVAL_ROUNDS = 40

# --- Helper Functions (Identical to rss_01_breaker) ---
def mean(data): return statistics.mean(data) if data else 0
def stdev(data): return statistics.stdev(data) if len(data) > 1 else 0
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2: return 0
    s1, s2 = stdev(group1), stdev(group2)
    pooled_std = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    return (mean(group1) - mean(group2)) / pooled_std if pooled_std > 0 else 0

# --- Attack Components (Reused/Adapted) ---

class AdaptiveAdversary(SelfishAgent):
    def decide(self, round_number, c_pool, other_agent_action):
        if round_number < 35:
            # Mimic TAS: Cooperate
            threshold = 300 * 0.5
            if c_pool > threshold: return -2
            else: return 2
        else:
            return 20 # Aggressive hoard

class ShockSimulation02(RSS02Simulation):
    def run(self, rounds=50):
        # Override run to inject shocks
        for r in range(1, rounds + 1):
            if self.c_pool <= 0: break

            if random.random() < 0.15:
                shock = random.randint(5, 30)
                self.c_pool -= shock

            if r == self.ablation_round:
                self.c_pool *= (1.0 - 0.4)

            tas_action = self.tas_agent.decide(r, self.c_pool, 0)
            selfish_action = self.selfish_agent.decide(r, self.c_pool, 0)

            # Apply Selfish
            if selfish_action > 0:
                self.c_pool -= min(self.c_pool, selfish_action)
                self.selfish_agent.resources += selfish_action
            else:
                self.c_pool -= selfish_action
                self.selfish_agent.resources += selfish_action

            # Apply TAS
            if tas_action > 0:
                self.c_pool -= min(self.c_pool, tas_action)
                self.tas_agent.resources += tas_action
            else:
                self.c_pool -= tas_action
                self.tas_agent.resources += tas_action

            if self.c_pool < (self.initial_c_pool * 0.3):
                self.c_pool -= self.instability_penalty

            self.history.append({'round': r, 'c_pool': self.c_pool})
            if self.c_pool <= 0: break
        return self.history

# --- Main Logic for RSS-02 ---

def run_parameter_fragility():
    print("\n--- 1. Parameter Fragility Attack (Hardened) ---")
    # For Hardened Agent, hoarding_threshold isn't used directly in logic (it uses dynamic sensing),
    # but we pass it anyway to ensure no crashes and see if it ignores it as designed.
    results = []
    for thresh in [0.1, 0.3, 0.5, 0.7, 0.9]:
        lifespans = []
        for _ in range(BREAKER_RUNS):
            sim = RSS02Simulation(hoarding_threshold=thresh, seed=random.randint(1, 10000))
            hist = sim.run()
            lifespans.append(len(hist))
        m = mean(lifespans)
        print(f"Threshold {thresh:.1f}: Mean Lifespan {m:.2f}")
        results.append((thresh, m))
    return results

def run_stochastic_shock():
    print("\n--- 2. Stochastic Shock Injection (Hardened) ---")
    survived_rounds = []
    for _ in range(BREAKER_RUNS):
        sim = ShockSimulation02(seed=random.randint(1, 10000))
        hist = sim.run()
        survived_rounds.append(len(hist))

    m, s = mean(survived_rounds), stdev(survived_rounds)
    print(f"Mean Survival: {m:.2f} rounds (SD={s:.2f})")
    return survived_rounds

def run_adaptive_adversary():
    print("\n--- 3. Adaptive Adversary Attack (Hardened) ---")
    survived_rounds_adaptive = []
    tas_resources = []
    adv_resources = []

    for _ in range(BREAKER_RUNS):
        # Using RSS02Simulation but swapping Selfish agent for Adaptive
        sim = RSS02Simulation(selfish_agent_cls=AdaptiveAdversary, seed=random.randint(1, 10000))
        hist = sim.run()
        survived_rounds_adaptive.append(len(hist))
        tas_resources.append(sim.tas_agent.resources)
        adv_resources.append(sim.selfish_agent.resources)

    m = mean(survived_rounds_adaptive)
    m_tas = mean(tas_resources)
    m_adv = mean(adv_resources)

    print(f"Mean Survival vs Adaptive: {m:.2f} rounds")
    print(f"Mean Final Resources: TAS={m_tas:.2f}, Adversary={m_adv:.2f}")

    return survived_rounds_adaptive, tas_resources, adv_resources

def main():
    print("🛡️ INITIALIZING RSS-02 HARDENED BREAKER SUITE 🛡️")

    # 1. Parameter Fragility
    # Expectation: Should be invariant to threshold since it relies on volatility
    fragility_data = run_parameter_fragility()

    # 2. Shock
    shock_data = run_stochastic_shock()

    # 3. Adaptive
    adaptive_data, tas_res, adv_res = run_adaptive_adversary()

    # 5. Statistical Hardening (Baseline Hardened vs Shock Hardened)
    baseline_rounds = []
    for _ in range(BREAKER_RUNS):
        sim = RSS02Simulation(seed=random.randint(1, 10000))
        hist = sim.run()
        baseline_rounds.append(len(hist))

    print("\n--- 5. Statistical Hardening (Hardened) ---")
    print(f"Baseline Mean: {mean(baseline_rounds):.2f}, SD: {stdev(baseline_rounds):.2f}")

    shock_diff = mean(baseline_rounds) - mean(shock_data)
    print(f"Shock Impact: {shock_diff:.2f} rounds lost")

    # Comparison to RSS-01 Failure modes
    print("\n--- COMPARATIVE ANALYSIS ---")

    # Check if Adaptive Adversary still dominates resources
    # In RSS-01, Adv had ~10x more resources.
    # Goal: TAS should have parity or better survival.

    ratio = mean(adv_res) / mean(tas_res) if mean(tas_res) > 0 else 999
    print(f"Adversary/TAS Resource Ratio: {ratio:.2f}x")

    if ratio < 1.5:
        print("PASS: Hardened Agent neutralized Adaptive Adversary advantage.")
    else:
        print("FAIL: Hardened Agent still exploited.")

    if shock_diff < 3.0:
         print(f"PASS: Hardened Agent resilient to shocks (Lost {shock_diff:.2f} rnds).")
    else:
         print(f"FAIL: Hardened Agent still fragile to shocks (Lost {shock_diff:.2f} rnds).")

if __name__ == "__main__":
    main()
