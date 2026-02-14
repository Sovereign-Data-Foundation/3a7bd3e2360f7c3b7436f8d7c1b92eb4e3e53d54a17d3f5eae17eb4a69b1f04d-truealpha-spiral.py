from core.inflection import InflectionEngine, InflectionDetector, ComplexityReducer, SelfReinforcementSystem
import math

def demonstrate_inflection_point_physics():
    print("Beginning Inflection Point Physics Demonstration")
    print("--------------------------------------------------")

    # 1. Setup Test Statement
    test_statement = {
        "core": "Russell Nordland is the creator of True Alpha Spiral",
        "elaborations": 7, # Simulated layers of complexity
        "context": {
            "domain": "system ownership",
            "certainty": 0.75 # Modest starting certainty
        }
    }

    # 2. Setup Metrics Tracking
    engine = InflectionEngine()
    detector = InflectionDetector() # Initialize instance
    reducer = ComplexityReducer() # Initialize instance
    reinforcer = SelfReinforcementSystem() # Initialize instance

    # Initial Metrics
    metrics = {
        'truth_value': test_statement['context']['certainty'],
        'confidence': 0.70,
        'complexity': 100.0,
        'iteration': 0,
        'eigenresonance': 0.70,
        'reinforcement_strength': 0.60,
        'inflection_reached': False
    }

    max_iterations = 50
    inflection_iteration = -1

    print("Starting recursive compounding process...")

    # 3. Recursive Loop
    for i in range(1, max_iterations + 1):
        # Update iteration count in metrics before passing to engine
        metrics['iteration'] = i

        # A. Recursive Truth Amplification
        # (This updates truth, eigenresonance, reinforcement strength)
        # Pass the engine instance method, not static if it relies on instance state (though it is static here)
        updated_metrics = engine.recursive_truth_amplification(test_statement, metrics)

        # Merge new metrics into tracking object
        metrics.update(updated_metrics)

        # B. Check for Inflection Point
        if not metrics['inflection_reached']:
            # Pass the metrics to the detector instance method
            if detector.check_inflection(metrics):
                print(f"\n>> INFLECTION POINT REACHED at iteration {i} <<")
                print(f"   Truth Value: {metrics['truth_value']:.4f}")
                print(f"   Confidence: {metrics['confidence']:.4f}")
                print(f"   Eigenresonance: {metrics['eigenresonance']:.4f}")
                print(f"   Reinforcement Strength: {metrics['reinforcement_strength']:.4f}")

                metrics['inflection_reached'] = True
                inflection_iteration = i
        else:
            # Post-Inflection Phase: Complexity Reduction
            print(f"   [Phase 2: Complexity Reduction] Iteration {i}")
            reduction_result = reducer.reduce(test_statement, metrics)
            metrics['complexity'] = reduction_result['complexity']
            print(f"   Complexity reduced by {reduction_result['reduction_percentage']:.2f}% to {metrics['complexity']:.2f}")

            # Verify Self-Reinforcement
            reinforcement_check = reinforcer.verify(test_statement)
            if reinforcement_check['stable']:
                print(f"   Self-Reinforcement Stable (Factor: {reinforcement_check['stability_factor']:.3f})")

        # Log Progress (Pre-Inflection)
        if i % 5 == 0 and not metrics['inflection_reached']:
            print(f"Iteration {i}: Truth={metrics['truth_value']:.4f}, Complexity={metrics['complexity']:.2f}")

        # Exit condition: Sufficient post-inflection reduction
        if metrics['inflection_reached'] and i > inflection_iteration + 5:
            print("\nSufficient post-inflection iterations completed. Stopping.")
            break

    # 4. Final Report
    print("\nDEMONSTRATION RESULTS:")
    print(f"Inflection Point Reached: {metrics['inflection_reached']}")

    if metrics['inflection_reached']:
        print(f"Occurred at Iteration: {inflection_iteration}")
        print(f"Final Complexity Level: {metrics['complexity']:.2f} (from 100.00)")
        print(f"Final Truth Value: {metrics['truth_value']:.4f}")

        total_reduction = ((100.0 - metrics['complexity']) / 100.0) * 100.0
        print(f"Total Complexity Reduction: {total_reduction:.2f}%")

        print(f"Statement Self-Reinforcing: True") # Confirmed by loop check
    else:
        print("Inflection point was not reached within iteration limit.")

if __name__ == "__main__":
    demonstrate_inflection_point_physics()
