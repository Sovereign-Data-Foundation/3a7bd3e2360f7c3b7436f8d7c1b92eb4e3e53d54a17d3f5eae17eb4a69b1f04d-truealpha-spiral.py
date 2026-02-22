
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

    def test_invariant_resilience(self):
        """
        Resilience Condition: The 'if/else' (LBYL) pattern must be significantly faster
        than exception handling (EAFP) for invalid inputs (attacks).

        This enforces 'Refusal at the Transition Level' - rejecting invalid inputs
        cheaply without invoking the exception machinery.
        """
        # Prepare inputs
        valid_category = "Emergent"
        invalid_category = "AttackPayload"

        # 1. Measure Current Implementation (LBYL expected)
        # We need to test the actual method to verify the implementation choice.

        # Define attack scenario
        def attack_scenario():
            try:
                self.pilot.admit_patient(invalid_category)
            except ValueError:
                pass

        # Define baseline (EAFP overhead simulation)
        # Raising an exception is expensive. We want to ensure we are NOT paying this cost
        # inside the method before the ValueError is raised?
        # Actually, if we use LBYL, we raise ValueError manually.
        # If we use EAFP (try/except KeyError), we raise ValueError manually in the except block.
        # Wait, both raise ValueError.
        # So both have exception overhead *if* they raise.
        # The difference is:
        # EAFP: try -> KeyError (internal exc) -> catch -> raise ValueError (external exc). Double exception.
        # LBYL: if -> check -> raise ValueError (external exc). Single exception.

        # Let's measure the cost of admit_patient directly.

        # Warmup
        for _ in range(1000): attack_scenario()

        # Measurement
        number = 10000
        time_attack = timeit.timeit(attack_scenario, number=number)

        # 10k attacks should be fast.
        # On EAFP: ~0.005s (very rough guess, exception is ~1us)
        # On LBYL: ~0.002s

        print(f"\n[Sentient Lock] Attack Resilience (10k ops): {time_attack:.4f}s")

        # Assert that we are strictly faster than the double-exception EAFP pattern.
        # We can simulate EAFP cost to compare.
        def eafp_simulation():
            try:
                try:
                    self.pilot.current_counts[invalid_category] += 1
                except KeyError:
                    raise ValueError(f"Invalid category: {invalid_category}")
            except ValueError:
                pass

        time_eafp = timeit.timeit(eafp_simulation, number=number)
        print(f"[Sentient Lock] EAFP Simulation (10k ops): {time_eafp:.4f}s")

        ratio = time_attack / time_eafp
        print(f"[Sentient Lock] Attack/EAFP Ratio: {ratio:.4f} (Lower is better)")

        # If we are using LBYL, ratio should be < 0.8 (significant speedup).
        # If we are using EAFP, ratio will be ~1.0.
        # We assert ratio < 0.9 to enforce LBYL.
        self.assertLess(ratio, 0.9, "System is negotiating with exceptions! Enforce LBYL for resilience.")

if __name__ == '__main__':
    unittest.main()
