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
        input_data = {"test_val": 0.5, "h0_signature": "mock_sig"}
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
        input_data = {"action": "test", "target": "system", "h0_signature": "mock_sig"}
        result = self.polymath.compute_multidisciplinary_output(input_data)

        # Mock returns 0.9 if no numerics
        # Kinetic based on mean velocity.
        # Physics returns 10.0, Ethics returns 0.0. Mean 5.0. Kinetic 12.5.
        # Potential = 1 / 0.9 = 1.111
        # Total ~ 13.61

        self.assertFalse(result["decision"].is_mutiny)

    def test_rirp_blocking(self):
        # Input without signature
        input_data = {"test_val": 0.5}
        result = self.polymath.compute_multidisciplinary_output(input_data)

        self.assertTrue(result.get("blocked"))
        self.assertIn("RIRP BLOCK", result.get("error"))

    def test_phoenix_trigger(self):
        # Setup conditions for Mutiny: High velocity (kinetic energy)
        # Physics discipline returns high velocity
        self.polymath.disciplines[0].compute_function = lambda x: {"velocity": 200.0, "score": 1.0}

        # Previous valid state
        # NOTE: With high velocity from Physics discipline, even this might trigger mutiny if thresholds are low?
        # But we default init thresholds: MutinyDetector(friction=1000, mutiny=5000)
        # 200.0 velocity -> Kinetic = 0.5 * 200^2 = 0.5 * 40000 = 20000.
        # This is > 5000. So the FIRST input will also trigger mutiny.
        # We need to lower velocity for the first call.

        self.polymath.disciplines[0].compute_function = lambda x: {"velocity": 10.0, "score": 1.0} # Low velocity
        valid_input = {"test_val": 0.1, "h0_signature": "sig1"}
        self.polymath.compute_multidisciplinary_output(valid_input)
        self.assertEqual(len(self.polymath.state_history), 1)

        # Mutiny-inducing input
        self.polymath.disciplines[0].compute_function = lambda x: {"velocity": 200.0, "score": 1.0} # High velocity
        mutiny_input = {"test_val": 0.1, "h0_signature": "sig2"}
        result = self.polymath.compute_multidisciplinary_output(mutiny_input)

        self.assertTrue(result.get("phoenix_triggered"))
        self.assertTrue(result["decision"].is_mutiny)

        # History should have been pruned of the mutiny state, leaving only the first one
        # Wait - PhoenixProtocol.initiate_rollback pops the *current* state.
        # But in compute_multidisciplinary_output, we append the state BEFORE checking Mutiny.
        # So we append the bad state (size 2). Then detect Mutiny. Then rollback.
        # Rollback pops the bad state (size 1). And returns the previous state (which is at index 0).
        self.assertEqual(len(self.polymath.state_history), 1)

        # And the returned restored state should match the first one
        self.assertEqual(result["restored_state"]["input"]["h0_signature"], "sig1")

if __name__ == '__main__':
    unittest.main()
