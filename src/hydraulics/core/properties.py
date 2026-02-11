"""Physical constants and water properties"""

from hydraulics.core.water_api import WaterAPIClient


class WaterProperties:
    """
    Water properties with dynamic temperature-based lookup.

    This class provides water properties that can be dynamically loaded based on
    temperature using the IAPWS (International Association for the Properties of
    Water and Steam) library, with fallback to default 20°C values.
    """

    # Gravitational acceleration
    g = 9.81  # m/s²

    # Default water properties at 20°C (NIST data) - used as fallback
    _default_density = 998.2  # kg/m³
    _default_dynamic_viscosity = 1.002e-3  # Pa·s (N·s/m²)
    _default_kinematic_viscosity = 1.004e-6  # m²/s

    # Current water properties (initialized to defaults)
    density = _default_density  # kg/m³
    dynamic_viscosity = _default_dynamic_viscosity  # Pa·s
    kinematic_viscosity = _default_kinematic_viscosity  # m²/s
    temperature = 20.0  # °C
    source = "default"  # 'iapws' or 'default'

    # HDPE pipe properties
    hdpe_roughness = 0.007e-3  # m (0.007 mm - smooth pipe)

    @classmethod
    def set_temperature(cls, temperature_celsius):
        """
        Set water properties based on temperature.

        Fetches properties from IAPWS library for the given temperature.
        Falls back to default 20°C values if API fails.

        Args:
            temperature_celsius: Water temperature in degrees Celsius (0-100°C)

        Raises:
            ValueError: If temperature is out of valid range
        """
        properties = WaterAPIClient.fetch_properties(temperature_celsius)

        cls.temperature = properties["temperature"]
        cls.density = properties["density"]
        cls.dynamic_viscosity = properties["dynamic_viscosity"]
        cls.kinematic_viscosity = properties["kinematic_viscosity"]
        cls.source = properties["source"]

    @classmethod
    def reset_to_defaults(cls):
        """Reset water properties to default 20°C values"""
        cls.temperature = 20.0
        cls.density = cls._default_density
        cls.dynamic_viscosity = cls._default_dynamic_viscosity
        cls.kinematic_viscosity = cls._default_kinematic_viscosity
        cls.source = "default"


def display_water_properties():
    """Display water properties used in calculations"""
    source_label = "IAPWS" if WaterProperties.source == "iapws" else "NIST data (default)"
    print(f"\n=== WATER PROPERTIES (at {WaterProperties.temperature:.1f}C - {source_label}) ===")
    print(f"Density (rho): {WaterProperties.density:.2f} kg/m^3")
    print(f"Dynamic viscosity (mu): {WaterProperties.dynamic_viscosity*1000:.3f} mPa.s")
    print(f"Kinematic viscosity (nu): {WaterProperties.kinematic_viscosity*1e6:.3f} mm^2/s")
    print(f"Gravitational acceleration (g): {WaterProperties.g} m/s^2")
    print(f"HDPE pipe roughness (epsilon): {WaterProperties.hdpe_roughness*1000:.4f} mm")
    print()
