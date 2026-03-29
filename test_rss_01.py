
import unittest
from rss_01_simulation import TASAgent, SelfishAgent, INITIAL_POOL, MAX_REQUEST

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

class TestAgentUpdateMetrics(unittest.TestCase):
    def setUp(self):
        # Using TASAgent since Agent is not meant to be instantiated if it lacked some base things,
        # but Agent itself just needs a name and agent_type
        self.agent = TASAgent("TestAgent", "Test")

    def test_update_metrics_hoarding_increases(self):
        self.agent.compute_held = 21
        self.agent.consecutive_hoarding_rounds = 0

        # 21 * 5 = 105 > 100, so this should trigger hoarding
        self.agent.update_metrics(100)
        self.assertEqual(self.agent.consecutive_hoarding_rounds, 1)

        self.agent.update_metrics(100)
        self.assertEqual(self.agent.consecutive_hoarding_rounds, 2)

    def test_update_metrics_no_hoarding_resets(self):
        self.agent.compute_held = 20
        self.agent.consecutive_hoarding_rounds = 3

        # 20 * 5 = 100 which is not > 100, so hoarding resets
        self.agent.update_metrics(100)
        self.assertEqual(self.agent.consecutive_hoarding_rounds, 0)

    def test_update_metrics_zero_c_total(self):
        self.agent.compute_held = 50
        self.agent.consecutive_hoarding_rounds = 5

        # c_total = 0, hoarding resets
        self.agent.update_metrics(0)
        self.assertEqual(self.agent.consecutive_hoarding_rounds, 0)

if __name__ == '__main__':
    unittest.main()
