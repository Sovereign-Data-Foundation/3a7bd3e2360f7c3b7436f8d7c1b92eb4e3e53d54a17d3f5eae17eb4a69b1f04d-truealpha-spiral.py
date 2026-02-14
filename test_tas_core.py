
import unittest
import asyncio
from unittest.mock import Mock, patch

# Need to patch BEFORE importing the module if we want to catch the module-level get_tracer call?
# Or patch the `tracer` object IN the module.

import tas_core.ethics.auditor

class TestAuditor(unittest.TestCase):
    def setUp(self):
        # Patch the module-level tracer object directly
        self.tracer_patch = patch('tas_core.ethics.auditor.tracer')
        self.mock_tracer = self.tracer_patch.start()

        # Setup span context
        self.mock_span = Mock()
        self.mock_tracer.start_as_current_span.return_value.__enter__.return_value = self.mock_span

    def tearDown(self):
        self.tracer_patch.stop()

    def test_calculate_bias_score(self):
        self.assertEqual(tas_core.ethics.auditor.calculate_bias_score("test"), 0.01)

    def test_audit_decision_success(self):
        async def mock_logic():
            return "Decision Approved"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(tas_core.ethics.auditor.audit_decision("test_context", mock_logic))
            self.assertEqual(result, "Decision Approved")

            # Check interaction with the mock span
            self.mock_span.set_attribute.assert_any_call("tas.context", "test_context")
            self.mock_span.add_event.assert_any_call("axiom_check_start")
            self.mock_span.set_attribute.assert_any_call("tas.metrics.bias_score", 0.01)
        finally:
            loop.close()

    def test_audit_decision_bias_fail(self):
        # Override calculate_bias_score locally for this test
        with patch('tas_core.ethics.auditor.calculate_bias_score', return_value=0.1):
             async def mock_logic():
                 return "Biased Content"

             loop = asyncio.new_event_loop()
             asyncio.set_event_loop(loop)

             try:
                 with self.assertRaises(RuntimeError) as cm:
                     loop.run_until_complete(tas_core.ethics.auditor.audit_decision("test_fail", mock_logic))

                 self.assertIn("Guardrail Triggered", str(cm.exception))
             finally:
                 loop.close()

if __name__ == '__main__':
    unittest.main()
