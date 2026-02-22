
import timeit
import collections

# Setup
baseline = {'Emergent': 0.3, 'Urgent': 0.5, 'Non-Urgent': 0.2}
current_counts = {k: 0 for k in baseline}

def admit_eafp(category):
    try:
        current_counts[category] += 1
    except KeyError:
        pass # Simulate handling

def admit_lbyl(category):
    if category in current_counts:
        current_counts[category] += 1
    else:
        pass # Simulate handling

def benchmark():
    # 1. Happy Path (100% valid)
    valid_cat = 'Emergent'
    t_eafp_valid = timeit.timeit(lambda: admit_eafp(valid_cat), number=1_000_000)
    t_lbyl_valid = timeit.timeit(lambda: admit_lbyl(valid_cat), number=1_000_000)

    print(f"Happy Path (1M ops):")
    print(f"EAFP: {t_eafp_valid:.4f}s")
    print(f"LBYL: {t_lbyl_valid:.4f}s")
    print(f"Ratio: {t_lbyl_valid / t_eafp_valid:.2f}x (LBYL/EAFP)")

    # 2. Attack Path (100% invalid)
    invalid_cat = 'Invalid'
    t_eafp_invalid = timeit.timeit(lambda: admit_eafp(invalid_cat), number=1_000_000)
    t_lbyl_invalid = timeit.timeit(lambda: admit_lbyl(invalid_cat), number=1_000_000)

    print(f"\nAttack Path (1M ops):")
    print(f"EAFP: {t_eafp_invalid:.4f}s")
    print(f"LBYL: {t_lbyl_invalid:.4f}s")
    print(f"Speedup: {t_eafp_invalid / t_lbyl_invalid:.2f}x")

if __name__ == "__main__":
    benchmark()
