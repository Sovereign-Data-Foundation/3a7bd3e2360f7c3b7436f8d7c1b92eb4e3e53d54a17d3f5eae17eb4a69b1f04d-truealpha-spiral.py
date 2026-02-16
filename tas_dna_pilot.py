
class ERTriagePilot:
    def __init__(self):
        # Baseline distribution: Emergent 30%, Urgent 50%, Non-Urgent 20%
        self.baseline = {
            'Emergent': 0.3,
            'Urgent': 0.5,
            'Non-Urgent': 0.2
        }
        # Optimization: Pre-compute items list for faster iteration
        self.baseline_items = list(self.baseline.items())

        # Optimized: Use pre-initialized dict instead of defaultdict for faster access
        self.current_counts = {k: 0 for k in self.baseline}
        self.total_patients = 0
        self.history = [] # To store deltas (categories) for rollback (Phoenix Protocol)
        self.attested_history_length = 0

        # New State: Track drift incrementally for O(1) read access
        self.current_drift = 0.0

    def _recalculate_drift(self):
        """
        Internal helper to update the drift metric.
        Called after any change to current_counts or total_patients.
        """
        if self.total_patients == 0:
            self.current_drift = 0.0
            return

        inv_total = 1.0 / self.total_patients
        counts = self.current_counts
        l1_distance = 0.0

        # Optimization: Iterate over pre-computed list
        for category, baseline_prob in self.baseline_items:
            current_prob = counts[category] * inv_total
            l1_distance += abs(current_prob - baseline_prob)

        self.current_drift = 0.5 * l1_distance

    def admit_patient(self, category):
        # Safety Fix: Check current_counts, not baseline.
        # This protects against KeyError if baseline is mutated after init but counts are not.
        if category not in self.current_counts:
            raise ValueError(f"Invalid category or uninitialized baseline key: {category}")

        # Save delta for potential rollback
        self.history.append(category)

        self.current_counts[category] += 1
        self.total_patients += 1

        # Update drift state immediately (Write-heavy optimization)
        self._recalculate_drift()

    def get_current_distribution(self):
        if self.total_patients == 0:
            return {k: 0 for k in self.baseline}
        return {k: v / self.total_patients for k, v in self.current_counts.items()}

    def calculate_drift(self):
        """
        Returns the current drift using the pre-calculated state.
        This is now an O(1) operation.
        """
        return self.current_drift

    def check_integrity(self, threshold=0.1):
        """
        Checks if the drift exceeds the threshold.
        If it does, triggers the Phoenix Protocol (rollback).
        """
        # Optimized: O(1) lookup
        drift = self.current_drift
        if drift > threshold:
            print(f"Drift detected ({drift} > {threshold}). Initiating Phoenix Protocol.")
            self.phoenix_protocol()
            return False

        # Mark current state as attested
        self.attested_history_length = len(self.history)
        return True

    def phoenix_protocol(self):
        """
        Reverts to the last attested state by undoing changes back to the
        last verified checkpoint. This ensures robust rollback beyond just
        the immediate previous state.
        """
        print(f"Initiating Phoenix Protocol... Rolling back from {len(self.history)} to {self.attested_history_length}")

        while len(self.history) > self.attested_history_length:
            category = self.history.pop()
            self.current_counts[category] -= 1
            self.total_patients -= 1

        print("System reverted to last attested state.")
        # Recalculate drift after rollback
        self._recalculate_drift()
