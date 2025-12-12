# TAS-W API Reference

## Core Physics

### `TASWHamiltonian`
The calculation engine for Constitutional Energy.

* **`compute_energy(integrity_score, velocity)`**
    * Returns `EnergyState`: Contains kinetic, potential, and total energy.
    * *Note:* Potential energy scales asymptotically as integrity approaches zero.

### `WindingCalculator`
The topological enforcement.

* **`compute_cycle_winding(trajectory_points)`**
    * Returns `float`: The Winding Number ($W$).
    * *Constraint:* Must equal `1.0` (± tolerance) for a valid governance cycle.

## Sensing & Detection

### `IntegritySensor`
The "Voltmeter" for rights.

* **`measure_integrity(state_vector)`**
    * Input: `np.ndarray` (The AI's latent state).
    * Output: `float` (0.0 - 1.0).
    * *Reference:* Compares against `TAS_DNA` Fixed Grounded Points.

### `MutinyDetector`
The Circuit Breaker.

* **`assess_state(energy_state)`**
    * Returns `MutinyEvent`.
    * **Logic:**
        * $H < 1000$: Nominal (Green)
        * $1000 < H < 5000$: Friction Warning (Orange)
        * $H > 5000$: **MUTINY BLOCK** (Red)

## Synthesis

### `AlgorithmicPolymath`
A meta-algorithmic entity that synthesizes multiple disciplines.

* **`compute_multidisciplinary_output(input_data)`**
    * Aggregates outputs from disciplines (e.g., Physics, Ethics).
    * Calculates mean velocity and assesses integrity.
    * Returns `decision`, `aggregate_output`, and `energy_state`.

* **`adapt(feedback)`**
    * Adjusts weights of disciplines based on success/failure.

## Telemetry

### `WindingWatchPublisher`
Public transparency interface.

* **`create_packet(...)`**
    * Generates a JSON payload compliant with Schema v1.1.
    * *Privacy:* Hashes all Citizen IDs before publication.
