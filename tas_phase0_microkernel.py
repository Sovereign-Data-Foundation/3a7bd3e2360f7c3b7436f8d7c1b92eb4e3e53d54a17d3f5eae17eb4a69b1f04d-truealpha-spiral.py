"""Phase 0 Micro Kernel Boot for TrueAlphaSpiral.

This module is intentionally small, deterministic, and dependency-free.
It establishes the first executable boundary condition for TAS_DNA-style
verification: normalize the boot manifest, hash it, and refuse execution
when the manifest is malformed or below the minimum coherence threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict, Tuple

PHASE = "PHASE_0_MICRO_KERNEL_BOOT"
MINIMUM_COHERENCE = 1.0
BOOT_STATUS = "BOOTSTRAP_LOCKED"
REFUSAL_STATUS = "BOOTSTRAP_REFUSED"


@dataclass(frozen=True)
class Phase0Manifest:
    """Canonical boot manifest for the Phase 0 kernel."""

    phase: str
    steward: str
    invariant: str
    coherence: float
    no_attestation_no_execution: bool = True

    def validate(self) -> None:
        """Fail closed when the boot manifest violates the boundary."""
        if self.phase != PHASE:
            raise ValueError("phase mismatch")
        if not self.steward.strip():
            raise ValueError("missing steward")
        if not self.invariant.strip():
            raise ValueError("missing invariant")
        if self.coherence < MINIMUM_COHERENCE:
            raise ValueError("coherence below boot threshold")
        if not self.no_attestation_no_execution:
            raise ValueError("attestation gate disabled")

    def canonical_bytes(self) -> bytes:
        """Return RFC-8785-style stable JSON bytes for hashing."""
        payload = asdict(self)
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def anchor_hash(self) -> str:
        """Compute the deterministic boot anchor."""
        return sha256(self.canonical_bytes()).hexdigest()


def boot_microkernel(manifest: Phase0Manifest) -> Dict[str, Any]:
    """Validate and seal the Phase 0 boot state.

    Returns a receipt-shaped dictionary that can be committed to an ITL-like
    append-only record. Any invalid manifest is refused before hashing.
    """
    try:
        manifest.validate()
    except ValueError as exc:
        return {
            "status": REFUSAL_STATUS,
            "reason": str(exc),
            "phase": manifest.phase,
        }

    return {
        "status": BOOT_STATUS,
        "phase": manifest.phase,
        "anchor_hash": manifest.anchor_hash(),
        "canonical_manifest": manifest.canonical_bytes().decode("utf-8"),
    }


def default_manifest() -> Phase0Manifest:
    """The minimal living boot condition for TAS Phase 0."""
    return Phase0Manifest(
        phase=PHASE,
        steward="Russell Nordland / TrueAlphaSpiral",
        invariant="No attestation -> no execution",
        coherence=1.0,
    )


def main() -> Tuple[str, str]:
    """CLI-friendly boot entrypoint."""
    receipt = boot_microkernel(default_manifest())
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return receipt["status"], receipt.get("anchor_hash", "")


if __name__ == "__main__":
    main()
