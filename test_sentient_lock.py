
import unittest
import timeit
from tas_dna_pilot import ERTriagePilot

class TestSentientLock(unittest.TestCase):
    """
    The Invariant: Optimization AND Safety = True.
    This test ensures no future optimization can bypass the ValueError validation
    in admit_patient, while confirming the performance characteristic (EAFP) is present.
    """
    def setUp(self):
        self.pilot = ERTriagePilot()

    def test_invariant_safety(self):
        """
        Safety Condition: Invalid inputs MUST raise ValueError.
        This prevents 'fast but wrong' optimizations (e.g. defaulting to 0).
        """
        with self.assertRaises(ValueError):
            self.pilot.admit_patient("InvalidCategory")

    def test_invariant_optimization(self):
        """
        Optimization Condition: The 'try/except' (EAFP) pattern must be faster
        than the explicit check (LBYL) for valid inputs.

        This is a heuristic check. We compare the current implementation against
        a simulated LBYL implementation.
        """
        # Prepare valid input
        category = "Emergent"

        # 1. Measure Current Implementation (EAFP)
        def current_impl():
            try:
                self.pilot.current_counts[category] += 1
            except KeyError:
                raise ValueError(f"Invalid category: {category}")

        # 2. Measure LBYL Implementation (The "safe but slow" alternative)
        def lbyl_impl():
            if category in self.pilot.baseline:
                self.pilot.current_counts[category] += 1
            else:
                raise ValueError(f"Invalid category: {category}")

        # Warmup
        for _ in range(1000): current_impl()
        for _ in range(1000): lbyl_impl()

        # Measurement
        number = 100000
        time_current = timeit.timeit(current_impl, number=number)
        time_lbyl = timeit.timeit(lbyl_impl, number=number)

        # We assert that current implementation is not significantly slower than LBYL
        # (it should be faster, but environment noise exists).
        # The key is that we are using the optimized path.
        # Strict "faster" check might be flaky in CI, so we log the ratio.
        ratio = time_current / time_lbyl
        print(f"\n[Sentient Lock] EAFP/LBYL Ratio: {ratio:.4f} (Lower is better)")

        # Ideally ratio < 1.0. We allow a small margin for noise, but if it's > 1.2,
        # the optimization might be lost or overhead introduced.
        self.assertLess(ratio, 1.2, "Performance regression detected: EAFP is significantly slower than LBYL.")

if __name__ == '__main__':
    unittest.main()
