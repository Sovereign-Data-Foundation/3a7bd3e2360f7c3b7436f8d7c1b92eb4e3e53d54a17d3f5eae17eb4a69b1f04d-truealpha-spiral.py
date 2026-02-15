import hashlib
import json
import time
import math
from typing import Dict, List, Tuple, Any, Optional

# Constants from TVC v0.2 Spec
GOLDEN = 1.618033988749895
COHERENCE_MIN = 0.95
RESONANCE_THRESHOLD = 5.0
ENERGY_COST_MAX = 100.0  # Max allowable energy cost for a valid transition

# Reason Codes
AIRLOCK_DENIED_NOT_DRAFT = "AIRLOCK_DENIED_NOT_DRAFT"
AIRLOCK_DENIED_INVALID_PARENT = "AIRLOCK_DENIED_INVALID_PARENT"
AIRLOCK_DENIED_PROVENANCE_INCOMPLETE = "AIRLOCK_DENIED_PROVENANCE_INCOMPLETE"
AIRLOCK_DENIED_CONSTRAINTS_FAILED = "AIRLOCK_DENIED_CONSTRAINTS_FAILED"
AIRLOCK_DENIED_COHERENCE_TOO_LOW = "AIRLOCK_DENIED_COHERENCE_TOO_LOW"
AIRLOCK_DENIED_BOND_BROKEN = "AIRLOCK_DENIED_BOND_BROKEN"
AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH = "AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH"
AIRLOCK_PASSED_STATE_COMMITTED = "AIRLOCK_PASSED_STATE_COMMITTED"

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def provenance_complete(support: List[str], ledger: List[Dict[str, Any]]) -> bool:
    """
    Checks if all support anchors (hashes) exist in the ledger history.
    """
    if not support:
        return True # No external dependencies required

    ledger_hashes = {block["block_hash"] for block in ledger}
    for anchor in support:
        if anchor not in ledger_hashes:
            return False
    return True

def all_constraints_met(constraints: List[str], payload: Dict[str, Any], ledger: List[Dict[str, Any]]) -> bool:
    """
    Validates IFF constraints.
    Current implementation supports 'SCHEMA_V1' and 'NO_EMPTY_PAYLOAD'.
    """
    for constraint in constraints:
        if constraint == "SCHEMA_V1":
            if "content" not in payload or not isinstance(payload["content"], str):
                return False
        elif constraint == "NO_EMPTY_PAYLOAD":
            if not payload.get("content"):
                return False
        # Add more constraints here as needed
    return True

def bond_valid(payload: Dict[str, Any], expected_bond_hash: str) -> bool:
    """
    Validates the golden bond coupling.
    The payload must declare a 'bond_hash' that matches the deterministic expected hash.
    """
    if "bond_hash" not in payload:
        return False
    return payload["bond_hash"] == expected_bond_hash

def calculate_thermodynamic_honesty(metrics: Dict[str, Any]) -> float:
    """
    Calculates the 'Energy Cost of Deception'.
    Truth scales at 1:1. Hallucination (drift) requires exponential correction.

    Formula: Cost = (1 - coherence) * e^(resonance_gap)
    Where resonance_gap is distance from perfect alignment (assumed 1.0 baseline).
    """
    coherence = metrics.get("coherence", 0.0)
    resonance = metrics.get("resonance", 1.0)

    # Drift from Truth (1.0)
    drift = 1.0 - coherence
    if drift < 0: drift = 0 # Should not happen if normalized

    # Exponential penalty for drift
    # If perfect truth (drift=0), cost is 0.
    # If hallucination (drift>0), cost scales exponentially.
    energy_cost = drift * math.exp(resonance)

    return energy_cost

def crystallize_block(payload: Dict[str, Any], parent_block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Commits the state to an immutable block format.
    """
    # Remove 'draft' mode, set to 'committed'
    committed_payload = payload.copy()
    committed_payload["mode"] = "committed"

    # Calculate block hash
    block_content = json.dumps(committed_payload, sort_keys=True)
    block_hash = sha256(f'{parent_block["block_hash"]}|{block_content}|{time.time()}')

    return {
        "block_hash": block_hash,
        "parent_hash": parent_block["block_hash"],
        "payload": committed_payload,
        "timestamp": time.time_ns(), # Use nanoseconds for precision
        "height": parent_block["height"] + 1
    }

def airlock_gate(candidate_payload: Dict[str, Any], parent_block: Dict[str, Any], ledger: List[Dict[str, Any]]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Airlock Gate: root-of-commit primitive.
    Draft is allowed in; only invariant-satisfying transitions exit as committed state.
    """

    # 0) Airlock entry: draft freedom
    if candidate_payload.get("mode") != "draft":
        return False, AIRLOCK_DENIED_NOT_DRAFT, None

    # 1) Lineage (chain continuity)
    if candidate_payload.get("parent_hash") != parent_block["block_hash"]:
        return False, AIRLOCK_DENIED_INVALID_PARENT, None

    # 2) Provenance completeness (support must resolve)
    if not provenance_complete(candidate_payload.get("support", []), ledger):
        return False, AIRLOCK_DENIED_PROVENANCE_INCOMPLETE, None

    # 3) Constraint set (IFF conditions)
    if not all_constraints_met(candidate_payload.get("constraints", []), candidate_payload, ledger):
        return False, AIRLOCK_DENIED_CONSTRAINTS_FAILED, None

    # 4) Coherence threshold (truth proxy)
    metrics = candidate_payload.get("metrics", {})
    if metrics.get("coherence", 0.0) < COHERENCE_MIN:
        return False, AIRLOCK_DENIED_COHERENCE_TOO_LOW, None

    # 5) Golden bond validation (non-bypassable coupling)
    # Expected bond is SHA256(ParentHash | GOLDEN)
    expected_bond = sha256(f'{parent_block["block_hash"]}|{GOLDEN}')
    if not bond_valid(candidate_payload, expected_bond):
        return False, AIRLOCK_DENIED_BOND_BROKEN, None

    # NEW: Thermodynamic Honesty Check (Input validation phase)
    # Calculate energy cost of this transition BEFORE inflection mechanics
    energy_cost = calculate_thermodynamic_honesty(metrics)
    candidate_payload["metrics"]["thermodynamic_cost"] = energy_cost

    if energy_cost > ENERGY_COST_MAX:
        # Revert "Truth as the Path of Least Resistance": High energy cost implies deception/hallucination masking
        return False, AIRLOCK_DENIED_ENERGY_COST_TOO_HIGH, None

    # 6) Inflection mechanics (deterministic amplification + collapse)
    resonance = float(metrics.get("resonance", 0.0))

    # Simulate deterministic amplification loop (conceptually)
    while resonance < RESONANCE_THRESHOLD:
        resonance *= GOLDEN

    # Inflection-triggered collapse to commitment-ready state
    if resonance >= RESONANCE_THRESHOLD:
        candidate_payload["metrics"]["complexity"] = 0.0
        candidate_payload["metrics"]["resonance"] = resonance * (GOLDEN ** 2)

    # 7) Exit to reality: crystallize + commit (irreversible)
    new_block = crystallize_block(candidate_payload, parent_block)
    ledger.append(new_block)

    return True, AIRLOCK_PASSED_STATE_COMMITTED, new_block
