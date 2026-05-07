import sys
import json
import hashlib
import time
import os

def sha256(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <claim.json>")
        sys.exit(1)

    claim_file = sys.argv[1]
    with open(claim_file, 'r') as f:
        claim_content = f.read()
        claim = json.loads(claim_content)

    # 1. Lodge -> Witness (receipt)
    claim_hash = sha256(claim_content)
    # A simplified manifest_hash and scope_hash for demonstration
    manifest_hash = sha256("manifest_v1")
    scope_hash = sha256(claim.get("allowed_scope", ""))

    witness_receipt = {
        "claim_hash": claim_hash,
        "manifest_hash": manifest_hash,
        "scope_hash": scope_hash,
        "timestamp": int(time.time())
    }

    os.makedirs("receipts", exist_ok=True)
    with open("receipts/sdf_witness.json", "w") as f:
        json.dump(witness_receipt, f, indent=2)
    print("Generated: receipts/sdf_witness.json")

    # 2. Compute -> Outcomes
    allowed_scope = claim.get("allowed_scope")

    # Process requests
    os.makedirs("outputs", exist_ok=True)

    requests_to_process = [
        ("requests/compute.json", "outputs/execution_receipt.json"),
        ("requests/compute_out_of_scope.json", "outputs/refusal_receipt.json")
    ]

    for req_file, out_file in requests_to_process:
        if not os.path.exists(req_file):
            print(f"File {req_file} not found.")
            continue

        with open(req_file, 'r') as f:
            req = json.load(f)

        # Invariant: Out-of-scope -> refuse
        if req.get("scope") != allowed_scope:
            receipt = {
                "status": "TAS_REFUSAL_RECEIPT",
                "request_id": req.get("request_id"),
                "reason": "Out-of-scope -> refuse"
            }
        else:
            receipt = {
                "status": "TAS_EXECUTION_RECEIPT",
                "request_id": req.get("request_id"),
                "claim_hash": claim_hash
            }

        with open(out_file, "w") as f:
            json.dump(receipt, f, indent=2)
        print(f"Generated: {out_file}")

if __name__ == "__main__":
    main()
