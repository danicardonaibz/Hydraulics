"""Physical constants and water properties"""


class WaterProperties:
    """Water properties at 20°C (from NIST data)"""

    # Gravitational acceleration
    g = 9.81  # m/s²

    # Water properties at 20°C (NIST data)
    density = 998.2  # kg/m³
    dynamic_viscosity = 1.002e-3  # Pa·s (N·s/m²)
    kinematic_viscosity = 1.004e-6  # m²/s

    # HDPE pipe properties
    hdpe_roughness = 0.007e-3  # m (0.007 mm - smooth pipe)


def display_water_properties():
    """Display water properties used in calculations"""
    print("\n=== WATER PROPERTIES (at 20C - NIST data) ===")
    print(f"Density (rho): {WaterProperties.density} kg/m^3")
    print(f"Dynamic viscosity (mu): {WaterProperties.dynamic_viscosity*1000:.3f} mPa.s")
    print(f"Kinematic viscosity (nu): {WaterProperties.kinematic_viscosity*1e6:.3f} mm^2/s")
    print(f"Gravitational acceleration (g): {WaterProperties.g} m/s^2")
    print(f"HDPE pipe roughness (epsilon): {WaterProperties.hdpe_roughness*1000:.4f} mm")
    print()
