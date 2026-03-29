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

        self.assertAlmostEqual(drift, 0.1, msg=f"Expected drift 0.1 (TVD), but got {drift}")

    def test_admit_patient_valid(self):
        # Test valid admission
        self.pilot.admit_patient('Emergent')
        self.assertEqual(self.pilot.total_patients, 1)
        self.assertEqual(self.pilot.current_counts['Emergent'], 1)
        self.assertEqual(self.pilot.history, ['Emergent'])

    def test_admit_patient_invalid(self):
        # Test invalid admission raises ValueError and preserves state
        initial_total = self.pilot.total_patients
        initial_history_len = len(self.pilot.history)

        with self.assertRaises(ValueError):
            self.pilot.admit_patient('InvalidCategory')

        self.assertEqual(self.pilot.total_patients, initial_total)
        self.assertEqual(len(self.pilot.history), initial_history_len)
        # Ensure 'InvalidCategory' is not in counts
        self.assertNotIn('InvalidCategory', self.pilot.current_counts)


    def test_get_current_distribution_zero_patients(self):
        # When total_patients is 0, it should return baseline keys initialized to 0
        dist = self.pilot.get_current_distribution()
        expected = {'Emergent': 0, 'Urgent': 0, 'Non-Urgent': 0}
        self.assertEqual(dist, expected)

    def test_get_current_distribution_with_patients(self):
        # Add some patients and verify correct distribution calculation
        self.pilot.admit_patient('Emergent')
        self.pilot.admit_patient('Emergent')
        self.pilot.admit_patient('Urgent')

        dist = self.pilot.get_current_distribution()

        # total 3 patients: 2 Emergent, 1 Urgent, 0 Non-Urgent
        expected = {
            'Emergent': 2.0 / 3.0,
            'Urgent': 1.0 / 3.0,
            'Non-Urgent': 0.0
        }

        # We use assertAlmostEqual for float comparison within dicts manually
        for k in expected:
            self.assertAlmostEqual(dist[k], expected[k])

if __name__ == '__main__':
    unittest.main()
