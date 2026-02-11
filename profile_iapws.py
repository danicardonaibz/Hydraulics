"""
Profiling script to measure IAPWS water property retrieval performance.

This script measures the time taken to retrieve water properties at various
temperatures to identify performance bottlenecks before implementing caching.
"""

import time
import statistics
from hydraulics.core.water_api import WaterAPIClient


def profile_single_call(temperature):
    """Profile a single IAPWS call"""
    start = time.perf_counter()
    result = WaterAPIClient.fetch_properties(temperature)
    elapsed = time.perf_counter() - start
    return elapsed, result


def profile_multiple_calls(temperatures, iterations=5):
    """Profile multiple calls at various temperatures"""
    print("=" * 80)
    print("IAPWS PERFORMANCE PROFILING - BEFORE OPTIMIZATION")
    print("=" * 80)
    print()

    all_times = []

    for temp in temperatures:
        times = []
        print(f"Temperature: {temp} deg C")

        for i in range(iterations):
            elapsed, result = profile_single_call(temp)
            times.append(elapsed)
            if i == 0:  # Print result details only once
                print(f"  Source: {result['source']}")
                print(f"  Density: {result['density']:.2f} kg/m^3")
                print(f"  Kinematic viscosity: {result['kinematic_viscosity']:.6e} m^2/s")

        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        all_times.extend(times)

        print(f"  Time (avg): {avg_time*1000:.3f} ms")
        print(f"  Time (min): {min_time*1000:.3f} ms")
        print(f"  Time (max): {max_time*1000:.3f} ms")
        print()

    # Overall statistics
    print("=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)
    print(f"Total calls: {len(all_times)}")
    print(f"Average time: {statistics.mean(all_times)*1000:.3f} ms")
    print(f"Median time: {statistics.median(all_times)*1000:.3f} ms")
    print(f"Min time: {min(all_times)*1000:.3f} ms")
    print(f"Max time: {max(all_times)*1000:.3f} ms")
    print(f"Std deviation: {statistics.stdev(all_times)*1000:.3f} ms")
    print()

    # Check if target is met
    avg_ms = statistics.mean(all_times) * 1000
    if avg_ms < 1.0:
        print(f"TARGET MET: Average time ({avg_ms:.3f} ms) is sub-millisecond")
    else:
        print(f"TARGET NOT MET: Average time ({avg_ms:.3f} ms) exceeds 1 ms")
        print(f"Speedup needed: {avg_ms:.1f}x")
    print()


if __name__ == "__main__":
    # Test temperatures: Common range for irrigation (5°C intervals)
    # Plus some edge cases
    test_temperatures = [5, 10, 15, 20, 25, 30, 35, 40]

    print("Starting IAPWS performance profiling...")
    print(f"Testing {len(test_temperatures)} temperatures with 5 iterations each")
    print()

    profile_multiple_calls(test_temperatures, iterations=5)
