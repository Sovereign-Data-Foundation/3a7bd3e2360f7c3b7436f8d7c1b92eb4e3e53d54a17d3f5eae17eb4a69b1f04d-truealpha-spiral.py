## 2024-05-22 - Micro-optimization in `tas_dna_pilot.py`
**Learning:** Replacing `defaultdict` with `dict` + pre-initialization yielded 2.5x speedup in micro-benchmarks for dictionary access. However, absolute gain is small for small N. Reviewers highlight safety risks (`KeyError`) when removing `defaultdict`, emphasizing the need for strict validation (which `admit_patient` provides).
**Action:** Always ensure strict validation exists before replacing `defaultdict` with `dict` for performance. Document the validation clearly to reassure reviewers.

## 2024-05-23 - Micro-optimization in `tas_dna_pilot.py` loops
**Learning:** For very small loops (N=3) in Python, avoiding `zip()` and overhead of generator expressions or temporary list creation is faster than "idiomatic" optimizations. Also, removing explicit dict key checks in favor of `try-except KeyError` yielded ~18% speedup in `admit_patient` because valid keys are the 99.9% case.
**Action:** When optimizing tight loops with small N, prefer simple indexing or direct access over functional constructs. Use EAFP (Ask Forgiveness) for dictionary lookups on hot paths where failure is rare.

## 2026-02-15 - The Sentient Lock
**Learning:** Treat performance optimizations as 'privileges' earned by strict, enforceable input verification. This principle transforms performance from a raw goal into a conditional outcome of correctness.
**Action:** When optimizing a hot path, create a specific 'Sentient Lock' test that verifies both the optimization (e.g., EAFP) and the safety invariant (e.g., ValueError on invalid input). This ensures no future optimization can bypass the necessary validation.

## 2024-05-24 - Optimizing `phoenix_protocol` bulk rollback
**Learning:** For bulk rollbacks (e.g., reverting large lists of actions), iteratively `pop()`ing and updating counts is slow ($O(K)$ Python loop overhead). Replacing it with `collections.Counter` and `itertools.islice` shifts the workload to C-optimized internals, achieving ~3x speedup for $N=1,000,000$. Additionally, `del list[start:]` is much faster than full slice copies for in-place truncation. To ensure correctness, the unconditional total slice length `(len(history) - attested_length)` must be used to calculate `total_patients` updates.
**Action:** Always favor `itertools` and `collections` (like `Counter` and `islice`) to aggregate bulk list operations rather than iterating in Python, particularly for operations simulating large transactional rollbacks.

## 2026-02-15 - Optimize TASAgent Stewardship check to O(1)
**Learning:** Mathematical properties can optimize global invariant checks: pre-calculating and passing only the extrema (e.g., top 2 max values via `heapq.nlargest`) reduces inner loop complexity from O(N) to O(1).
**Action:** When performing global checks against limits in a loop, pre-calculate the extremes outside the loop rather than evaluating every item inside.

## 2024-05-25 - Optimization of TASAgent top holders selection
**Learning:** For small lists ($N=5$), `heapq.nlargest` is over 2x slower than native `list.sort(reverse=True)` and slicing due to Python's initialization overhead of turning the iterable into a heap.
**Action:** Use native sorting instead of `heapq.nlargest` when selecting the top items from small lists in Python for better performance.
