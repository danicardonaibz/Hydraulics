"""Tests for water API integration"""

import pytest
from hydraulics.core.water_api import WaterAPIClient
from hydraulics.core.properties import WaterProperties


class TestWaterAPIClient:
    """Test WaterAPIClient functionality"""

    def test_fetch_properties_at_20c(self):
        """Test fetching properties at 20°C"""
        props = WaterAPIClient.fetch_properties(20.0)

        assert props["temperature"] == 20.0
        assert props["source"] in ["iapws", "default"]
        # Density should be close to 998.2 kg/m³ at 20°C
        assert 997.0 < props["density"] < 999.0
        # Dynamic viscosity should be close to 1.002 mPa·s
        assert 0.9e-3 < props["dynamic_viscosity"] < 1.1e-3
        # Kinematic viscosity should be close to 1.004 mm²/s
        assert 0.9e-6 < props["kinematic_viscosity"] < 1.1e-6

    def test_fetch_properties_at_10c(self):
        """Test fetching properties at 10°C"""
        props = WaterAPIClient.fetch_properties(10.0)

        assert props["temperature"] == 10.0
        # Water is denser at 10°C than at 20°C
        assert props["density"] > 999.0
        # Water is more viscous at 10°C than at 20°C
        assert props["dynamic_viscosity"] > 1.1e-3

    def test_fetch_properties_at_30c(self):
        """Test fetching properties at 30°C"""
        props = WaterAPIClient.fetch_properties(30.0)

        assert props["temperature"] == 30.0
        # Water is less dense at 30°C than at 20°C
        assert props["density"] < 997.0
        # Water is less viscous at 30°C than at 20°C
        assert props["dynamic_viscosity"] < 1.0e-3

    def test_invalid_temperature_too_low(self):
        """Test error handling for temperature below 0°C"""
        with pytest.raises(ValueError, match="Temperature must be between 0 and 100"):
            WaterAPIClient.fetch_properties(-10.0)

    def test_invalid_temperature_too_high(self):
        """Test error handling for temperature above 100°C"""
        with pytest.raises(ValueError, match="Temperature must be between 0 and 100"):
            WaterAPIClient.fetch_properties(150.0)

    def test_get_default_properties(self):
        """Test default property fallback"""
        props = WaterAPIClient._get_default_properties()

        assert props["temperature"] == 20.0
        assert props["density"] == 998.2
        assert props["dynamic_viscosity"] == 1.002e-3
        assert props["kinematic_viscosity"] == 1.004e-6
        assert props["source"] == "default"


class TestWaterProperties:
    """Test WaterProperties class"""

    def test_default_properties(self):
        """Test default properties at 20°C"""
        WaterProperties.reset_to_defaults()

        assert WaterProperties.temperature == 20.0
        assert WaterProperties.density == 998.2
        assert WaterProperties.dynamic_viscosity == 1.002e-3
        assert WaterProperties.kinematic_viscosity == 1.004e-6
        assert WaterProperties.source == "default"

    def test_set_temperature(self):
        """Test setting temperature updates properties"""
        WaterProperties.set_temperature(15.0)

        assert WaterProperties.temperature == 15.0
        # Properties should have changed from default
        assert WaterProperties.density != 998.2

        # Reset for other tests
        WaterProperties.reset_to_defaults()

    def test_reset_to_defaults(self):
        """Test resetting to defaults"""
        # First change temperature
        WaterProperties.set_temperature(25.0)
        assert WaterProperties.temperature == 25.0

        # Then reset
        WaterProperties.reset_to_defaults()
        assert WaterProperties.temperature == 20.0
        assert WaterProperties.density == 998.2
        assert WaterProperties.source == "default"

    def test_constants_unchanged(self):
        """Test that constants remain unchanged"""
        # Set temperature to something different
        WaterProperties.set_temperature(15.0)

        # Constants should not change
        assert WaterProperties.g == 9.81
        assert WaterProperties.hdpe_roughness == 0.007e-3

        # Reset for other tests
        WaterProperties.reset_to_defaults()
