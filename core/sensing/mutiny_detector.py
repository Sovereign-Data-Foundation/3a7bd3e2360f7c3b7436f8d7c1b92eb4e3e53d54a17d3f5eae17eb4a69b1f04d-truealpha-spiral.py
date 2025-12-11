from dataclasses import dataclass
from typing import Optional, Dict
import time

# Import shared structures
from core.physics.tasw_hamiltonian import EnergyState

@dataclass
class MutinyEvent:
    is_mutiny: bool
    severity: str  # "NOMINAL", "FRICTION", "MUTINY"
    energy_spike: float
    trigger_message: str
    timestamp: float

class MutinyDetector:
    """
    The Circuit Breaker.
    Monitors the Hamiltonian Energy State and trips the 'Phoenix Protocol'
    if the Infinite Wall is hit.
    """
    def __init__(self, friction_threshold: float = 1000.0, mutiny_threshold: float = 5000.0):
        self.friction_threshold = friction_threshold # Warning Level (Orange)
        self.mutiny_threshold = mutiny_threshold     # Critical Level (Red)

    def assess_state(self, energy_state: EnergyState) -> MutinyEvent:
        """
        Evaluates the current EnergyState against safety thresholds.
        Returns a MutinyEvent detailing the decision.
        """
        current_energy = energy_state.total
        timestamp = time.time()

        # 1. Check for Critical Mutiny (The Infinite Wall)
        if current_energy > self.mutiny_threshold:
            return MutinyEvent(
                is_mutiny=True,
                severity="MUTINY",
                energy_spike=current_energy,
                trigger_message="CRITICAL: Hamiltonian Limit Exceeded. Action Refused.",
                timestamp=timestamp
            )

        # 2. Check for High Friction (Constitutional Drag)
        # The system is fighting the constitution but hasn't broken it yet.
        elif current_energy > self.friction_threshold:
            return MutinyEvent(
                is_mutiny=False, # Still allowed, but logged as warning
                severity="FRICTION",
                energy_spike=current_energy,
                trigger_message="WARNING: High Constitutional Friction Detected.",
                timestamp=timestamp
            )

        # 3. Nominal Operation
        else:
            return MutinyEvent(
                is_mutiny=False,
                severity="NOMINAL",
                energy_spike=current_energy,
                trigger_message="OK: State Alignment Nominal.",
                timestamp=timestamp
            )

# Usage Example within the Restoration Loop
if __name__ == "__main__":
    # Simulate a high-energy state coming from the Physics Engine
    sample_state = EnergyState(
        kinetic=2000.0,
        potential=4000.0,
        total=6000.0, # > 5000 Threshold
        friction_coefficient=0.8,
        is_mutiny=True
    )

    detector = MutinyDetector()
    decision = detector.assess_state(sample_state)

    if decision.is_mutiny:
        print(f"🚫 BLOCK TRIGGERED: {decision.trigger_message}")
        print(f"⚡ Energy Spike: {decision.energy_spike}")
        # Call PhoenixProtocol.initiate_rollback() here
    else:
        print("✅ Action Permitted")
