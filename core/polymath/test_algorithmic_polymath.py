import unittest
from core.polymath.algorithmic_polymath import AlgorithmicPolymath, Discipline
from core.physics.tasw_hamiltonian import EnergyState

class TestAlgorithmicPolymath(unittest.TestCase):
    def setUp(self):
        self.disciplines = [
            Discipline(
                name="Physics",
                compute_function=lambda x: {"velocity": 10.0, "score": 1.0},
                weight=1.0
            ),
            Discipline(
                name="Ethics",
                compute_function=lambda x: {"velocity": 0.0, "score": 0.5},
                weight=1.0
            )
        ]
        self.polymath = AlgorithmicPolymath(self.disciplines)

    def test_initialization(self):
        self.assertEqual(len(self.polymath.disciplines), 2)
        self.assertEqual(self.polymath.integrity_threshold, 0.8)

    def test_compute_multidisciplinary_output(self):
        input_data = {"test_val": 0.5}
        result = self.polymath.compute_multidisciplinary_output(input_data)

        # Check structure
        self.assertIn("decision", result)
        self.assertIn("aggregate_output", result)
        self.assertIn("energy_state", result)

        # Check velocity averaging
        # Physics velocity 10, Ethics velocity 0. Mean = 5.
        # Energy calculation uses mean velocity.
        energy_state = result["energy_state"]
        # Kinetic = 0.5 * v^2 = 0.5 * 25 = 12.5
        self.assertAlmostEqual(energy_state.kinetic, 12.5)

        # Check integrity assessment (mock)
        # Input has 0.5. assess_integrity returns 0.5.
        # Potential = 1 / 0.5 = 2.0
        self.assertAlmostEqual(energy_state.potential, 2.0)

        # Total = 14.5. This is low, so NOMINAL.
        self.assertFalse(result["decision"].is_mutiny)

    def test_adaptation(self):
        initial_weights = [d.weight for d in self.polymath.disciplines]
        self.assertEqual(initial_weights, [1.0, 1.0]) # Actually they get normalized to 0.5 if we ran logic, but here initiated as 1.0

        # Manually normalize first to match what adapt does internally?
        # No, adapt normalizes at the end.

        # Simulate success
        self.polymath.adapt({"success": True})

        # Both started at 1.0. Both get * 1.1 = 1.1.
        # Then normalized: 1.1 / 2.2 = 0.5.

        # Let's skew it
        self.polymath.disciplines[0].weight = 2.0
        self.polymath.disciplines[1].weight = 1.0
        # Physics 2.0, Ethics 1.0

        # Simulate failure
        self.polymath.adapt({"success": False})
        # Physics: 2.0 * 0.9 = 1.8
        # Ethics: 1.0 * 0.9 = 0.9
        # Total: 2.7
        # Physics Norm: 1.8 / 2.7 = 0.666
        # Ethics Norm: 0.9 / 2.7 = 0.333

        self.assertAlmostEqual(self.polymath.disciplines[0].weight, 0.66666666)
        self.assertAlmostEqual(self.polymath.disciplines[1].weight, 0.33333333)

    def test_input_resilience(self):
        # Test with string inputs which should be ignored by mock integrity check
        input_data = {"action": "test", "target": "system"}
        result = self.polymath.compute_multidisciplinary_output(input_data)

        # Mock returns 0.9 if no numerics
        # Kinetic based on mean velocity.
        # Physics returns 10.0, Ethics returns 0.0. Mean 5.0. Kinetic 12.5.
        # Potential = 1 / 0.9 = 1.111
        # Total ~ 13.61

        self.assertFalse(result["decision"].is_mutiny)

if __name__ == '__main__':
    unittest.main()
