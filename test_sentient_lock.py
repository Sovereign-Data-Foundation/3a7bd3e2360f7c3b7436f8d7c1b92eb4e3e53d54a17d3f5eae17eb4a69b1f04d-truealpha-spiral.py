
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
        # Access private attribute as strict structure is now enforced
        self.assertNotIsInstance(self.pilot._current_counts, collections.defaultdict,
                                 "Regression: Optimization lost! _current_counts should be a standard dict.")

        # Ensure keys are pre-initialized
        self.assertEqual(len(self.pilot._current_counts), 3)
        self.assertEqual(self.pilot._current_counts['Emergent'], 0)

    def test_admit_patient_new_baseline_key_does_not_keyerror(self):
        """
        Regression Test: "Baseline Mutation Edge Case"
        Ensures that if baseline evolves (mutates) without syncing current_counts,
        admit_patient rejects the input safely instead of crashing with KeyError.
        """
        pilot = ERTriagePilot()
        # Simulate baseline evolving after __init__
        # NOTE: We must use the private attribute because .baseline is now read-only (structurally enforced!)
        pilot._baseline["NewCat"] = 0.0

        # Precondition: key is in baseline but NOT in counts (dangerous state)
        self.assertIn("NewCat", pilot.baseline)
        self.assertNotIn("NewCat", pilot.current_counts)

        # Expected behavior: Reject safely (ValueError) because storage isn't ready.
        # It must NOT raise KeyError.
        try:
            pilot.admit_patient("NewCat")
        except ValueError as e:
            self.assertIn("Invalid category", str(e))
        except KeyError:
            self.fail("FAILED: admit_patient raised KeyError! The Sentient Lock is broken.")

if __name__ == '__main__':
    unittest.main()
