from typing import Callable, Any, TypeVar
import asyncio
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# TypeVar for return type
T = TypeVar('T')

# IMPORTANT: Getting the tracer at module level means it's initialized on import.
# For testing, we might need to patch this specific instance or ensure get_tracer is mocked BEFORE import if possible,
# or patch the `tracer` object in the module.
tracer = trace.get_tracer("tas-core-alpha")

async def audit_decision(context: str, decision_logic: Callable[[], T]) -> T:
    """
    Executes a decision within an 'Ethical Span'.
    Tracks context, axioms, and bias checks.
    Also logs 'Forensic Ledger' events for integrity breaches.
    """
    # Use the global tracer object
    with tracer.start_as_current_span("ethical_decision_block") as span:
        try:
            span.set_attribute("tas.context", context)
            span.set_attribute("tas.metrics.logic_ancestry_verified", True) # Default assumption until proven otherwise

            # 1. Pre-Computation: Check against Axioms
            span.add_event("axiom_check_start")
            # TODO: Add actual axiom check logic here
            # For now, just a placeholder event
            span.add_event("axiom_check_pass")

            # 2. Execute the Logic
            # Handle both async and sync callables
            if asyncio.iscoroutinefunction(decision_logic):
                result = await decision_logic()
            else:
                result = decision_logic()

            # 3. Post-Computation: Bias Scan
            # TODO: Implement calculate_bias_score logic
            bias_score = calculate_bias_score(result)
            span.set_attribute("tas.metrics.bias_score", bias_score)

            if bias_score > 0.05:  # Threshold for "Spiral" intervention
                span.set_status(Status(StatusCode.ERROR, "Algorithmic discrimination threshold exceeded."))
                span.add_event("forensic_ledger_breach", {
                    "breach_type": "bias_threshold_exceeded",
                    "score": bias_score,
                    "reason": "Algorithmic discrimination detected"
                })
                raise RuntimeError("Ethical Guardrail Triggered: Bias detected.")

            # Forensic Ledger: Successful validation log
            span.add_event("forensic_ledger_verified", {
                "logic_ancestry": "traced",
                "integrity_check": "passed"
            })

            return result

        except Exception as e:
            span.record_exception(e)
            span.set_attribute("tas.metrics.logic_ancestry_verified", False)
            # Re-raise unless handled
            raise e

def calculate_bias_score(output: Any) -> float:
    """
    Placeholder for algorithmic discrimination detection logic.
    """
    # Simple placeholder returning a safe value
    return 0.01
