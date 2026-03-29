import unittest
import math
from tas_core.alpha.airlock import airlock_gate, AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH, AIRLOCK_PASSED

class TestAirlock(unittest.TestCase):
    def test_airlock_gate_passed(self):
        status, cost = airlock_gate(1.0, 1.0)
        self.assertEqual(status, AIRLOCK_PASSED)
        self.assertEqual(cost, 0.0)

    def test_airlock_gate_denied(self):
        status, cost = airlock_gate(0.0, 2.0)
        self.assertEqual(status, AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH)
        self.assertGreater(cost, 5.0)

    def test_airlock_gate_high_resonance(self):
        # Test boundary condition for resonance > 709.0 (math.exp limit)
        status, cost = airlock_gate(0.5, 710.0)
        self.assertEqual(status, AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH)
        self.assertEqual(cost, float('inf'))

if __name__ == '__main__':
    unittest.main()
