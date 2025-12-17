import unittest
from uvk.v0_1.code_verification_kernel import CodeVerificationKernel, CodeArtifact

class TestCodeVerificationKernel(unittest.TestCase):
    def setUp(self):
        self.kernel = CodeVerificationKernel()

        # Valid artifact
        self.valid_artifact = CodeArtifact(
            source_code="fn main() { println!(\"Hello\"); }",
            spec="This code is proven to print Hello",
            build_script="cargo build",
            test_suite="cargo test",
            commit_history=[{"message": "Initial commit"}, {"message": "Add spec"}],
            required_checks=["Compilation", "FormalVerification"]
        )

        # Unsafe artifact (Static analysis fail)
        self.unsafe_artifact = CodeArtifact(
            source_code="fn main() { unsafe { ... } }",
            spec="Proven",
            build_script="build",
            test_suite="test",
            commit_history=[],
            required_checks=["Compilation"]
        )

        # Unverified artifact (Formal spec fail)
        self.unverified_artifact = CodeArtifact(
            source_code="fn main() {}",
            spec="Draft spec", # Does not contain "proven"
            build_script="build",
            test_suite="test",
            commit_history=[],
            required_checks=["Compilation"]
        )

    def test_verify_valid_artifact(self):
        result = self.kernel.verify(self.valid_artifact)
        self.assertEqual(result.status, "VERIFIED")
        self.assertIsNotNone(result.ics)
        self.assertEqual(result.winding_I, 0.0)
        # q2: 5 passed checks / 2 required = 2.5 > 1.0
        self.assertGreater(result.q2, 1.0)
        self.assertEqual(result.gradH, 0.0)

    def test_verify_unsafe_artifact(self):
        result = self.kernel.verify(self.unsafe_artifact)
        self.assertEqual(result.status, "REJECTED")
        self.assertIsNone(result.ics)
        self.assertNotEqual(result.winding_I, 0.0) # Should have winding due to failure
        self.assertIn("StaticAnalysis", str(result.obligations_summary) + str(result))

    def test_verify_unproven_artifact(self):
        result = self.kernel.verify(self.unverified_artifact)
        self.assertEqual(result.status, "REJECTED")
        self.assertNotEqual(result.winding_I, 0.0)

    def test_gradH_calculation(self):
        artifact = CodeArtifact(
            source_code="ok", spec="proven", build_script="", test_suite="",
            commit_history=[
                {"message": "Fix bug"},
                {"message": "Add unsafe optimization"}, # Contains unsafe
                {"message": "Refactor"}
            ],
            required_checks=["Compilation"]
        )
        # We manually test the metric calculation via verify or accessing the kernel helper if exposed
        # The kernel calculates gradH internally.
        result = self.kernel.verify(artifact)
        # 1 unsafe / 3 total = 0.333
        self.assertAlmostEqual(result.gradH, 1/3)

if __name__ == '__main__':
    unittest.main()
