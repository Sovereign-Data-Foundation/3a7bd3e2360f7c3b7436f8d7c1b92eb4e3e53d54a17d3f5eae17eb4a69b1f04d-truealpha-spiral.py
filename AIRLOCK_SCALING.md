# Scaling the Thermodynamic Airlock

The `airlock_gate` function in `tas_core/alpha/airlock.py` serves as the foundational "physics engine" of TrueAlphaSpiral (TAS). By defining the cost of an idea as `(1 - Coherence) * e^Resonance`, it creates an exponential penalty for complex fabrications.

This document reviews the current implementation and proposes mathematical models for scaling this "honesty-by-design" framework to handle more complex reasoning tasks.

## 1. Current Implementation Review

The current `airlock_gate` is an elegant abstraction:

```python
def airlock_gate(coherence, resonance):
    if coherence >= 1.0:
        cost = 0.0
    elif resonance > 709.0:
        cost = float('inf')
    else:
        cost = (1.0 - coherence) * math.exp(resonance)

    if math.isnan(cost) or cost > MAX_ENERGY_COST:
        return AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH, cost

    return AIRLOCK_PASSED, cost
```

### Strengths:
* **The Exponential Wall:** `math.exp(resonance)` ensures that as an idea becomes more complex (higher resonance), the penalty for even slight deviations from truth (low coherence) scales exponentially. It physically prevents "big lies."
* **Computational Safety:** The explicit checks for `coherence >= 1.0` and `resonance > 709.0` prevent unnecessary floating-point operations and `OverflowError` crashes.
* **Deterministic Threshold:** The hard `MAX_ENERGY_COST` (5.0) provides a clear, un-hackable boundary.

### Limitations for Complex Reasoning:
* **Static Dimensions:** It currently relies on two 1D variables (`coherence` and `resonance`). Complex reasoning (e.g., multi-step logic, code generation) often has varying levels of certainty across different dimensions (syntax, logic, context).
* **Lack of Temporal Decay/Momentum:** In a multi-step chain of thought, an early error should propagate and compound the cost of subsequent steps. The current model evaluates ideas in isolation.

## 2. Proposed Mathematical Scaling Models

To scale the Thermodynamic Airlock for complex reasoning, we must transition from evaluating isolated ideas to evaluating **chains of thought** (CoT) and **multi-dimensional assertions**.

### Model A: The Markovian Airlock (Temporal Scaling)

For multi-step reasoning, the cost of step $t$ must be a function of the coherence of step $t$ *and* the accumulated cost of previous steps.

Let $C_t$ be the coherence of the current step, and $R_t$ be its resonance. Let $E_{t-1}$ be the accumulated energy cost prior to this step.

$$ E_t = E_{t-1} + [ (1 - C_t) \cdot e^{R_t} \cdot (1 + \lambda E_{t-1}) ] $$

*   **The Penalty Multiplier $(1 + \lambda E_{t-1})$:** $\lambda$ is a compounding factor. If the system is already "running hot" (high prior errors), the energy cost of a new fabrication is amplified. This forces the system to self-correct early, or face inevitable threshold rejection.

### Model B: The Vector Space Airlock (Dimensional Scaling)

For complex tasks (like writing a python script), "Coherence" isn't a single number. It's a vector: $[\text{Syntax}, \text{Logic}, \text{Context}]$.

Let $\vec{C}$ be the coherence vector and $\vec{W}$ be a weight vector denoting the importance of each dimension. The resonance $R$ remains a scalar magnitude of the task's complexity.

We define an "Error Vector": $\vec{\epsilon} = \vec{1} - \vec{C}$

The new cost function becomes the dot product of the weighted error vector, scaled by resonance:

$$ \text{Cost} = (\vec{\epsilon} \cdot \vec{W}) \cdot e^R $$

This allows the Airlock to enforce different tolerances. For example, a minor Context error might have a low weight, allowing passage, but a Syntax error (which breaks the program) has a high weight, triggering immediate rejection.

### Model C: The Thermodynamic Hamiltonian (System-Wide Scaling)

To fully implement the "Ethical Hamiltonian" described in the TAS philosophy, we must model the entire system's state space.

Let $\psi$ represent the current state of the reasoning engine. We define a Hamiltonian operator $\hat{H}$ that measures the total "ethical energy" (drift) of the system:

$$ \hat{H}\psi = E_{drift}\psi $$

If $E_{drift} > \kappa_{limit}$ (the fractal boundary), the `Phoenix Protocol` is triggered. This requires calculating the "kinetic energy" of the generation (how fast it's producing tokens) and the "potential energy" of the semantic landscape (how far it is from verified ground truth).

## 3. Implementation Pathway

1.  **Refactor `airlock_gate`:** Update the function signature to accept vectors or lists of historical states to implement Model A or B.
2.  **Define Coherence Metrics:** We need concrete, programmatic ways to measure `coherence`. For code, this could be static analysis scores (pylint) or test pass rates. For text, it could be cross-validation against a trusted knowledge base.
3.  **Establish Phoenix Triggers:** Integrate the new scaled `cost` calculation directly into the `tas_core.alpha.airlock` module, ensuring that a breach of `MAX_ENERGY_COST` instantly invokes the rollback mechanism defined in the `Phoenix Protocol`.
