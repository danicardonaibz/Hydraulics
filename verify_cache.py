"""
Simple verification script to confirm caching works correctly.
"""

import time
from hydraulics.core.water_api import WaterAPIClient

print("Testing IAPWS caching...")
print()

# Test 1: Call same temperature twice
print("Test 1: Call same temperature twice (20°C)")
print("-" * 50)

# First call (cache miss)
start = time.perf_counter()
result1 = WaterAPIClient.fetch_properties(20.0)
time1 = time.perf_counter() - start

# Second call (should be cache hit)
start = time.perf_counter()
result2 = WaterAPIClient.fetch_properties(20.0)
time2 = time.perf_counter() - start

print(f"First call: {time1*1000:.3f} ms")
print(f"Second call: {time2*1000:.6f} ms")
print(f"Speedup: {time1/time2:.0f}x")
print(f"Results match: {result1 == result2}")
print()

# Test 2: Check cache info
print("Test 2: Cache statistics")
print("-" * 50)
info = WaterAPIClient.get_cache_info()
print(f"Hits: {info.hits}")
print(f"Misses: {info.misses}")
print(f"Size: {info.currsize}/{info.maxsize}")
print()

# Test 3: Pre-warm and verify
print("Test 3: Pre-warming cache")
print("-" * 50)
WaterAPIClient.clear_cache()
print("Cache cleared")

print("Pre-warming 0-40°C in 5°C steps...")
cached = WaterAPIClient.prewarm_cache(0, 40, 5)
print(f"Cached {cached} temperatures")

info = WaterAPIClient.get_cache_info()
print(f"Cache size: {info.currsize}")
print(f"Cache misses so far: {info.misses}")
print()

# Now test a pre-warmed temperature
print("Testing pre-warmed temperature (20°C)...")
start = time.perf_counter()
result = WaterAPIClient.fetch_properties(20.0)
time_prewarmed = time.perf_counter() - start
print(f"Retrieval time: {time_prewarmed*1000:.6f} ms")

info_after = WaterAPIClient.get_cache_info()
print(f"Cache hits after test: {info_after.hits} (was {info.hits})")
print(f"Cache misses after test: {info_after.misses} (was {info.misses})")

if info_after.hits > info.hits:
    print("SUCCESS: Pre-warmed value retrieved from cache!")
else:
    print("FAIL: Pre-warmed value was not cached")
