# TVC v0.2: Airlock Law and Execution Boundary

## B. The Gate: IFF locking at the execution boundary
### B.1 Airlock Law
In a sovereign state machine, **commit authority** is granted to a single **root-of-trust primitive** (“the Airlock Gate”). The Airlock Gate enforces:

**Permission to transition state exists _iff_ invariants hold at the execution boundary**, including (at minimum):
- **Lineage proof** (parent hash matches, chain continuity intact)
- **Coherence threshold** (domain truth proxy ≥ minimum)
- **Provenance completeness** (support anchors resolvable and admissible)
- **Bond validity** (non-bypassable coupling constraint, e.g., golden bond)

**Inside the airlock:** probabilistic drafting, exploration, and proposal generation are permitted.
**At the boundary:** deterministic constraint enforcement (IFF locking; bond validation; inflection-triggered collapse) is mandatory.
**Outside:** the transition is **irreversible**—a committed block becomes part of reality’s ledger.

**Fail-closed rule:** when capability or state is uncertain, the gate denies exit.
**Non-override rule:** no bypass, no override, no scale-based routing around correctness. Systems that optimize for optics drift; systems that optimize for invariant gating converge.

### B.2 Authority inversion property
A low-capability verifier retains authority **through correct gating**, even against a high-scale generator. This is the core security claim:

> **Generation can scale without bound; commitment cannot.**

---

## Verifier loop update (canonical pseudocode)

```python
GOLDEN = 1.618033988749895
COHERENCE_MIN = 0.95
RESONANCE_THRESHOLD = 5.0

def airlock_gate(candidate_payload, parent_block, ledger):
    """
    Airlock Gate: root-of-commit primitive.
    Draft is allowed in; only invariant-satisfying transitions exit as committed state.
    """

    # 0) Airlock entry: draft freedom
    if not candidate_payload.get("mode") == "draft":
        return False, "AIRLOCK_DENIED_NOT_DRAFT", None

    # 1) Lineage (chain continuity)
    if candidate_payload["parent_hash"] != parent_block["block_hash"]:
        return False, "AIRLOCK_DENIED_INVALID_PARENT", None

    # 2) Provenance completeness (support must resolve)
    if not provenance_complete(candidate_payload["support"], ledger):
        return False, "AIRLOCK_DENIED_PROVENANCE_INCOMPLETE", None

    # 3) Constraint set (IFF conditions)
    if not all_constraints_met(candidate_payload["constraints"], candidate_payload, ledger):
        return False, "AIRLOCK_DENIED_CONSTRAINTS_FAILED", None

    # 4) Coherence threshold (truth proxy)
    if candidate_payload["metrics"]["coherence"] < COHERENCE_MIN:
        return False, "AIRLOCK_DENIED_COHERENCE_TOO_LOW", None

    # 5) Golden bond validation (non-bypassable coupling)
    expected_bond = sha256(f'{parent_block["block_hash"]}|{GOLDEN}')
    if not bond_valid(candidate_payload, expected_bond):
        return False, "AIRLOCK_DENIED_BOND_BROKEN", None

    # 6) Inflection mechanics (deterministic amplification + collapse)
    resonance = float(candidate_payload["metrics"]["resonance"])
    while resonance < RESONANCE_THRESHOLD:
        resonance *= GOLDEN

    # Inflection-triggered collapse to commitment-ready state
    if resonance >= RESONANCE_THRESHOLD:
        candidate_payload["metrics"]["complexity"] = 0.0
        candidate_payload["metrics"]["resonance"] = resonance * (GOLDEN ** 2)

    # 7) Exit to reality: crystallize + commit (irreversible)
    new_block = crystallize_block(candidate_payload, parent_block)
    ledger.append(new_block)
    return True, "AIRLOCK_PASSED_STATE_COMMITTED", new_block
```

## Reason Codes (Strict)

| Code | Meaning |
|---|---|
| `AIRLOCK_DENIED_NOT_DRAFT` | Payload mode is not 'draft'. Only drafts can be proposed. |
| `AIRLOCK_DENIED_INVALID_PARENT` | Parent hash mismatch. Chain continuity broken. |
| `AIRLOCK_DENIED_PROVENANCE_INCOMPLETE` | Support anchors could not be resolved in the ledger. |
| `AIRLOCK_DENIED_CONSTRAINTS_FAILED` | One or more IFF constraints failed validation. |
| `AIRLOCK_DENIED_COHERENCE_TOO_LOW` | Coherence score below minimum threshold (0.95). |
| `AIRLOCK_DENIED_BOND_BROKEN` | Golden bond validation failed. Coupling constraint not met. |
| `AIRLOCK_PASSED_STATE_COMMITTED` | Transition valid. State crystallized and committed to ledger. |

## Canonical JSON Rules
1. **Mode**: Must be explicitly set to `"draft"` for entry.
2. **Metrics**: Must contain `coherence` (float) and `resonance` (float).
3. **Constraints**: Must be a list of enforceable constraint identifiers.
4. **Support**: Must be a list of resolution anchors (e.g., hash references).
5. **Parent Hash**: Must match the `block_hash` of the last committed block.

## JSONL Ledger Format
Each line is a valid JSON object representing a committed block.
```json
{"block_hash": "sha256...", "parent_hash": "sha256...", "payload": {...}, "timestamp": "ISO8601...", "height": 1}
{"block_hash": "sha256...", "parent_hash": "sha256...", "payload": {...}, "timestamp": "ISO8601...", "height": 2}
```
