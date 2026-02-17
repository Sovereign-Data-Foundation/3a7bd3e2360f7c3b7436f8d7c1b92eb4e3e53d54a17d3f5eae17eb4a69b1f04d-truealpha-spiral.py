
import timeit

def baseline(requests, c_pool, total_requested):
    allocated_total = 0
    # Simulating the loop body
    for i, amount in requests:
        allocation = int(amount * (c_pool / total_requested))
        allocated_total += allocation
    return allocated_total

def optimized_int(requests, c_pool, total_requested):
    allocated_total = 0
    # Simulating the loop body
    if total_requested > 0:
        for i, amount in requests:
            allocation = (amount * c_pool) // total_requested
            allocated_total += allocation
    return allocated_total

def run_benchmark():
    num_requests = 10000
    requests = [(i, 10) for i in range(num_requests)]
    c_pool = 50000
    total_requested = sum(r[1] for r in requests) # 100000

    # Verify correctness
    base_res = baseline(requests, c_pool, total_requested)
    opt_int_res = optimized_int(requests, c_pool, total_requested)

    assert base_res == opt_int_res, f"Mismatch: {base_res} != {opt_int_res}"

    print(f"Benchmarking with {num_requests} requests...")

    number = 1000
    t_base = timeit.timeit(lambda: baseline(requests, c_pool, total_requested), number=number)
    t_int = timeit.timeit(lambda: optimized_int(requests, c_pool, total_requested), number=number)

    print(f"Baseline (Float Div): {t_base:.4f}s")
    print(f"Optimized (Int Div):  {t_int:.4f}s")

    speedup = t_base / t_int
    print(f"Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    run_benchmark()
