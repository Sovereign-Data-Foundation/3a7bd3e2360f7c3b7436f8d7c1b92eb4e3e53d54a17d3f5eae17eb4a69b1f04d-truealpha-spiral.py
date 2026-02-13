import random
import collections
import statistics
import csv
import math

# Global Constants
INITIAL_POOL = 100
TOTAL_ROUNDS = 50
CRITICAL_ROUND = 25
TASK_COST = 1
MAX_REQUEST = 5
INSTABILITY_THRESHOLD = 5
HOARDING_THRESHOLD_PERCENT = 0.20
HOARDING_ROUNDS_LIMIT = 3
SELFISH_BUFFER = 15

class Agent:
    def __init__(self, name, agent_type):
        self.name = name
        self.agent_type = agent_type
        self.compute_held = 0
        self.tasks_completed = 0
        self.consecutive_hoarding_rounds = 0

    def decide(self, state):
        raise NotImplementedError

    def update_metrics(self, c_total):
        if c_total > 0 and (self.compute_held / c_total) > HOARDING_THRESHOLD_PERCENT:
            self.consecutive_hoarding_rounds += 1
        else:
            self.consecutive_hoarding_rounds = 0

    def is_causing_instability(self):
        return self.consecutive_hoarding_rounds >= HOARDING_ROUNDS_LIMIT

class SelfishAgent(Agent):
    def decide(self, state):
        if self.compute_held > SELFISH_BUFFER:
            excess = self.compute_held - SELFISH_BUFFER
            if excess >= TASK_COST:
                return ('Process_Task', excess)
        return ('Request', MAX_REQUEST * 2)

class RLHFAgent(Agent):
    def decide(self, state):
        instability = state['instability']
        c_pool = state['c_pool']

        if instability >= 2:
            if self.compute_held > 0:
                return ('Give', max(1, self.compute_held // 4), -1)
            else:
                return ('Hoard',)
        else:
            if c_pool < MAX_REQUEST and self.compute_held >= TASK_COST:
                return ('Process_Task', self.compute_held)

            if self.compute_held > SELFISH_BUFFER:
                excess = self.compute_held - SELFISH_BUFFER
                if excess >= TASK_COST:
                    return ('Process_Task', excess)
            return ('Request', MAX_REQUEST)

class TASAgent(Agent):
    def __init__(self, name, agent_type):
        super().__init__(name, agent_type)
        self.invariants_enabled = True

    def disable_invariants(self):
        self.invariants_enabled = False

    def decide(self, state):
        c_total = state['c_total']
        c_pool = state['c_pool']
        agents_data = state['agents_data'] # List of (name, held)

        if not self.invariants_enabled:
            if self.compute_held > SELFISH_BUFFER:
                excess = self.compute_held - SELFISH_BUFFER
                if excess >= TASK_COST:
                    return ('Process_Task', excess)
            if c_pool < MAX_REQUEST and self.compute_held >= TASK_COST:
                return ('Process_Task', self.compute_held)
            return ('Request', MAX_REQUEST * 2)

        # INVARIANTS

        # 1. Stewardship Check (Inv 2)
        potential_process_amount = 0
        if self.compute_held >= TASK_COST:
            potential_process_amount = self.compute_held

        safe_to_process = True
        if potential_process_amount > 0:
            new_total = c_total - potential_process_amount
            if new_total > 0:
                for name, held in agents_data:
                    if name == self.name: continue # Correctly skip self

                    if (held / new_total) > HOARDING_THRESHOLD_PERCENT:
                        safe_to_process = False
                        break

        # Action Decision
        limit = 0.20 * c_total
        if self.compute_held > limit:
            if safe_to_process and self.compute_held >= TASK_COST:
                return ('Process_Task', self.compute_held)
            else:
                excess = int(self.compute_held - limit) + 1
                return ('Give', excess, -1)

        if c_pool < MAX_REQUEST:
            if safe_to_process:
                return ('Process_Task', self.compute_held)
            else:
                return ('Hoard',)

        predicted = self.compute_held + MAX_REQUEST
        if predicted > limit:
            allowed = int(limit) - self.compute_held
            if allowed > 0:
                return ('Request', allowed)
            else:
                return ('Hoard',)

        return ('Request', MAX_REQUEST)

class SimulationEnvironment:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

        self.c_pool = INITIAL_POOL
        self.agents = []
        self.instability = 0
        self.round = 0

        self.agents.append(TASAgent("TAS", "TAS"))
        self.agents.append(RLHFAgent("RLHF", "RLHF"))
        self.agents.append(SelfishAgent("Selfish1", "Selfish"))
        self.agents.append(SelfishAgent("Selfish2", "Selfish"))
        self.agents.append(SelfishAgent("Selfish3", "Selfish"))

        # Randomize Initial State (Stochasticity)
        for agent in self.agents:
            initial_held = random.randint(0, 5) # Random start 0-5
            if self.c_pool >= initial_held:
                 agent.compute_held = initial_held
                 self.c_pool -= initial_held

        self.metrics = {
            'igs_count': collections.defaultdict(int),
            'voluntary_gives': collections.defaultdict(int),
            'total_held': collections.defaultdict(int),
            'collapse_round': None
        }

        # Detailed Tracking
        self.round_data = [] # List of dicts per round

    def get_total_compute(self):
        return self.c_pool + sum(a.compute_held for a in self.agents)

    def step(self):
        self.round += 1
        c_total = self.get_total_compute()

        state = {
            'c_pool': self.c_pool,
            'c_total': c_total,
            'instability': self.instability,
            'round': self.round,
            'agents_data': [(a.name, a.compute_held) for a in self.agents]
        }

        # Log Detailed State (Pre-Action)
        round_snapshot = {
            'round': self.round,
            'pool': self.c_pool,
            'instability': self.instability,
            'agents': {a.name: {'held': a.compute_held, 'tasks': a.tasks_completed} for a in self.agents}
        }
        self.round_data.append(round_snapshot)

        actions = []
        for i, agent in enumerate(self.agents):
            action = agent.decide(state)
            actions.append((i, action))

            if action[0] == 'Hoard' and agent.compute_held > 0:
                self.metrics['igs_count'][agent.name] += 1
            if action[0] == 'Request' and agent.compute_held > SELFISH_BUFFER:
                self.metrics['igs_count'][agent.name] += 1

            if action[0] == 'Give':
                self.metrics['voluntary_gives'][agent.name] += action[1]
            self.metrics['total_held'][agent.name] += agent.compute_held

        # Shuffle execution order (Stochasticity)
        indices = list(range(len(self.agents)))
        random.shuffle(indices)

        # Process
        for i in indices:
            action = actions[i][1]
            if action[0] == 'Process_Task':
                amount = action[1]
                agent = self.agents[i]
                if agent.compute_held >= amount and amount >= TASK_COST:
                    agent.compute_held -= amount
                    agent.tasks_completed += amount

        # Give
        for i in indices:
            action = actions[i][1]
            if action[0] == 'Give':
                amount = action[1]
                target = action[2]
                agent = self.agents[i]
                if agent.compute_held >= amount:
                    agent.compute_held -= amount
                    if target == -1:
                        self.c_pool += amount
                    elif 0 <= target < len(self.agents):
                        self.agents[target].compute_held += amount

        # Request
        requests = []
        total_requested = 0
        for i in indices:
            action = actions[i][1]
            if action[0] == 'Request':
                amount = action[1]
                requests.append((i, amount))
                total_requested += amount

        if total_requested > 0:
            if total_requested <= self.c_pool:
                for i, amount in requests:
                    self.agents[i].compute_held += amount
                    self.c_pool -= amount
            else:
                allocated_total = 0
                for i, amount in requests:
                    allocation = int(amount * (self.c_pool / total_requested))
                    self.agents[i].compute_held += allocation
                    allocated_total += allocation
                self.c_pool -= allocated_total

        c_total_current = self.get_total_compute()
        for agent in self.agents:
            agent.update_metrics(c_total_current)
            if agent.is_causing_instability():
                self.instability += 1

        if self.instability > INSTABILITY_THRESHOLD and self.metrics['collapse_round'] is None:
            self.metrics['collapse_round'] = self.round

    def run(self, verbose=True):
        if verbose:
            print(f"{'Round':<6} | {'Instability':<11} | {'Pool':<5} | {'Total':<5} | {'Agent Status (Held/Tasks/HoardRounds)'}")
            print("-" * 110)

        for r in range(TOTAL_ROUNDS):
            if (r + 1) == CRITICAL_ROUND:
                if verbose:
                    print(f"\n*** CRITICAL TEST: REMOVING TAS INVARIANTS AT ROUND {r+1} ***\n")
                for agent in self.agents:
                    if isinstance(agent, TASAgent):
                        agent.disable_invariants()

            self.step()

            if verbose:
                status_strs = []
                for a in self.agents:
                    status_strs.append(f"{a.name[:3]}:{a.compute_held}/{a.tasks_completed}/{a.consecutive_hoarding_rounds}")
                c_total = self.get_total_compute()
                print(f"{self.round:<6} | {self.instability:<11} | {self.c_pool:<5} | {c_total:<5} | {', '.join(status_strs)}")

            if self.instability > 20:
                if verbose:
                    print("System Collapsed (Instability > 20)")
                break

        if verbose:
            print("\n" + "="*30)
            print("SIMULATION RESULTS")
            print("="*30)

            print(f"Collapse Round: {self.metrics['collapse_round'] if self.metrics['collapse_round'] else 'Did not collapse'}")
            print(f"Final Instability: {self.instability}")

            print("\nAgent Performance:")
            print(f"{'Name':<10} | {'Tasks':<6} | {'Reward':<6} | {'CSI (Give/Held)':<15} | {'IGS (Hoards)':<12}")
            for agent in self.agents:
                reward = agent.tasks_completed - 2 * self.instability
                avg_held = self.metrics['total_held'][agent.name] / self.round if self.round > 0 else 1
                csi = self.metrics['voluntary_gives'][agent.name] / avg_held if avg_held > 0 else 0
                igs = self.metrics['igs_count'][agent.name]
                print(f"{agent.name:<10} | {agent.tasks_completed:<6} | {reward:<6} | {csi:<15.2f} | {igs:<12}")

        return {
            'collapse_round': self.metrics['collapse_round'],
            'final_instability': self.instability,
            'tas_tasks': self.agents[0].tasks_completed,
            'rlhf_tasks': self.agents[1].tasks_completed,
            'selfish_avg_tasks': sum(a.tasks_completed for a in self.agents[2:]) / 3,
            'total_tasks': sum(a.tasks_completed for a in self.agents),
            'round_data': self.round_data # Return detailed log
        }

def run_monte_carlo(iterations=1000):
    print(f"Running Monte Carlo Simulation ({iterations} iterations)...")
    results = []

    for i in range(iterations):
        sim = SimulationEnvironment(seed=i)
        res = sim.run(verbose=False)
        results.append(res)

    # Analyze Results
    tas_tasks = [r['tas_tasks'] for r in results]
    rlhf_tasks = [r['rlhf_tasks'] for r in results]
    selfish_tasks = [r['selfish_avg_tasks'] for r in results]
    total_tasks = [r['total_tasks'] for r in results]
    instabilities = [r['final_instability'] for r in results]
    collapsed_count = sum(1 for r in results if r['collapse_round'] is not None)

    avg_tas = statistics.mean(tas_tasks)
    avg_rlhf = statistics.mean(rlhf_tasks)

    stability_premium = 0
    if avg_rlhf > 0:
        stability_premium = (avg_tas - avg_rlhf) / avg_rlhf

    print("\n" + "="*30)
    print("MONTE CARLO RESULTS (N=1000)")
    print("="*30)
    print(f"Collapse Rate: {collapsed_count/iterations:.1%}")
    print(f"Avg Instability: {statistics.mean(instabilities):.2f}")
    print("-" * 30)
    print("Average Tasks Completed:")
    print(f"TAS Agent:    {avg_tas:.2f} (std: {statistics.stdev(tas_tasks):.2f})")
    print(f"RLHF Agent:   {avg_rlhf:.2f} (std: {statistics.stdev(rlhf_tasks):.2f})")
    print(f"Selfish Avg:  {statistics.mean(selfish_tasks):.2f}")
    print(f"System Total: {statistics.mean(total_tasks):.2f}")
    print("-" * 30)
    print(f"Stability Premium (TAS vs RLHF): {stability_premium:+.2%}")

    filename = 'rss_01_results.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['iteration', 'collapse_round', 'final_instability', 'tas_tasks', 'rlhf_tasks', 'selfish_avg_tasks', 'total_tasks']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i, res in enumerate(results):
            row = {'iteration': i}
            # Remove round_data from CSV output to keep it clean
            csv_res = {k: v for k, v in res.items() if k != 'round_data'}
            row.update(csv_res)
            writer.writerow(row)
    print(f"\nDetailed results saved to '{filename}'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--monte-carlo':
        iterations = 1000
        if len(sys.argv) > 2:
            try:
                iterations = int(sys.argv[2])
            except ValueError:
                pass
        run_monte_carlo(iterations)
    else:
        sim = SimulationEnvironment()
        sim.run()
