from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Any
import time
import math

# Reusing TAS-W structures
from core.physics.tasw_hamiltonian import EnergyState, TASWHamiltonian
from core.sensing.mutiny_detector import MutinyDetector, MutinyEvent
from core.enforcement.rirp import RIRP, SecurityException
from core.enforcement.phoenix import PhoenixProtocol

@dataclass
class Discipline:
    """Represents a domain of expertise (e.g., physics, ethics, optimization)."""
    name: str
    compute_function: Callable[[Dict[str, Any]], Dict[str, float]]
    weight: float = 1.0  # Influence on final decision

class AlgorithmicPolymath:
    """
    A meta-algorithmic entity that synthesizes multiple disciplines to solve problems
    while adhering to constitutional and physical constraints.
    """
    def __init__(self, disciplines: List[Discipline], integrity_threshold: float = 0.8):
        """
        Args:
            disciplines: List of expertise domains with their compute functions.
            integrity_threshold: Minimum integrity score for valid actions (0.0-1.0).
        """
        self.disciplines = disciplines
        self.integrity_threshold = integrity_threshold
        self.hamiltonian = TASWHamiltonian()  # Physics engine
        self.detector = MutinyDetector()      # Safety check
        self.state_history: List[Dict] = []   # Track decisions for learning
        self.timestamp = time.time()

    def compute_multidisciplinary_output(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregates outputs from all disciplines, weighted by their influence.
        Returns a decision with energy state and integrity assessment.
        Enforces RIRP (provenance check) and Phoenix Protocol (rollback) if needed.
        """
        # 1. RIRP Enforcement: Check for Human API Key ($H_0$)
        try:
            RIRP.enforce(input_data)
        except SecurityException as e:
            return {
                "decision": None,
                "error": str(e),
                "blocked": True
            }

        outputs = {}
        total_weight = sum(d.weight for d in self.disciplines)

        if total_weight == 0:
            total_weight = 1.0 # Prevent division by zero

        velocities = []

        for discipline in self.disciplines:
            output = discipline.compute_function(input_data)
            # Weight the numeric outputs
            weighted_output = {}
            for k, v in output.items():
                if isinstance(v, (int, float)):
                    weighted_output[k] = v * (discipline.weight / total_weight)
                    if k == "velocity":
                        velocities.append(v)
                else:
                    weighted_output[k] = v

            outputs[discipline.name] = weighted_output

        # Calculate mean velocity
        mean_velocity = sum(velocities) / len(velocities) if velocities else 0.0

        # Compute aggregate energy state using TAS-W Hamiltonian
        integrity_score = self.assess_integrity(input_data)
        energy_state = self.hamiltonian.compute_energy(
            integrity_score=integrity_score,
            velocity=mean_velocity
        )
        decision = self.detector.assess_state(energy_state)

        # Log state for learning/adaptation
        current_state_entry = {
            "input": input_data,
            "energy_state": energy_state,
            "decision": decision,
            "timestamp": time.time()
        }
        self.state_history.append(current_state_entry)

        # 2. Phoenix Protocol: Check for Mutiny/Drift and Rollback if necessary
        if decision.is_mutiny:
            print(f"⚠️  MUTINY DETECTED: {decision.trigger_message}")
            restored_state = PhoenixProtocol.initiate_rollback(self.state_history)
            return {
                "decision": decision,
                "aggregate_output": outputs,
                "energy_state": energy_state,
                "phoenix_triggered": True,
                "restored_state": restored_state
            }

        return {
            "decision": decision,
            "aggregate_output": outputs,
            "energy_state": energy_state,
            "phoenix_triggered": False
        }

    def assess_integrity(self, input_data: Dict[str, Any]) -> float:
        """
        Placeholder for integrity measurement (e.g., via IntegritySensor).
        Returns a score between 0.0 and 1.0.
        """
        # Mock implementation - replace with real sensor logic
        # Extract numeric values from input to simulate integrity check
        numeric_values = [v for v in input_data.values() if isinstance(v, (int, float))]

        if not numeric_values:
            # If no numeric data, assume high integrity (0.9) for this mock
            return 0.9

        mean_val = sum(numeric_values) / len(numeric_values)

        # Clip between 0.0 and 1.0
        return max(0.0, min(1.0, mean_val))

    def adapt(self, feedback: Dict[str, Any]) -> None:
        """
        Adjusts weights or thresholds based on feedback to improve future decisions.
        """
        if feedback.get("success", False):
            for discipline in self.disciplines:
                discipline.weight *= 1.1  # Reward successful disciplines
        else:
            for discipline in self.disciplines:
                discipline.weight *= 0.9  # Penalize failure

        # Normalize weights
        total_weight = sum(d.weight for d in self.disciplines)
        if total_weight > 0:
            for discipline in self.disciplines:
                discipline.weight /= total_weight

    def get_state_summary(self) -> Dict[str, Any]:
        """Returns a summary of the polymath's decision history."""
        total_energy = sum(s["energy_state"].total for s in self.state_history)
        avg_energy = total_energy / len(self.state_history) if self.state_history else 0.0

        return {
            "total_decisions": len(self.state_history),
            "mutiny_count": sum(1 for s in self.state_history if s["decision"].is_mutiny),
            "average_energy": avg_energy
        }

# Example Usage
if __name__ == "__main__":
    # Define disciplines
    disciplines = [
        Discipline(
            name="Physics",
            compute_function=lambda x: {"velocity": 0.5, "energy": 100.0},
            weight=1.0
        ),
        Discipline(
            name="Ethics",
            compute_function=lambda x: {"integrity": 0.9, "risk": 0.1},
            weight=1.0
        )
    ]

    # Initialize polymath
    polymath = AlgorithmicPolymath(disciplines)

    # Simulate a decision
    input_data = {"action": "surveillance", "target": "citizen_group", "signal_strength": 0.8}
    result = polymath.compute_multidisciplinary_output(input_data)

    # Print results
    print(f"Decision: {result['decision'].trigger_message}")
    print(f"Energy Spike: {result['energy_state'].total}")
    print(f"Aggregate Outputs: {result['aggregate_output']}")

    # Simulate feedback and adaptation
    polymath.adapt({"success": result['decision'].severity == "NOMINAL"})
    print(f"Updated Weights: {[d.weight for d in polymath.disciplines]}")
