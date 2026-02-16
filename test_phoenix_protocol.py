import unittest
from tas_dna_pilot import ERTriagePilot

class TestPhoenixProtocol(unittest.TestCase):
    def setUp(self):
        self.pilot = ERTriagePilot()

    def test_admit_and_attest(self):
        """Test that admit_patient adds to history and check_integrity attests it."""
        self.pilot.admit_patient('Emergent')
        self.assertEqual(len(self.pilot.history), 1)
        self.assertEqual(self.pilot.history[-1], 'Emergent')

        # Use a high threshold to ensure integrity check passes and attests the state
        self.assertTrue(self.pilot.check_integrity(threshold=1.0))
        self.assertEqual(self.pilot.attested_history_length, 1)

    def test_revert_to_initial_state(self):
        """Test reverting to initial state if no attestation happened."""
        # Add patients that cause drift
        self.pilot.admit_patient('Urgent')
        self.pilot.admit_patient('Urgent')

        # Manually trigger phoenix protocol
        self.pilot.phoenix_protocol()

        # Should be empty
        self.assertEqual(self.pilot.total_patients, 0)
        self.assertEqual(len(self.pilot.history), 0)
        # Use property access
        self.assertEqual(self.pilot.current_counts['Urgent'], 0)

    def test_revert_to_attested_state(self):
        """Test reverting to a specifically attested state."""
        # 1. Reach a valid state (attested)
        # We need to craft a state with low drift.
        # 3 Emergent, 5 Urgent, 2 Non-Urgent = 10 total. Exact baseline.
        for _ in range(3): self.pilot.admit_patient('Emergent')
        for _ in range(5): self.pilot.admit_patient('Urgent')
        for _ in range(2): self.pilot.admit_patient('Non-Urgent')

        self.assertTrue(self.pilot.check_integrity())
        # After this, attested_history_length should be 10.

        # 2. Add patients that cause drift
        # Add 10 'Non-Urgent' patients
        for _ in range(10):
            self.pilot.admit_patient('Non-Urgent')

        self.assertEqual(self.pilot.total_patients, 20)

        # 3. Trigger Phoenix Protocol
        self.pilot.phoenix_protocol()

        # 4. Check if reverted to attested state (10 patients)
        self.assertEqual(self.pilot.total_patients, 10)
        self.assertEqual(self.pilot.current_counts['Non-Urgent'], 2)
        # History length should be 10
        self.assertEqual(len(self.pilot.history), 10)

    def test_delta_storage(self):
        """Verify that history stores categories (delta) not snapshots."""
        # This test is specific to the implementation detail requested.
        self.pilot.admit_patient('Emergent')
        # Check the last item in history
        last_item = self.pilot.history[-1]
        self.assertEqual(last_item, 'Emergent')

if __name__ == '__main__':
    unittest.main()
