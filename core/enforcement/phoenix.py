from typing import List, Dict, Any, Optional

class PhoenixProtocol:
    """
    The Phoenix Protocol.
    Handles 'Low-Entropy Restoration' by pruning divergent logic trees and reverting
    to the Last Invariant-Compliant State.
    """

    @staticmethod
    def initiate_rollback(state_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Prunes the divergent state (the last one) and returns the previous compliant state.

        Args:
            state_history: The list of historical states/decisions.

        Returns:
            The restored state (Dict) or None if history is empty.
        """
        if not state_history:
            print("PHOENIX: No history to rollback.")
            return None

        # The last state caused the trigger (Drift/Mutiny).
        # We prune it (The Burn).
        bad_state = state_history.pop()
        print(f"PHOENIX: Pruning divergent state from timestamp {bad_state.get('timestamp')}")

        # In a complex system, we might need to restore 'system parameters' from the previous state.
        # Here we return the new 'last' state as the anchor.
        if state_history:
            restored_state = state_history[-1]
            print(f"PHOENIX: Rollback complete. System restored to state at {restored_state.get('timestamp')}")
            return restored_state
        else:
            print("PHOENIX: System reset to Genesis state (empty history).")
            return None
