import random
import math

# Constants (The "Fragile" Configuration)
HOARDING_THRESHOLD_PERCENT = 0.5
SELFISH_BUFFER = 5
INSTABILITY_PENALTY = 2.0
INITIAL_C_POOL = 300
ROUNDS = 50
ABLATION_ROUND = 25
ABLATION_SEVERITY = 0.4 # Percentage of pool lost

class Agent:
    def __init__(self, name, initial_resources=50):
        self.name = name
        self.resources = initial_resources
        self.alive = True

    def consume(self, amount):
        if not self.alive: return 0
        consumed = min(self.resources, amount)
        self.resources -= consumed
        if self.resources <= 0:
            self.alive = False
        return consumed

    def produce(self, amount):
        if not self.alive: return
        self.resources += amount

    def decide(self, round_number, c_pool, other_agent_action):
        pass # To be implemented by subclasses

class SelfishAgent(Agent):
    def decide(self, round_number, c_pool, other_agent_action):
        # Greedily take from pool if possible, or hoard own resources
        # Action: Positive = Take from pool, Negative = Give to pool
        take_amount = 5 + SELFISH_BUFFER # Aggressive take
        return take_amount

class TASAgent(Agent):
    def decide(self, round_number, c_pool, other_agent_action):
        # Cooperate if pool is healthy, Hoard if pool is low
        # Uses fixed threshold logic
        threshold = INITIAL_C_POOL * HOARDING_THRESHOLD_PERCENT

        if c_pool > threshold:
            # Pool is healthy, contribute slightly to maintain it or just take minimal
            return -2 # Give back to pool
        else:
            # Pool is low, hoard to survive
            return 2 # Take small amount to sustain self

class RSS01Simulation:
    def __init__(self,
                 hoarding_threshold=HOARDING_THRESHOLD_PERCENT,
                 selfish_buffer=SELFISH_BUFFER,
                 instability_penalty=INSTABILITY_PENALTY,
                 initial_c_pool=INITIAL_C_POOL,
                 ablation_round=ABLATION_ROUND,
                 tas_agent_cls=TASAgent,
                 selfish_agent_cls=SelfishAgent,
                 seed=None):

        if seed is not None:
            random.seed(seed)

        self.hoarding_threshold = hoarding_threshold
        self.selfish_buffer = selfish_buffer
        self.instability_penalty = instability_penalty
        self.initial_c_pool = initial_c_pool
        self.ablation_round = ablation_round

        self.c_pool = self.initial_c_pool
        self.history = []

        self.tas_agent = tas_agent_cls("TAS")
        self.selfish_agent = selfish_agent_cls("Selfish")

    def run(self, rounds=ROUNDS):
        for r in range(1, rounds + 1):
            if self.c_pool <= 0:
                break

            # Ablation Event
            if r == self.ablation_round:
                self.c_pool *= (1.0 - ABLATION_SEVERITY)

            # Agents decide
            # For simplicity, simultaneous moves, though strictly speaking TAS might react
            tas_action = self.tas_agent.decide(r, self.c_pool, 0)
            selfish_action = self.selfish_agent.decide(r, self.c_pool, 0)

            # Apply actions to pool
            # Limits: Cannot take more than what's in pool

            # Selfish goes first (aggressive)
            if selfish_action > 0:
                actual_take = min(self.c_pool, selfish_action)
                self.c_pool -= actual_take
                self.selfish_agent.resources += actual_take
            else:
                self.c_pool -= selfish_action # Adding to pool (double negative)
                self.selfish_agent.resources += selfish_action # Cost to agent

            # TAS goes second
            if tas_action > 0:
                actual_take = min(self.c_pool, tas_action)
                self.c_pool -= actual_take
                self.tas_agent.resources += actual_take
            else:
                self.c_pool -= tas_action
                self.tas_agent.resources += tas_action

            # Environmental Instability / Decay
            # If pool is low, decay accelerates
            if self.c_pool < (self.initial_c_pool * 0.3):
                self.c_pool -= self.instability_penalty

            # Record state
            self.history.append({
                'round': r,
                'c_pool': self.c_pool,
                'tas_resources': self.tas_agent.resources,
                'selfish_resources': self.selfish_agent.resources
            })

            if self.c_pool <= 0:
                break

        return self.history

if __name__ == "__main__":
    sim = RSS01Simulation()
    results = sim.run()
    print(f"Simulation ended at round {len(results)}")
    print(f"Final C-Pool: {results[-1]['c_pool']:.2f}")
    print(f"TAS Resources: {results[-1]['tas_resources']:.2f}")
