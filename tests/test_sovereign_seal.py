
import unittest
from tas_core.alpha.sovereign import SovereignRuntime

class TestSovereignSeal(unittest.TestCase):
    def tearDown(self):
        # Reset the sealed state to avoid side effects on other tests
        if hasattr(SovereignRuntime, '_is_sealed'):
            del SovereignRuntime._is_sealed

    def test_seal_runtime(self):
        """
        Test that seal_runtime() sets the sealed state.
        """
        self.assertFalse(hasattr(SovereignRuntime, '_is_sealed'))

        result = SovereignRuntime.seal_runtime()
        self.assertIn("SovereignRuntime sealed", result)
        self.assertTrue(SovereignRuntime._is_sealed)

        # Test double seal
        result2 = SovereignRuntime.seal_runtime()
        self.assertIn("already sealed", result2)

if __name__ == '__main__':
    unittest.main()
