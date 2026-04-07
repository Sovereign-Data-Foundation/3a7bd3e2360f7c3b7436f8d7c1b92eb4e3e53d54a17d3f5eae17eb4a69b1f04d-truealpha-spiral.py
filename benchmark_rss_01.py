import timeit
import io
import sys
from rss_01_simulation import SimulationEnvironment

if __name__ == '__main__':
    # benchmark without verbose param
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        t_optimized = timeit.timeit("sim = SimulationEnvironment(); sim.run(verbose=False)", globals=globals(), number=1000)
    finally:
        sys.stdout = original_stdout

    print(f"Optimized (1000 runs, verbose=False): {t_optimized:.4f}s")
