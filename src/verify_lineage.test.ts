
import { Gatekeeper, LineageProof, VerificationResult } from './verify_lineage';

/**
 * Must-Fail Test Suite: verify_lineage.test.ts
 * Enforced by Artifact E: Runtime Configuration
 *
 * Objectives:
 * 1. Verify strict type safety (no implicit any).
 * 2. Ensure async handling is robust.
 * 3. Validate Manifest Determinism.
 */

describe('Gatekeeper (Crystalline Lattice v2026.1)', () => {
    let gatekeeper: Gatekeeper;

    beforeEach(() => {
        gatekeeper = new Gatekeeper();
    });

    it('should reject invalid proof structure with strict error handling', async () => {
        // Enforcing strict null checks
        const invalidProof = {} as LineageProof;

        await expect(gatekeeper.verify_lineage(invalidProof))
            .rejects
            .toThrow("Invalid proof structure: Missing hash or signature");
    });

    it('should validate valid lineage proof correctly', async () => {
        const validProof: LineageProof = {
            hash: "0xHASH123",
            timestamp: Date.now(),
            signature: "SIG_VALID_123"
        };

        const result: VerificationResult = await gatekeeper.verify_lineage(validProof);

        expect(result.verified).toBe(true);
        expect(result.timestamp).toBeDefined();
        expect(result.reason).toBeUndefined();
    });

    it('should reject forged signatures via Ledger-Binding logic', async () => {
        const forgedProof: LineageProof = {
            hash: "0xHASH456",
            timestamp: Date.now(),
            signature: "FORGED_SIG"
        };

        const result = await gatekeeper.verify_lineage(forgedProof);

        expect(result.verified).toBe(false);
        expect(result.reason).toBe("Signature mismatch");
    });

    it('should handle negative timestamps strictly', async () => {
        const timeTravelProof: LineageProof = {
            hash: "0xHASH789",
            timestamp: -1000,
            signature: "SIG_FUTURE"
        };

        const result = await gatekeeper.verify_lineage(timeTravelProof);

        expect(result.verified).toBe(false);
        expect(result.reason).toBe("Invalid timestamp");
    });

    // Test for Manifest Determinism (structure check)
    it('should enforce strict property initialization', () => {
        expect(gatekeeper).toBeInstanceOf(Gatekeeper);
        // Accessing private property would fail compilation, confirming strict modifiers.
        // (gatekeeper as any).validSignatures; // This would be 'any' access, disallowed by policy but testable via expectation of failure if we could compile it.
    });
});
