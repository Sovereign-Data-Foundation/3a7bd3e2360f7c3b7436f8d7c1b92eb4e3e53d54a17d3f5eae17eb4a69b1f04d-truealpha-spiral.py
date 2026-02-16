
import unittest
from tas_dna_pilot import ERTriagePilot

class TestSentientLock(unittest.TestCase):
    """
    Enforces the 'Sentient Lock' invariant:
    Optimization (Direct Dict Access) + Safety (Strict Validation) = True.
    """

    def setUp(self):
        self.pilot = ERTriagePilot()

    def test_invariant_validation_before_access(self):
        """
        The Lock: Attempting to admit an invalid patient MUST raise ValueError
        (Validation Layer), preventing a raw KeyError (Optimization Layer).
        """
        invalid_category = "Ghost_in_the_Machine"

        # 1. Ensure the invalid category is NOT in the baseline (precondition)
        self.assertNotIn(invalid_category, self.pilot.baseline)

        # 2. Attempt admission
        with self.assertRaises(ValueError) as cm:
            self.pilot.admit_patient(invalid_category)

        # 3. Verify the error message confirms strict validation
        self.assertIn("Invalid category", str(cm.exception))

    def test_optimization_structure(self):
        """
        Verify that the optimization (dict instead of defaultdict) is actually present.
        If someone reverts to defaultdict without realizing, this test warns them
        that the performance contract is broken.
        """
        # Ensure it's a standard dict, not a defaultdict
        import collections
        self.assertNotIsInstance(self.pilot.current_counts, collections.defaultdict,
                                 "Regression: Optimization lost! current_counts should be a standard dict.")

        # Ensure keys are pre-initialized
        self.assertEqual(len(self.pilot.current_counts), 3)
        self.assertEqual(self.pilot.current_counts['Emergent'], 0)

if __name__ == '__main__':
    unittest.main()
