## 2024-05-22 - Micro-optimization in `tas_dna_pilot.py`
**Learning:** Replacing `defaultdict` with `dict` + pre-initialization yielded 2.5x speedup in micro-benchmarks for dictionary access. However, absolute gain is small for small N. Reviewers highlight safety risks (`KeyError`) when removing `defaultdict`, emphasizing the need for strict validation (which `admit_patient` provides).
**Action:** Always ensure strict validation exists before replacing `defaultdict` with `dict` for performance. Document the validation clearly to reassure reviewers.

## 2024-05-23 - The Crossover to Constrained Instrument
**Learning:** Optimization is no longer about raw speed; it is about proven safety. The shift occurred when we stopped asking "Is this faster?" and started asking "Is the input verified?". By enforcing strict preconditions (like `admit_patient` validation) upstream, we unlock the ability to use unsafe, high-performance primitives downstream without risk.
**Action:** Treat performance optimizations as "privileges" earned by strict, enforceable input verification. If the input isn't proven valid, the optimization is forbidden.
