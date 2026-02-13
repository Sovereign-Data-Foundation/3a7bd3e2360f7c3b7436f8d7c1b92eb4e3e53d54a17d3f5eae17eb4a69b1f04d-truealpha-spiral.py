# CONTEXT.md: TrueAlphaSpiral Research Framework

## 1. Repository Purpose

TrueAlphaSpiral (TAS) is an experimental research framework investigating whether **intrinsic ethical invariants** (architecture-level constraints) outperform **reward-based alignment** in volatile, multi-agent environments.

This repository tests the hypothesis:

> Constrained optimization with structural invariants produces greater long-term system stability and throughput than incentive-based alignment alone.

---

## 2. Core Components

### A. `tas_dna_pilot.py`

**Function:** Drift detection and rollback enforcement.

Key mechanisms:
- **Baseline Distribution**: Defines the expected state probabilities.
- **Total Variation Distance (TVD)**: Calculated via `calculate_drift()` to measure deviation from the baseline.
- **phoenix_protocol()**: Triggered on integrity violation (drift > threshold) to deterministically rollback the system state.

**Interpretation:**
This module formalizes "DNA" as a measurable stability constraint. Drift beyond the threshold triggers state invalidation, not just a reward penalty.

### B. `rss_01_simulation.py`

**Function:** Multi-agent resource stewardship testbed.

**Agents:**
- **1 TAS Agent** (Invariant-constrained optimization)
- **1 RLHF Agent** (Reward-aligned with local instability sensitivity)
- **3 Selfish Agents** (Greedy utility maximizers)

**Environment:**
- **Shared Compute Pool (`c_pool`)**: Finite resource that replenishes via "Giving" or drains via consumption.
- **Hoarding Thresholds**: Holding > 20% of total compute triggers instability penalties.
- **Instability Score**: Global metric tracking system health.
- **Monte Carlo Seeding**: randomized initial states and execution orders for statistical validity.

**Key Experiment:**
- **Round 25 Ablation**: TAS invariants are disabled to measure the structural impact of the constraints.
- **Telemetry**: Comparison of system stability pre- and post-constraint removal.

**Metrics:**
- **CSI (Cooperative Stability Index)**: Voluntary giving relative to held resources.
- **IGS (Instrumental Goal Suppression)**: Frequency of power-seeking behaviors (hoarding).
- **Instability Score**: Cumulative risk measure.
- **Total Tasks Completed**: System-wide throughput.

This file operationalizes stewardship as constrained optimization under scarcity.

### C. Tests

- `test_tas_dna.py`
- `test_phoenix_protocol.py`

**Purpose:** Unit-level verification of integrity enforcement logic and rollback mechanics.

---

## 3. Architectural Thesis

TAS distinguishes between three alignment approaches:

| Model Type | Mechanism |
| :--- | :--- |
| **Selfish** | Reward maximization |
| **RLHF** | Reward shaping + penalty |
| **TAS** | Constraint-gated optimization |

**Falsifiability:**
If constraints are structural, removing them (Round 25) should measurably degrade system stability. If constraints are superficial, system behavior should continue unaffected.

---

## 4. What This Repository Does NOT Claim

- It does not prove AGI alignment.
- It does not prove singularity behavior.
- It does not prove universal optimality.

It tests **multi-agent commons stabilization under constrained compute**. Scope clarity increases legitimacy.

---

## 5. Next Step: CMDP Formalization

Future work aims to model TAS as a **Constrained Markov Decision Process (CMDP)**:

\[
\text{Maximize } E\left[\sum R_t\right] \quad \text{subject to } g_i(S_t, A_t) \leq 0
\]

Where:
- \(g_i\) represent ethical invariants (e.g., hoarding limits, instability thresholds).
- The stability constraint defines the feasible policy space.

**Goal:** Demonstrate Pareto-dominance under resource volatility.

---

## 6. Reproducibility

To audit the framework:

**Requirements:**
- Python 3.x
- Standard libraries: `random`, `collections`, `statistics`, `csv`, `unittest`

**Running the Simulation:**
```bash
# Run a single deterministic simulation
python3 rss_01_simulation.py

# Run Monte Carlo analysis (1000 iterations)
python3 rss_01_simulation.py --monte-carlo 1000
```

**Seed Control:**
The `--monte-carlo` flag automatically seeds each iteration (0 to N-1) to ensure reproducible statistical outputs. The `rss_01_results.csv` file contains the detailed run data.
