"""
Water properties API client using IAPWS (International Association for the
Properties of Water and Steam) standards.

This module provides dynamic water property lookup based on temperature,
with fallback to default 20°C values if the API fails.
"""

import warnings


class WaterAPIClient:
    """Client for fetching water properties using IAPWS library"""

    # Default properties at 20°C (fallback values)
    DEFAULT_TEMPERATURE = 20.0  # °C
    DEFAULT_DENSITY = 998.2  # kg/m³
    DEFAULT_DYNAMIC_VISCOSITY = 1.002e-3  # Pa·s
    DEFAULT_KINEMATIC_VISCOSITY = 1.004e-6  # m²/s

    @staticmethod
    def fetch_properties(temperature_celsius):
        """
        Fetch water properties at specified temperature using IAPWS-95 formulation.

        Args:
            temperature_celsius: Water temperature in degrees Celsius

        Returns:
            dict: Water properties with keys:
                - temperature: Temperature in °C
                - density: Density in kg/m³
                - dynamic_viscosity: Dynamic viscosity in Pa·s
                - kinematic_viscosity: Kinematic viscosity in m²/s
                - source: 'iapws' or 'default' indicating data source

        Raises:
            ValueError: If temperature is out of valid range (0-100°C for liquid water)
        """
        # Validate temperature range
        if temperature_celsius < 0 or temperature_celsius > 100:
            raise ValueError(
                f"Temperature must be between 0 and 100°C. Got: {temperature_celsius}°C"
            )

        try:
            # Import IAPWS library (lazy import to handle missing dependency gracefully)
            from iapws import IAPWS95

            # Convert Celsius to Kelvin for IAPWS
            temperature_kelvin = temperature_celsius + 273.15

            # Calculate properties at slightly higher pressure to ensure liquid phase
            # At 100°C and 0.101325 MPa, water is at saturation (liquid/vapor transition)
            # Use 0.2 MPa to ensure liquid phase for all temperatures 0-100°C
            pressure_mpa = 0.2 if temperature_celsius >= 99.0 else 0.101325

            # IAPWS95 uses T (K) and P (MPa) as inputs
            water = IAPWS95(T=temperature_kelvin, P=pressure_mpa)

            # Check if calculation was successful and in liquid phase
            if not hasattr(water, "rho") or water.rho is None:
                raise RuntimeError("IAPWS calculation failed to produce valid density")

            # Verify we got liquid phase (density should be > 900 kg/m³ for liquid water)
            if water.rho < 900:
                raise RuntimeError(f"IAPWS returned vapor phase at {temperature_celsius}°C (rho={water.rho:.2f} kg/m³)")

            # Extract properties
            density = water.rho  # kg/m³
            dynamic_viscosity = water.mu  # Pa·s

            # Calculate kinematic viscosity: nu = mu / rho
            kinematic_viscosity = dynamic_viscosity / density  # m²/s

            return {
                "temperature": temperature_celsius,
                "density": density,
                "dynamic_viscosity": dynamic_viscosity,
                "kinematic_viscosity": kinematic_viscosity,
                "source": "iapws",
            }

        except ImportError:
            # IAPWS library not installed
            warnings.warn(
                "IAPWS library not installed. Install with 'pip install iapws'. "
                f"Using default properties for {WaterAPIClient.DEFAULT_TEMPERATURE}°C.",
                UserWarning,
            )
            return WaterAPIClient._get_default_properties()

        except Exception as e:
            # Any other error (calculation failure, invalid state, etc.)
            warnings.warn(
                f"Failed to fetch water properties from IAPWS: {e}. "
                f"Using default properties for {WaterAPIClient.DEFAULT_TEMPERATURE}°C.",
                UserWarning,
            )
            return WaterAPIClient._get_default_properties()

    @staticmethod
    def _get_default_properties():
        """
        Get default water properties at 20°C (NIST data)

        Returns:
            dict: Water properties at 20°C
        """
        return {
            "temperature": WaterAPIClient.DEFAULT_TEMPERATURE,
            "density": WaterAPIClient.DEFAULT_DENSITY,
            "dynamic_viscosity": WaterAPIClient.DEFAULT_DYNAMIC_VISCOSITY,
            "kinematic_viscosity": WaterAPIClient.DEFAULT_KINEMATIC_VISCOSITY,
            "source": "default",
        }
