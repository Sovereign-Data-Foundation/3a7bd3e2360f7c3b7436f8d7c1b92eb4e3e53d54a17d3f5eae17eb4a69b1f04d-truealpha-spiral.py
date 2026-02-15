
import json
import hashlib
from tas_core.alpha.airlock import airlock_gate

# Mock Ledger and Parent Block
def create_genesis_block():
    return {
        "block_hash": "genesis_hash_0000",
        "parent_hash": "0000000000000000",
        "payload": {"mode": "committed", "message": "Genesis"},
        "timestamp": 0,
        "height": 0
    }

ledger = [create_genesis_block()]
parent_block = ledger[-1]

# Helper to generate a valid bond hash
def get_bond_hash(parent_hash, golden):
    return hashlib.sha256(f"{parent_hash}|{golden}".encode('utf-8')).hexdigest()

# Scenario 1: Valid draft, fails provenance (support anchor missing)
draft_provenance_fail = {
    "mode": "draft",
    "parent_hash": parent_block["block_hash"],
    "support": ["non_existent_hash_1234"], # Fails here
    "constraints": [],
    "metrics": {"coherence": 0.99, "resonance": 1.0},
    "bond_hash": get_bond_hash(parent_block["block_hash"], 1.618033988749895)
}

success, reason, new_block = airlock_gate(draft_provenance_fail, parent_block, ledger)
print(f"Scenario 1 (Provenance Fail): Success={success}, Reason={reason}")
assert reason == "AIRLOCK_DENIED_PROVENANCE_INCOMPLETE"


# Scenario 2: Valid draft, fails coherence (< 0.95)
draft_coherence_fail = {
    "mode": "draft",
    "parent_hash": parent_block["block_hash"],
    "support": [],
    "constraints": [],
    "metrics": {"coherence": 0.94, "resonance": 1.0}, # Fails here
    "bond_hash": get_bond_hash(parent_block["block_hash"], 1.618033988749895)
}

success, reason, new_block = airlock_gate(draft_coherence_fail, parent_block, ledger)
print(f"Scenario 2 (Coherence Fail): Success={success}, Reason={reason}")
assert reason == "AIRLOCK_DENIED_COHERENCE_TOO_LOW"

# Scenario 3: "High Energy Deception" (Coherence ok, but High Resonance gap -> High Energy Cost)
# This simulates a "lie" that is trying hard to look valid (high complexity/resonance)
draft_energy_fail = {
    "mode": "draft",
    "parent_hash": parent_block["block_hash"],
    "support": [],
    "constraints": [],
    "metrics": {"coherence": 0.95, "resonance": 10.0}, # High resonance gap
    "bond_hash": get_bond_hash(parent_block["block_hash"], 1.618033988749895)
}

# Cost = (1 - 0.95) * e^10 = 0.05 * 22026 = ~1101 > 100.0 (Limit)
success, reason, new_block = airlock_gate(draft_energy_fail, parent_block, ledger)
print(f"Scenario 3 (Energy Cost Fail): Success={success}, Reason={reason}")
assert reason == "AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH"


# Scenario 4: Valid draft, passes all invariants
draft_success = {
    "mode": "draft",
    "parent_hash": parent_block["block_hash"],
    "support": [],
    "constraints": [],
    "metrics": {"coherence": 0.99, "resonance": 1.0},
    "bond_hash": get_bond_hash(parent_block["block_hash"], 1.618033988749895)
}

success, reason, new_block = airlock_gate(draft_success, parent_block, ledger)
print(f"Scenario 4 (Success): Success={success}, Reason={reason}")
assert reason == "AIRLOCK_PASSED_STATE_COMMITTED"
assert new_block["parent_hash"] == parent_block["block_hash"]
assert len(ledger) == 2 # Genesis + 1
# Verify energy cost was logged
print(f"Success Block Energy Cost: {new_block['payload']['metrics'].get('thermodynamic_cost')}")


print("\nAirlock Demo Complete. Ledger State:")
for block in ledger:
    print(json.dumps(block))
