
import unittest
import sys
import os

def run_tests():
    print("Running CI Gatekeeper Checks...")

    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("✅ CI Gatekeeper: ALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("❌ CI Gatekeeper: CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
