import unittest
from tas_dna_pilot import ERTriagePilot

class TestERTriagePilot(unittest.TestCase):
    def setUp(self):
        self.pilot = ERTriagePilot()

    def test_calculate_drift_exact_baseline(self):
        # Manually set counts to match baseline exactly (10 patients)
        # Emergent: 3, Urgent: 5, Non-Urgent: 2
        self.pilot.current_counts['Emergent'] = 3
        self.pilot.current_counts['Urgent'] = 5
        self.pilot.current_counts['Non-Urgent'] = 2
        self.pilot.total_patients = 10

        drift = self.pilot.calculate_drift()
        self.assertAlmostEqual(drift, 0.0)

    def test_calculate_drift_known_deviation(self):
        # Scenario:
        # Baseline: E=0.3, U=0.5, N=0.2
        # Current:  E=0.4, U=0.4, N=0.2
        # Difference:
        #   E: |0.4 - 0.3| = 0.1
        #   U: |0.4 - 0.5| = 0.1
        #   N: |0.2 - 0.2| = 0.0
        # Sum of abs diffs (L1) = 0.2
        # TVD = 0.5 * 0.2 = 0.1

        self.pilot.current_counts['Emergent'] = 4
        self.pilot.current_counts['Urgent'] = 4
        self.pilot.current_counts['Non-Urgent'] = 2
        self.pilot.total_patients = 10

        drift = self.pilot.calculate_drift()

        # This assertion should fail with current buggy implementation (which returns 0.2)
        self.assertAlmostEqual(drift, 0.1, msg=f"Expected drift 0.1 (TVD), but got {drift}")

if __name__ == '__main__':
    unittest.main()
