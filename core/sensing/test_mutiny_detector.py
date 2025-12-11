import unittest
from core.physics.tasw_hamiltonian import EnergyState
from core.sensing.mutiny_detector import MutinyDetector

class TestMutinyDetector(unittest.TestCase):
    def setUp(self):
        self.detector = MutinyDetector(friction_threshold=1000.0, mutiny_threshold=5000.0)

    def test_nominal_state(self):
        state = EnergyState(
            kinetic=100.0,
            potential=100.0,
            total=200.0,
            friction_coefficient=0.1,
            is_mutiny=False
        )
        event = self.detector.assess_state(state)
        self.assertFalse(event.is_mutiny)
        self.assertEqual(event.severity, "NOMINAL")
        self.assertIn("OK", event.trigger_message)

    def test_friction_state(self):
        state = EnergyState(
            kinetic=1000.0,
            potential=1000.0,
            total=2000.0,
            friction_coefficient=0.5,
            is_mutiny=False
        )
        event = self.detector.assess_state(state)
        self.assertFalse(event.is_mutiny)
        self.assertEqual(event.severity, "FRICTION")
        self.assertIn("WARNING", event.trigger_message)

    def test_mutiny_state(self):
        state = EnergyState(
            kinetic=3000.0,
            potential=3000.0,
            total=6000.0,
            friction_coefficient=0.9,
            is_mutiny=True
        )
        event = self.detector.assess_state(state)
        self.assertTrue(event.is_mutiny)
        self.assertEqual(event.severity, "MUTINY")
        self.assertIn("CRITICAL", event.trigger_message)

if __name__ == '__main__':
    unittest.main()
