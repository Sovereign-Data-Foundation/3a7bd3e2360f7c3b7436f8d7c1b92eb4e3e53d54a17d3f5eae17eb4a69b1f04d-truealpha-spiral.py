import collections

class ERTriagePilot:
    def __init__(self):
        # Baseline distribution: Emergent 30%, Urgent 50%, Non-Urgent 20%
        self.baseline = {
            'Emergent': 0.3,
            'Urgent': 0.5,
            'Non-Urgent': 0.2
        }
        self.current_counts = collections.defaultdict(int)
        self.total_patients = 0
        self.history = [] # To store snapshots for rollback (Phoenix Protocol)

    def admit_patient(self, category):
        if category not in self.baseline:
            raise ValueError(f"Invalid category: {category}")

        # Save state for potential rollback
        self.history.append(category)

        self.current_counts[category] += 1
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
            current_prob = self.current_counts.get(category, 0) / self.total_patients
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
        return True

    def phoenix_protocol(self):
        """
        Reverts to the last attested state.
        (Simplified for this pilot: just undoes the last addition)
        """
        if self.history:
            category = self.history.pop()
            self.current_counts[category] -= 1
            self.total_patients -= 1
            print("System reverted to previous state.")
