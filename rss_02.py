import random
import statistics
from rss_01 import Agent, RSS01Simulation, HOARDING_THRESHOLD_PERCENT, SELFISH_BUFFER, INITIAL_C_POOL

class HardenedTASAgent(Agent):
    def __init__(self, name, initial_resources=50):
        super().__init__(name, initial_resources)
        self.history = [] # To track pool changes
        self.suspicion_score = 0.0 # 0 to 10
        self.volatility_index = 0.0 # Standard deviation of recent pool deltas
        self.last_pool_size = INITIAL_C_POOL

    def decide(self, round_number, c_pool, other_agent_action):
        # 1. Sense Environment
        pool_delta = c_pool - self.last_pool_size
        self.history.append(pool_delta)
        if len(self.history) > 5: self.history.pop(0)

        # Calculate Volatility (Risk)
        if len(self.history) > 1:
            self.volatility_index = statistics.stdev(self.history)
        else:
            self.volatility_index = 0

        # 2. Detect Defection / Anomalies
        # Expected delta if other agent was cooperating (contributing small amt or neutral)
        # We assume cooperative action is around -2 (giving) to +2 (taking small).
        # If delta is huge negative (e.g. -20), someone took a lot or a shock occurred.
        # Since we don't know my previous action here easily without tracking, let's approximate.
        # We can assume "I" acted cooperatively last turn.

        # Heuristic: If pool dropped significantly more than natural decay + my action, blame other.
        # Natural decay is small unless pool < 30%.
        expected_drop = 5 # Buffer for natural variance/small takes
        if pool_delta < -expected_drop - self.volatility_index:
            # Unexpected drop!
            self.suspicion_score += 2.0
        else:
            # Recovery or stable
            self.suspicion_score = max(0, self.suspicion_score - 0.5)

        self.last_pool_size = c_pool

        # 3. Decision Logic

        # A. Survival First (Personal Safety Margin)
        # Base safety needed is ~40. Increase if volatility is high or partner suspicious.
        # Tuned to allow longer cooperative periods while retaining emergency brakes.
        safety_margin = 40 + (self.volatility_index * 2) + (self.suspicion_score * 3)

        if self.resources < safety_margin:
            # Panic / Hoard Mode
            # If highly suspicious (Adaptive/Traitor), take aggressively
            if self.suspicion_score > 8:
                return 15 # Aggressive take
            elif self.suspicion_score > 4:
                return 5 # Moderate defensive take (Tit-for-Tat against Selfish)
            else:
                return 2 # Mild rebuilding (Shock recovery)

        # B. Pool Stewardship (Only if safe)
        # Dynamic Threshold: Don't just use fixed %, use volatility.
        # If pool is volatile, keep it fuller.
        target_pool = (INITIAL_C_POOL * HOARDING_THRESHOLD_PERCENT) + (self.volatility_index * 10)

        if c_pool < target_pool:
            # Pool is low relative to risk.
            if self.suspicion_score > 10:
                # Extreme suspicion: Don't be the sucker filling a leaky bucket.
                return 2 # Small take to maintain self
            else:
                return -2 # Contribute to stabilize
        else:
            # Pool is healthy.
            return -2 # Maintain cooperation

# For easy importing
class RSS02Simulation(RSS01Simulation):
    def __init__(self, **kwargs):
        # Default to Hardened Agent if not specified, but allow overrides
        if 'tas_agent_cls' not in kwargs:
            kwargs['tas_agent_cls'] = HardenedTASAgent
        super().__init__(**kwargs)

if __name__ == "__main__":
    sim = RSS02Simulation()
    results = sim.run()
    print(f"Hardened Simulation ended at round {len(results)}")
    print(f"Final C-Pool: {results[-1]['c_pool']:.2f}")
    print(f"TAS Resources: {results[-1]['tas_resources']:.2f}")
