"""
Profiling script to measure IAPWS water property retrieval performance WITH CACHING.

This script measures the performance improvement achieved by implementing
LRU caching for water property retrieval.
"""

import time
import statistics
from hydraulics.core.water_api import WaterAPIClient


def profile_cached_performance():
    """Profile performance with cache enabled"""
    print("=" * 80)
    print("IAPWS PERFORMANCE PROFILING - AFTER OPTIMIZATION (WITH CACHE)")
    print("=" * 80)
    print()

    # Test temperatures: Common range for irrigation (5°C intervals)
    test_temperatures = [5, 10, 15, 20, 25, 30, 35, 40]

    # Phase 1: First call (cache miss) - will be slow
    print("PHASE 1: Initial calls (cache misses)")
    print("-" * 80)
    first_call_times = []
    for temp in test_temperatures:
        start = time.perf_counter()
        result = WaterAPIClient.fetch_properties(temp)
        elapsed = time.perf_counter() - start
        first_call_times.append(elapsed)
        print(f"  {temp} deg C: {elapsed*1000:.3f} ms (source: {result['source']})")
    print()

    # Phase 2: Repeated calls (cache hits) - should be extremely fast
    print("PHASE 2: Repeated calls (cache hits)")
    print("-" * 80)
    iterations = 1000  # Many iterations to measure sub-millisecond times accurately
    cached_times = []

    for temp in test_temperatures:
        start = time.perf_counter()
        for _ in range(iterations):
            WaterAPIClient.fetch_properties(temp)
        elapsed = time.perf_counter() - start
        avg_time = elapsed / iterations
        cached_times.append(avg_time)
        print(f"  {temp} deg C: {avg_time*1000:.6f} ms (avg of {iterations} calls)")
    print()

    # Phase 3: Cache statistics
    print("PHASE 3: Cache statistics")
    print("-" * 80)
    cache_info = WaterAPIClient.get_cache_info()
    total_calls = cache_info.hits + cache_info.misses
    hit_rate = (cache_info.hits / total_calls * 100) if total_calls > 0 else 0
    print(f"  Cache hits: {cache_info.hits}")
    print(f"  Cache misses: {cache_info.misses}")
    print(f"  Cache size: {cache_info.currsize} / {cache_info.maxsize}")
    print(f"  Hit rate: {hit_rate:.1f}%")
    print()

    # Phase 4: Performance summary
    print("=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    avg_first_call = statistics.mean(first_call_times) * 1000
    avg_cached = statistics.mean(cached_times) * 1000

    print(f"First call (cache miss): {avg_first_call:.3f} ms")
    print(f"Cached call (cache hit): {avg_cached:.6f} ms")
    print(f"Speedup factor: {avg_first_call / avg_cached:.0f}x")
    print()

    # Check if target is met
    if avg_cached < 1.0:
        print(f"TARGET MET: Cached retrieval ({avg_cached:.6f} ms) is sub-millisecond!")
        print(f"Performance gain: {(1.0 - avg_cached):.6f} ms below 1ms target")
    else:
        print(f"TARGET NOT MET: Cached retrieval ({avg_cached:.3f} ms) exceeds 1 ms")
    print()

    # Phase 5: Test with pre-warming
    print("=" * 80)
    print("TESTING PRE-WARMING FUNCTIONALITY")
    print("=" * 80)
    WaterAPIClient.clear_cache()
    print("Cache cleared.")

    start = time.perf_counter()
    cached_count = WaterAPIClient.prewarm_cache(0, 40, 5)
    elapsed = time.perf_counter() - start
    print(f"Pre-warmed cache with {cached_count} temperatures (0-40°C, 5°C step)")
    print(f"Pre-warming time: {elapsed*1000:.1f} ms")

    cache_info = WaterAPIClient.get_cache_info()
    print(f"Cache size after pre-warming: {cache_info.currsize}")
    print()

    # Test that pre-warmed values are now cached
    print("Testing pre-warmed values (should be instant):")
    prewarm_times = []
    for temp in [0, 10, 20, 30, 40]:
        start = time.perf_counter()
        WaterAPIClient.fetch_properties(temp)
        elapsed = time.perf_counter() - start
        prewarm_times.append(elapsed)
        print(f"  {temp} deg C: {elapsed*1000:.6f} ms")

    avg_prewarm = statistics.mean(prewarm_times) * 1000
    print(f"Average pre-warmed retrieval: {avg_prewarm:.6f} ms")
    print()


if __name__ == "__main__":
    print("Starting IAPWS performance profiling WITH CACHING...")
    print()
    profile_cached_performance()
    print("Profiling complete!")
