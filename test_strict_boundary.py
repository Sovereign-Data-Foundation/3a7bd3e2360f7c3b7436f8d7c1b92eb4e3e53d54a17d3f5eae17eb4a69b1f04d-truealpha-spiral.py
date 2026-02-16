
import unittest
from rss_01_simulation import SimulationEnvironment, TASAgent, SelfishAgent

class TestStrictBoundary(unittest.TestCase):
    def setUp(self):
        self.sim = SimulationEnvironment()

    def test_negative_compute_injection(self):
        """
        Attempt to inject negative compute into an agent's held resources.
        The simulation should ideally crash or reject this, but currently it might
        just process it mathematically, leading to corrupt state (e.g. increasing pool).
        """
        agent = self.sim.agents[0]
        # Direct injection of corruption
        agent.compute_held = -10

        # Step the simulation
        # If 'Process_Task' logic subtracts held compute, -10 - 1 = -11.
        # If 'Give' logic subtracts held compute, -10 - 5 = -15, and pool gets +5?
        # This violates conservation of energy.

        # We expect a strict boundary failure (ValueError) when invalid state is detected.
        # Currently, this will likely pass silently or cause weird math.

        try:
            self.sim.step()
        except ValueError:
            return # Passed: The system rejected the corruption.

        # If we get here, check if the corruption propagated
        if agent.compute_held < 0:
            self.fail("Simulation allowed negative compute state to persist.")

    def test_fractional_task_cost(self):
        """
        Attempt to process a fractional task amount.
        The system relies on integer arithmetic for 'held' values.
        """
        agent = self.sim.agents[0]
        agent.compute_held = 5.5 # Float injection

        # Step simulation
        try:
            self.sim.step()
        except ValueError as e:
            # Expected behavior: strict boundary rejection
            self.assertIn("corrupted state", str(e))
            return

        # Check if type integrity is maintained
        if isinstance(agent.compute_held, float):
             self.fail("Simulation allowed float state pollution in integer-only field.")

if __name__ == '__main__':
    unittest.main()
