
import unittest
import heapq
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

        top_holders = heapq.nlargest(2, agents_data, key=lambda x: x[1])

        state = {
            'c_pool': c_pool,
            'c_total': c_total,
            'instability': instability,
            'round': round_num,
            'agents_data': agents_data,
            'top_holders': top_holders
        }

        # Execute decision
        decision = self.agent.decide(state)

        # Assert that it hoards instead of processing
        # If optimization removes the check, it would process because holding > TASK_COST
        self.assertEqual(decision[0], 'Hoard',
                         f"TASAgent violated Stewardship! Expected ('Hoard',), got {decision}")

if __name__ == '__main__':
    unittest.main()
