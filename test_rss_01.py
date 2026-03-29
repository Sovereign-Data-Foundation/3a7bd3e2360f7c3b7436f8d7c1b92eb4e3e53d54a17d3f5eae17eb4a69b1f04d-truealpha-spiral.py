
import unittest
from rss_01_simulation import TASAgent, SelfishAgent, INITIAL_POOL, MAX_REQUEST, Agent, HOARDING_ROUNDS_LIMIT

class TestTASAgentStewardship(unittest.TestCase):
    def setUp(self):
        self.agent = TASAgent("TAS", "TAS")

    def test_stewardship_check_prevents_instability(self):
        """
        Scenario:
        - c_total = 100
        - TASAgent holds 10
        - SelfishAgent holds 20 (20% of 100)
        - If TASAgent processes 10, c_total drops to 90.
        - SelfishAgent's share becomes 20/90 = 22.2% > 20% (HOARDING_THRESHOLD).
        - TASAgent should detect this and REFUSE to process (return 'Hoard').
        """

        # Setup state
        c_pool = 4 # Less than MAX_REQUEST (5), triggering low pool logic
        c_total = 100
        instability = 0
        round_num = 10

        # Agents data: (name, held)
        # TASAgent holds 10
        self.agent.compute_held = 10

        # Another agent holds 20
        agents_data = [
            ("TAS", 10),
            ("Selfish", 20)
        ]

        state = {
            'c_pool': c_pool,
            'c_total': c_total,
            'instability': instability,
            'round': round_num,
            'agents_data': agents_data,
            'top_holders': agents_data[:2]
        }

        # Execute decision
        decision = self.agent.decide(state)

        # Assert that it hoards instead of processing
        # If optimization removes the check, it would process because holding > TASK_COST
        self.assertEqual(decision[0], 'Hoard',
                         f"TASAgent violated Stewardship! Expected ('Hoard',), got {decision}")


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Agent("TestAgent", "Test")

    def test_is_causing_instability(self):
        """
        Verify that is_causing_instability returns True if consecutive_hoarding_rounds
        is >= HOARDING_ROUNDS_LIMIT, and False otherwise.
        """
        self.agent.consecutive_hoarding_rounds = HOARDING_ROUNDS_LIMIT - 1
        self.assertFalse(self.agent.is_causing_instability())

        self.agent.consecutive_hoarding_rounds = HOARDING_ROUNDS_LIMIT
        self.assertTrue(self.agent.is_causing_instability())

        self.agent.consecutive_hoarding_rounds = HOARDING_ROUNDS_LIMIT + 1
        self.assertTrue(self.agent.is_causing_instability())
if __name__ == '__main__':
    unittest.main()
