import collections
import itertools

class ERTriagePilot:
    def __init__(self):
        # Baseline distribution: Emergent 30%, Urgent 50%, Non-Urgent 20%
        self.baseline = {
            'Emergent': 0.3,
            'Urgent': 0.5,
            'Non-Urgent': 0.2
        }
        # Optimized: Use pre-initialized dict instead of defaultdict for faster access
        self.current_counts = {k: 0 for k in self.baseline}
        self.total_patients = 0
        self.history = [] # To store deltas (categories) for rollback (Phoenix Protocol)
        self.attested_history_length = 0

    def admit_patient(self, category):
        # Optimization: Use EAFP (try-except) to avoid redundant key lookup.
        # This is faster than 'if category not in self.baseline' for valid inputs.
        try:
            self.current_counts[category] += 1
        except KeyError:
            raise ValueError(f"Invalid category: {category}")

        # Save delta for potential rollback
        self.history.append(category)
        self.total_patients += 1

    def get_current_distribution(self):
        if self.total_patients == 0:
            return {k: 0 for k in self.baseline}
        return {k: v / self.total_patients for k, v in self.current_counts.items()}

    def calculate_drift(self):
        """
        Calculates the drift using Total Variation Distance (TVD) between
        the current distribution and the baseline.
        TVD(P, Q) = 0.5 * sum(|P(x) - Q(x)|)
        """
        if self.total_patients == 0:
            return 0.0

        # TVD = 0.5 * sum(|P(x) - Q(x)|)
        l1_distance = 0.0
        for category, baseline_prob in self.baseline.items():
            # Optimized: Direct dict access is faster than .get()
            current_prob = self.current_counts[category] / self.total_patients
            l1_distance += abs(current_prob - baseline_prob)

        return 0.5 * l1_distance

    def check_integrity(self, threshold=0.1):
        """
        Checks if the drift exceeds the threshold.
        If it does, triggers the Phoenix Protocol (rollback).
        """
        drift = self.calculate_drift()
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
        current_len = len(self.history)
        target_len = self.attested_history_length

        if current_len <= target_len:
            return

        print(f"Initiating Phoenix Protocol... Rolling back from {current_len} to {target_len}")

        # Slice the history to get the items to be removed
        # Optimization: Use islice to avoid list copy
        rollback_slice = itertools.islice(self.history, target_len, None)

        # Count occurrences in the slice efficiently
        rollback_counts = collections.Counter(rollback_slice)

        # Subtract counts from current_counts
        for category, count in rollback_counts.items():
            self.current_counts[category] -= count

        # Update total_patients
        self.total_patients -= (current_len - target_len)

        # Truncate history in place
        del self.history[target_len:]

        print("System reverted to last attested state.")
