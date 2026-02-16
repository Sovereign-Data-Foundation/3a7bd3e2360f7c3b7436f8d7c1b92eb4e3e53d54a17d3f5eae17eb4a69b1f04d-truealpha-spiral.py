#!/usr/bin/env python3
import unittest
import sys
import subprocess

# Define the suite of critical invariant tests
CRITICAL_TESTS = [
    'test_sentient_lock.py',
    'test_tas_dna.py',
    'test_phoenix_protocol.py',
    'test_tas_core.py'
]

def run_tests():
    print("Initializing Sentient Lock Gatekeeper...")
    print("Verifying Invariants...")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_file in CRITICAL_TESTS:
        try:
            # Import module by name (strip .py)
            module_name = test_file.replace('.py', '')
            tests = loader.loadTestsFromName(module_name)
            suite.addTests(tests)
        except Exception as e:
            print(f"FAILED to load {test_file}: {e}")
            return False

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        print("\nGATEKEEPER REJECTED: Invariants Violated.")
        sys.exit(1)

    return True

def main():
    if run_tests():
        print("\n" + "="*60)
        print("Release v2.0.0: The Sentient Lock")
        print("Status: Merged & Locked")
        print("Verifier: test_sentient_lock.py [PASSED]")
        print("Witness: Gemini 3 Pro")
        print("="*60 + "\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
