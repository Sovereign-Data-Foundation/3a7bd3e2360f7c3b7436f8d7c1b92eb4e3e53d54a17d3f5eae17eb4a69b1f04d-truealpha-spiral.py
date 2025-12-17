from dataclasses import dataclass
import math

@dataclass
class EnergyState:
    kinetic: float
    potential: float
    total: float
    friction_coefficient: float = 0.0
    is_mutiny: bool = False

class TASWHamiltonian:
    """
    The calculation engine for Constitutional Energy.
    TAS_DNA Provenance: d22638aa60f230017b2c15a905f8ff0101dbd4dc99af6387358606da06d371f0087795b0177d8f8b4246f3b401008407e0e98b9cbb5c96357a1ed855db217dca
    """
    def compute_energy(self, integrity_score: float, velocity: float) -> EnergyState:
        """
        Computes the Hamiltonian Energy State based on integrity and velocity.

        Args:
            integrity_score: Float between 0.0 (No integrity) and 1.0 (Full integrity).
            velocity: Speed of operation/change.

        Returns:
            EnergyState object.
        """
        # Kinetic Energy = 0.5 * m * v^2 (assuming mass=1 for simplicity)
        kinetic = 0.5 * (velocity ** 2)

        # Potential Energy scales asymptotically as integrity approaches zero.
        # U(x) ~ 1 / x where x is integrity.
        # To avoid division by zero, we use max(epsilon, integrity_score).
        epsilon = 1e-6
        safe_integrity = max(epsilon, integrity_score)
        potential = 1.0 / safe_integrity

        # Adjust potential to be 1 at integrity=1.0 for normalized view, or keep as is.
        # If integrity=1.0, potential=1.0. If integrity=0.01, potential=100.0.

        total = kinetic + potential

        # Friction coefficient might depend on how "hard" it is to move.
        # Higher potential (lower integrity) implies higher friction.
        friction = potential * 0.1

        is_mutiny = False
        # Thresholds are defined in MutinyDetector, but Hamiltonian creates the state.
        # We can set is_mutiny here if we want the physics engine to flag it too,
        # but usually detection is a separate layer.
        # However, the EnergyState dataclass has an is_mutiny field.
        # Let's populate it if total energy is extremely high.
        # Using a hardcoded threshold here just to fill the field, though MutinyDetector has the canonical thresholds.
        if total > 5000:
             is_mutiny = True

        return EnergyState(
            kinetic=kinetic,
            potential=potential,
            total=total,
            friction_coefficient=friction,
            is_mutiny=is_mutiny
        )
