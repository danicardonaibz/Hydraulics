"""Performance benchmark tests for IAPWS caching"""

import time
import pytest
from hydraulics.core.water_api import WaterAPIClient


class TestIAPWSPerformance:
    """Test IAPWS caching performance"""

    def test_cache_warmup(self):
        """Test cache pre-warming"""
        # Clear cache first
        WaterAPIClient.clear_cache()

        # Pre-warm cache
        cached_count = WaterAPIClient.prewarm_cache(0, 40, 5)

        # Should cache 0, 5, 10, 15, 20, 25, 30, 35, 40 = 9 temperatures
        assert cached_count == 9, f"Expected 9 cached temperatures, got {cached_count}"

        # Check cache info
        cache_info = WaterAPIClient.get_cache_info()
        assert cache_info.currsize == 9, f"Cache size should be 9, got {cache_info.currsize}"

    def test_cache_hit_performance(self):
        """Test that cached retrievals are <1ms"""
        # Clear cache
        WaterAPIClient.clear_cache()

        # First call (cache miss) - will be slow
        _ = WaterAPIClient.fetch_properties(20.0)

        # Subsequent calls (cache hits) - should be very fast
        times = []
        for _ in range(100):
            start = time.perf_counter()
            _ = WaterAPIClient.fetch_properties(20.0)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        # Average time should be < 1ms for cached values
        avg_time_ms = sum(times) / len(times)
        max_time_ms = max(times)

        print(f"\n   Cached retrieval performance:")
        print(f"   Average: {avg_time_ms:.6f} ms")
        print(f"   Max: {max_time_ms:.6f} ms")
        print(f"   Min: {min(times):.6f} ms")

        assert avg_time_ms < 1.0, f"Average cached time should be <1ms, got {avg_time_ms:.3f}ms"
        assert max_time_ms < 2.0, f"Max cached time should be <2ms, got {max_time_ms:.3f}ms"

    def test_cache_hit_rate(self):
        """Test cache hit rate in typical usage"""
        # Clear cache
        WaterAPIClient.clear_cache()

        # Simulate typical irrigation calculation - same temperature repeated
        temperatures = [20.0] * 100  # Same temp 100 times

        for temp in temperatures:
            _ = WaterAPIClient.fetch_properties(temp)

        # Check cache statistics
        cache_info = WaterAPIClient.get_cache_info()
        hit_rate = cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0

        print(f"\n   Cache statistics:")
        print(f"   Hits: {cache_info.hits}")
        print(f"   Misses: {cache_info.misses}")
        print(f"   Hit rate: {hit_rate:.1%}")

        # Hit rate should be 99% (1 miss, 99 hits)
        assert hit_rate >= 0.99, f"Cache hit rate should be >=99%, got {hit_rate:.1%}"

    def test_multiple_temperatures_cache(self):
        """Test cache with multiple temperatures"""
        # Clear cache
        WaterAPIClient.clear_cache()

        # Use 10 different temperatures, repeat each 10 times
        temperatures = []
        for temp in range(10, 50, 4):  # 10, 14, 18, 22, 26, 30, 34, 38, 42, 46
            temperatures.extend([float(temp)] * 10)

        for temp in temperatures:
            _ = WaterAPIClient.fetch_properties(temp)

        # Check cache statistics
        cache_info = WaterAPIClient.get_cache_info()

        print(f"\n   Multi-temperature cache stats:")
        print(f"   Cache size: {cache_info.currsize}")
        print(f"   Hits: {cache_info.hits}")
        print(f"   Misses: {cache_info.misses}")
        print(f"   Hit rate: {cache_info.hits / (cache_info.hits + cache_info.misses):.1%}")

        # Should have 10 unique temperatures cached
        assert cache_info.currsize == 10, f"Cache should have 10 entries, got {cache_info.currsize}"

        # Should have 10 misses (first call for each temp) and 90 hits (9 repeats each)
        assert cache_info.misses == 10, f"Should have 10 misses, got {cache_info.misses}"
        assert cache_info.hits == 90, f"Should have 90 hits, got {cache_info.hits}"

    def test_cache_clear(self):
        """Test cache clearing"""
        # Clear cache
        WaterAPIClient.clear_cache()

        # Add some data
        WaterAPIClient.fetch_properties(20.0)
        WaterAPIClient.fetch_properties(25.0)

        cache_info = WaterAPIClient.get_cache_info()
        assert cache_info.currsize == 2, "Cache should have 2 entries"

        # Clear cache
        WaterAPIClient.clear_cache()

        cache_info = WaterAPIClient.get_cache_info()
        assert cache_info.currsize == 0, "Cache should be empty after clear"
        assert cache_info.hits == 0, "Hits should be 0 after clear"
        assert cache_info.misses == 0, "Misses should be 0 after clear"


    def test_speedup_factor(self):
        """Test actual speedup from caching"""
        # Clear cache
        WaterAPIClient.clear_cache()

        # Measure uncached time
        start = time.perf_counter()
        _ = WaterAPIClient.fetch_properties(20.0)
        uncached_time = time.perf_counter() - start

        # Measure cached time (take average of 10 calls)
        cached_times = []
        for _ in range(10):
            start = time.perf_counter()
            _ = WaterAPIClient.fetch_properties(20.0)
            cached_times.append(time.perf_counter() - start)

        cached_time = sum(cached_times) / len(cached_times)

        speedup = uncached_time / cached_time if cached_time > 0 else 0

        print(f"\n   Performance speedup:")
        print(f"   Uncached time: {uncached_time*1000:.3f} ms")
        print(f"   Cached time: {cached_time*1000:.6f} ms")
        print(f"   Speedup: {speedup:.0f}x")

        # Should have significant speedup (at least 100x)
        assert speedup >= 100, f"Speedup should be at least 100x, got {speedup:.0f}x"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
