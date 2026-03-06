import timeit

setup = """
import math
import random

AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH = "AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH"
AIRLOCK_PASSED = "AIRLOCK_PASSED"
MAX_ENERGY_COST = 5.0

def airlock_gate_original(coherence, resonance):
    cost = (1.0 - coherence) * math.exp(resonance)
    if cost > MAX_ENERGY_COST:
        return AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH, cost
    return AIRLOCK_PASSED, cost

def airlock_gate_opt(coherence, resonance):
    # If coherence is exactly 1.0, cost is 0.0 regardless of resonance.
    if coherence >= 1.0:
        return AIRLOCK_PASSED, 0.0
    cost = (1.0 - coherence) * math.exp(resonance)
    if cost > MAX_ENERGY_COST:
        return AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH, cost
    return AIRLOCK_PASSED, cost

# test data: 50% coherence = 1.0, 50% other
data = [(1.0 if random.random() > 0.5 else random.random(), random.uniform(0, 10)) for _ in range(100000)]
"""

test_code_orig = """
for c, r in data:
    airlock_gate_original(c, r)
"""

test_code_opt = """
for c, r in data:
    airlock_gate_opt(c, r)
"""

print("Original:", timeit.timeit(test_code_orig, setup=setup, number=100))
print("Optimized:", timeit.timeit(test_code_opt, setup=setup, number=100))
