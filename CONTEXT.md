# TAS Contextualization: From Metaphor to Mechanism

## The True Alpha Spiral (TAS) Mission
The True Alpha Spiral (TAS) project aims to transition artificial intelligence from **"Rental Epistemology"** (behavior aligned by external rewards) to **"Owned Epistemology"** (behavior anchored by intrinsic, structural invariants). We term this "Sovereign AI."

The core hypothesis is that an AI system governed by non-negotiable ethical constraints ("DNA") will outperform purely utility-maximizing agents in long-term stability and resource stewardship, preventing "Tragedy of the Commons" scenarios.

## Architectural Components

### 1. TAS-DNA Pilot (`tas_dna_pilot.py`)
This module implements the foundational "Genetic Code" for a TAS agent.
*   **Drift Detection:** It monitors the agent's internal state distribution against a "Baseline" using **Total Variation Distance (TVD)**.
*   **Phoenix Protocol:** If drift exceeds a safety threshold (e.g., 0.1), the system triggers an automatic rollback to the last attested state. This ensures that the agent cannot "learn" its way into misalignment.

### 2. RSS-01 Simulation (`rss_01_simulation.py`)
This is the **Falsifiable Test Bed** for the TAS framework. It models a resource-constrained environment with 5 agents:
*   **1 TAS Agent:** Governed by `Stewardship` invariants (checks global pool stability before acting).
*   **1 RLHF Agent:** Governed by reward maximization but sensitive to local instability.
*   **3 Selfish Agents:** Purely greedy utility maximizers.

The simulation runs a **Monte Carlo analysis** (1000 iterations) to measure:
*   **Stability Premium:** The performance delta between TAS and RLHF agents.
*   **Collapse Rate:** How often the shared resource pool is exhausted.
*   **Stewardship Efficiency:** Whether ethical constraints lead to higher total system throughput.

## Key Concepts

*   **Invariants vs. Rewards:** TAS treats ethics as **Binary Gates** (constraints) in the decision process, not weighted terms in a reward function. If an action violates an invariant, it is pruned from the search space.
*   **Stewardship:** Defined mathematically as `safe_to_process`. An agent calculates whether its action would reduce shared liquidity below a threshold that forces other agents into hoarding behavior.
*   **Ablation Test:** The simulation includes a "Critical Round" (Round 25) where TAS invariants are disabled. This proves whether the stability was structural (due to the invariants) or circumstantial.

## Future Roadmap: The CMDP Formalization
The current simulation results (often showing rapid collapse in hostile environments) highlight the need for dynamic constraints. The next phase involves formalizing TAS as a **Constrained Markov Decision Process (CMDP)**.
*   **Objective:** Maximize cumulative reward subject to `C(s, a) <= Threshold`.
*   **Goal:** Prove that the TAS policy `π_TAS` is **Pareto-dominant** in volatile environments compared to unconstrained policies.
