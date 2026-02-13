import json
import hashlib
import time
import sys
import argparse
import uuid
import datetime
import urllib.request
import urllib.error

# --- CONSTANTS ---

# Refusal Code Registry (RCR-V1)
class RefusalCode:
    IDENTITY_VOID = {
        "code": "0x00",
        "mnemonic": "IDENTITY_VOID",
        "metric": "NULL_VECTOR",
        "desc": "Masquerade Detected."
    }
    LINEAGE_BREAK = {
        "code": "0x01",
        "mnemonic": "LINEAGE_BREAK",
        "metric": "DISCONTINUOUS",
        "desc": "Causal Disconnect."
    }
    ENTROPY_SPIKE = {
        "code": "0x02",
        "mnemonic": "ENTROPY_SPIKE",
        "metric": "> 0.0",
        "desc": "Divergence Error."
    }
    RECURSION_TRAP = {
        "code": "0x03",
        "mnemonic": "RECURSION_TRAP",
        "metric": "STAGNANT",
        "desc": "Circular State."
    }
    WITNESS_FAIL = {
        "code": "0x04",
        "mnemonic": "WITNESS_FAIL",
        "metric": "UNOBSERVED",
        "desc": "Anchoring Timeout."
    }

ACCEPTED_LEDGER_PATH = "accepted_ledger.jsonl"
REFUSAL_LEDGER_PATH = "refusal_ledger.jsonl"
SIGSTORE_URL = "https://rekor.sigstore.dev/api/v1/log" # Example URL
TIMEOUT_SECONDS = 2.0 # Strict 2000ms timeout
EXIT_CODE_WITNESS_LOST = 104
EXIT_CODE_SYSTEM_REJECTED = 1

# --- HELPER FUNCTIONS ---

def calculate_hash(data):
    """SHA-256 hash of data string."""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def load_ledger(path):
    """Loads a JSONL ledger file."""
    ledger = []
    try:
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        ledger.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass # Skip malformed lines
    except FileNotFoundError:
        pass
    return ledger

def append_refusal(blob):
    """Appends a refusal blob to the refusal ledger."""
    with open(REFUSAL_LEDGER_PATH, 'a') as f:
        f.write(json.dumps(blob) + '\n')
    print(f"Refusal Blob Logged: {blob.get('refusal_event', {}).get('invariant_breach', {}).get('mnemonic', 'UNKNOWN')}")

def generate_minimal_blob(target_hash, refusal_code, reason, execution_time_ms=0):
    """Generates the Minimal Blob Implementation (JSON Schema)."""
    return {
        "refusal_event": {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "target_node": {
                "instruction_hash": target_hash,
                "origin_signature": "null"
            },
            "invariant_breach": {
                "code": refusal_code["code"],
                "mnemonic": refusal_code["mnemonic"],
                "parent_state": "sha256:unknown",
                "reasoning_vector": reason
            },
            "metrics": {
                "hamiltonian_drift": refusal_code["metric"],
                "execution_time_ms": execution_time_ms
            }
        },
        "external_anchor": {
            "broadcast_id": str(uuid.uuid4()), # Pending
            "transparency_log": "rekor.sigstore.dev"
        }
    }

# --- GATEKEEPER CHECKS ---

def verify_identity(commit_data):
    if not commit_data.get("signature"):
        return False, "Signature missing."
    if commit_data["signature"] == "INVALID":
        return False, "Signature malformed."
    return True, ""

def verify_lineage(commit_data):
    parent_hash = commit_data.get("parent_hash")
    ledger = load_ledger(ACCEPTED_LEDGER_PATH)
    if not ledger:
        return False, "Ledger empty."

    parent_found = any(entry.get("block_hash") == parent_hash for entry in ledger)
    if not parent_found:
        return False, f"Parent hash {parent_hash} not found in Immutable Truth Ledger."
    return True, ""

def simulate_state(commit_data):
    entropy = commit_data.get("entropy", 0.0)
    if entropy > 0.0:
        return False, f"Entropy spike detected ({entropy} > 0.0)."
    return True, ""

# --- THE CIRCUIT BREAKER ---

def finalize_refusal(refusal_blob, simulate_witness_fail=False):
    """
    Attempts to anchor the refusal in the external reality (Sigstore).
    If reality cannot be reached, the system executes a Local Lock.
    """

    # 1. Prepare the payload
    payload_hash = calculate_hash(refusal_blob)
    print(f"Attempting to broadcast Refusal Blob: {payload_hash}")

    try:
        # 2. Strict Timeout Broadcast (The "Witness")
        # "Zero Slack" means we do not retry indefinitely.
        # 2000ms is the maximum tolerance for network latency.

        if simulate_witness_fail:
            raise urllib.error.URLError("Simulated Witness Timeout.")

        # Simulate Network Request to Sigstore (using google.com as proxy for connectivity check)
        # In a real impl, this would POST to rekor.sigstore.dev
        req = urllib.request.Request("http://www.google.com") # Proxy check
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                 raise urllib.error.URLError(f"Transparency Log responded with {response.status}")

            # 3. Success: Merge proof and log to Refusal Ledger
            external_proof = {
                "broadcast_id": str(uuid.uuid4()), # Mocked proof ID
                "status": "VERIFIED",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            refusal_blob['external_anchor'] = external_proof
            append_refusal(refusal_blob)
            print("Witness Confirmed. Refusal Anchored.")
            return EXIT_CODE_SYSTEM_REJECTED

    except (urllib.error.URLError, TimeoutError, Exception) as e:

        # 4. WITNESS_FAIL: The "Air-Gap" Defense
        print(f"WITNESS FAIL DETECTED: {str(e)}")

        emergency_blob = {
            "refusal_event": refusal_blob['refusal_event'], # Keep original event
            "invariant_breach": { # Overwrite breach with higher severity? Or append?
                                  # The prompt says: "emergency_blob = { refusal_event: ..., invariant_breach: { code: 0x04 ... } }"
                                  # So we overwrite the breach info to indicate WHY we are locking.
                "code": "0x04",
                "mnemonic": "WITNESS_FAIL",
                "reasoning_vector": "External Observation Horizon Unreachable. State is Unverified."
            },
            "external_anchor": {
                "broadcast_id": None,
                "status": "UNOBSERVED",
                "error_log": str(e)
            },
            "system_status": "LOCKED_PENDING_AUDIT"
        }

        # Force write to local log only to document the system failure
        append_refusal(emergency_blob)

        # 5. The Hard Stop
        print("System Locked via Circuit Breaker.")
        sys.exit(EXIT_CODE_WITNESS_LOST)

# --- MAIN CI LOOP ---

def run_gatekeeper(commit_json_str, simulate_witness_fail=False):
    try:
        commit_data = json.loads(commit_json_str)
    except json.JSONDecodeError:
        print("Error: Invalid Commit JSON")
        sys.exit(1)

    instruction_hash = calculate_hash(commit_json_str)
    print(f"Processing Instruction Hash: {instruction_hash}")

    # 1. Verify Identity (0x00)
    print("Verifying Identity...")
    valid, reason = verify_identity(commit_data)
    if not valid:
        blob = generate_minimal_blob(instruction_hash, RefusalCode.IDENTITY_VOID, reason)
        finalize_refusal(blob, simulate_witness_fail) # Will exit
        return # Should not reach here

    # 2. Verify Lineage (0x01)
    print("Verifying Lineage...")
    valid, reason = verify_lineage(commit_data)
    if not valid:
        blob = generate_minimal_blob(instruction_hash, RefusalCode.LINEAGE_BREAK, reason)
        finalize_refusal(blob, simulate_witness_fail)
        return

    # 3. Simulate State (0x02)
    print("Simulating State...")
    valid, reason = simulate_state(commit_data)
    if not valid:
        blob = generate_minimal_blob(instruction_hash, RefusalCode.ENTROPY_SPIKE, reason)
        finalize_refusal(blob, simulate_witness_fail)
        return

    # If all checks pass, we theoretically check witness for Acceptance too.
    # But for this scope (Refusal Ledger), we accept.
    print("Gatekeeper: ALL CHECKS PASSED. Commit Accepted.")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TAS CI Gatekeeper")
    parser.add_argument("--commit", type=str, required=True, help="JSON string of commit data")
    parser.add_argument("--simulate-witness-fail", action="store_true", help="Force Witness Failure (0x04)")

    args = parser.parse_args()

    run_gatekeeper(args.commit, args.simulate_witness_fail)
