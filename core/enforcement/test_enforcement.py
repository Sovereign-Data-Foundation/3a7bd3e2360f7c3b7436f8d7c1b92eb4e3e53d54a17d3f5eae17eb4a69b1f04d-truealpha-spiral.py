import unittest
from core.enforcement.rirp import RIRP, SecurityException
from core.enforcement.phoenix import PhoenixProtocol

class TestEnforcement(unittest.TestCase):

    # --- RIRP Tests ---
    def test_rirp_valid_provenance(self):
        input_data = {"data": "test", "h0_signature": "valid_sig_123"}
        self.assertTrue(RIRP.validate_provenance(input_data))
        # Should not raise exception
        try:
            RIRP.enforce(input_data)
        except SecurityException:
            self.fail("RIRP.enforce raised SecurityException on valid input")

    def test_rirp_missing_provenance(self):
        input_data = {"data": "test"} # No signature
        self.assertFalse(RIRP.validate_provenance(input_data))
        with self.assertRaises(SecurityException) as cm:
            RIRP.enforce(input_data)
        self.assertIn("Missing $H_0$ signature", str(cm.exception))

    def test_rirp_empty_provenance(self):
        input_data = {"data": "test", "h0_signature": ""} # Empty
        self.assertFalse(RIRP.validate_provenance(input_data))
        with self.assertRaises(SecurityException):
            RIRP.enforce(input_data)

    # --- Phoenix Protocol Tests ---
    def test_phoenix_rollback(self):
        history = [
            {"timestamp": 1, "state": "good"},
            {"timestamp": 2, "state": "bad_mutiny"}
        ]
        restored = PhoenixProtocol.initiate_rollback(history)

        # Should have popped the last one and returned the one before it
        self.assertEqual(len(history), 1)
        self.assertEqual(restored["timestamp"], 1)
        self.assertEqual(restored["state"], "good")

    def test_phoenix_rollback_empty(self):
        history = []
        restored = PhoenixProtocol.initiate_rollback(history)
        self.assertIsNone(restored)

    def test_phoenix_rollback_single_item(self):
        history = [{"timestamp": 1, "state": "bad_mutiny"}]
        restored = PhoenixProtocol.initiate_rollback(history)
        # Should be empty now
        self.assertEqual(len(history), 0)
        # Should return None as there is no previous state
        self.assertIsNone(restored)

if __name__ == '__main__':
    unittest.main()
