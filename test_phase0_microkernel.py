import unittest

from tas_phase0_microkernel import (
    boot_microkernel,
    default_manifest,
    Phase0Manifest,
    BOOT_STATUS,
    REFUSAL_STATUS,
)


class TestPhase0MicroKernel(unittest.TestCase):
    def test_boot_success(self):
        receipt = boot_microkernel(default_manifest())
        self.assertEqual(receipt["status"], BOOT_STATUS)
        self.assertIn("anchor_hash", receipt)

    def test_refusal_on_low_coherence(self):
        bad = Phase0Manifest(
            phase="PHASE_0_MICRO_KERNEL_BOOT",
            steward="Russell",
            invariant="No attestation -> no execution",
            coherence=0.5,
        )
        receipt = boot_microkernel(bad)
        self.assertEqual(receipt["status"], REFUSAL_STATUS)

    def test_refusal_on_missing_invariant(self):
        bad = Phase0Manifest(
            phase="PHASE_0_MICRO_KERNEL_BOOT",
            steward="Russell",
            invariant="",
            coherence=1.0,
        )
        receipt = boot_microkernel(bad)
        self.assertEqual(receipt["status"], REFUSAL_STATUS)


if __name__ == "__main__":
    unittest.main()
