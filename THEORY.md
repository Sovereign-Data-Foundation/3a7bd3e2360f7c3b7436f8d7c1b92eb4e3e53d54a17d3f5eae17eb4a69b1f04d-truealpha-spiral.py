# TAS Theoretical Framework: Stability via Invariant Projection

## 1. Introduction: The Constrained Multi-Agent Markov Decision Process (CM-MDP)

We define the True Alpha Spiral (TAS) system as a **Constrained Multi-Agent Markov Decision Process (CM-MDP)**. Unlike standard RL environments where safety is an auxiliary reward term, TAS treats safety as a geometric constraint on the state space.

Let \(\mathcal{S}\) be the state space representing resource distribution, and \(\mathcal{A}\) the joint action space of all agents. The transition function \(T: \mathcal{S} \times \mathcal{A} \to \mathcal{S}\) defines the system dynamics.

The objective is to maximize the collective reward \(R\) subject to the safety constraint \(C\):

\[
\max_{\pi} E_{\pi}\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t)\right] \quad \text{s.t.} \quad C(s_t) \leq \beta \quad \forall t
\]

Where \(\beta\) is the global instability threshold.

---

## 2. Theorem 1: Boundary Convergence

**Theorem:** Given a global instability threshold \(\beta\), the Phoenix Protocol \(\Phi\) guarantees that the system state \(S_t\) remains within the **Safe Manifold** \(\mathcal{S}_{safe} = \{s \in \mathcal{S} : \text{Hoard}(s) \le \beta\}\) for all \(t > 0\), regardless of the reward-seeking behavior of individual agents.

**Proof Sketch:**

1.  **Inductive Step:** Assume \(S_t \in \mathcal{S}_{safe}\).
2.  **Transition:** An agent \(i\) takes action \(a_i\) seeking to maximize \(R_i\), resulting in a proposed next state \(\hat{S}_{t+1}\).
3.  **Projection:** The Protocol \(\Phi\) acts as a gatekeeper:
    \[
    S_{t+1} = \mathbb{1}_{\mathcal{S}_{safe}}(\hat{S}_{t+1}) \cdot \hat{S}_{t+1} + (1 - \mathbb{1}_{\mathcal{S}_{safe}}(\hat{S}_{t+1})) \cdot S_{rollback}
    \]
4.  **Conclusion:** Since \(S_{rollback} \in \mathcal{S}_{safe}\) (by definition of the initial or stable state), then \(S_{t+1}\) is guaranteed to be in \(\mathcal{S}_{safe}\).

This projection mechanism ensures that the system cannot drift into irreversible collapse states, even under adversarial pressure from selfish agents.

---

## 3. Lemma 1: The "Incentive to Stabilize"

While the Phoenix Protocol is a hard constraint, it creates a **Secondary Incentive Gradient**. Because a rollback results in a loss of "tasks completed" (potential reward), agents governed by RLHF or local optimization will eventually learn to approximate the boundary of the invariant to avoid the cost of the reset.

Mathematically, the effective reward \(R'_{i}\) becomes:

\[
R'_{i}(s, a) = R_i(s, a) \cdot P(\text{Acceptance}) - \text{Cost}_{rollback} \cdot P(\text{Violation})
\]

This aligns the selfish interest of the agent with the structural integrity of the system, transforming the "Tragedy of the Commons" into a cooperative game.

---

## 4. Operationalizing the "DNA Module"

To make the TrueAlphaSpiral framework falsifiable, we define the "DNA" (invariant set) checking mechanism using **Total Variation Distance (TVD)**.

### 4.1 Drift Detection

The DNA module monitors the distribution of compute \(\mathcal{D}\). If the distance between the current distribution \(P\) and the "Equitable Distribution" \(Q\) exceeds the threshold \(\epsilon\), the system identifies "Ethical Drift."

\[
\delta(P, Q) = \sup_{A \in \mathcal{F}} |P(A) - Q(A)| > \epsilon
\]

This formal metric provides the trigger condition for the Phoenix Protocol, ensuring that intervention is based on measurable statistical divergence rather than arbitrary rules.
