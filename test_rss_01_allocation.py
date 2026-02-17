
import unittest
from rss_01_simulation import SimulationEnvironment

class MockAgent:
    def __init__(self, name):
        self.name = name
        self.compute_held = 0
        self.tasks_completed = 0
        self.consecutive_hoarding_rounds = 0
        self.request_amount = 10

    def decide(self, state):
        return ('Request', self.request_amount)

    def update_metrics(self, c_total):
        pass

    def is_causing_instability(self):
        return False

class TestAllocationLogic(unittest.TestCase):
    def test_proportional_allocation(self):
        """
        Verify that allocation is proportional when total_requested > c_pool.
        """
        sim = SimulationEnvironment()
        sim.c_pool = 10

        # 2 Agents, each requesting 10. Total 20.
        # Pool 10. Ratio 0.5.
        # Expected: 5 each.
        sim.agents = [MockAgent("A1"), MockAgent("A2")]

        sim.step()

        self.assertEqual(sim.agents[0].compute_held, 5)
        self.assertEqual(sim.agents[1].compute_held, 5)
        self.assertEqual(sim.c_pool, 0)

    def test_integer_truncation(self):
        """
        Verify integer truncation behavior matches expected (floor).
        """
        sim = SimulationEnvironment()
        sim.c_pool = 10

        # 3 Agents, requesting 10 each. Total 30.
        # Pool 10. Ratio 1/3.
        # Expected: 10 * 10 // 30 = 3.
        # Remainder 1 stays in pool?
        # Logic: self.c_pool -= allocated_total.
        # allocated_total = 3+3+3 = 9.
        # c_pool should be 10 - 9 = 1.

        sim.agents = [MockAgent("A1"), MockAgent("A2"), MockAgent("A3")]

        sim.step()

        self.assertEqual(sim.agents[0].compute_held, 3)
        self.assertEqual(sim.agents[1].compute_held, 3)
        self.assertEqual(sim.agents[2].compute_held, 3)
        self.assertEqual(sim.c_pool, 1)

if __name__ == '__main__':
    unittest.main()
