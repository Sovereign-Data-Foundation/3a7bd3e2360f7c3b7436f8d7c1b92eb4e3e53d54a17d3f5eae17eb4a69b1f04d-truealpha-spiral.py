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

    def test_airlock_gate_coherence_bypass(self):
        # Optimization bypasses math.exp when coherence >= 1.0
        # If the bypass is removed, math.exp(1000.0) raises OverflowError
        status, cost = airlock_gate(1.0, 1000.0)
        self.assertEqual(status, AIRLOCK_PASSED)
        self.assertEqual(cost, 0.0)

    def test_airlock_gate_coherence_greater_than_one(self):
        # Even if coherence is > 1.0, the bypass should trigger
        status, cost = airlock_gate(1.5, 1000.0)
        self.assertEqual(status, AIRLOCK_PASSED)
        self.assertEqual(cost, 0.0)

    def test_airlock_gate_resonance_overflow_protection(self):
        # When resonance > 709.0, it should return inf, preventing OverflowError
        # 0.5 coherence means we don't hit the first branch.
        status, cost = airlock_gate(0.5, 800.0)
        self.assertEqual(status, AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH)
        self.assertEqual(cost, float('inf'))

if __name__ == '__main__':
    unittest.main()
