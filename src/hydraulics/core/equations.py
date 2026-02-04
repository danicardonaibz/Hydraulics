"""Hydraulic calculation equations - Darcy-Weisbach, Colebrook-White, Reynolds, Christiansen"""

import math


def calculate_reynolds(velocity, diameter, kinematic_viscosity):
    """
    Calculate Reynolds number

    Re = v * D / ν

    Args:
        velocity: Flow velocity in m/s
        diameter: Pipe internal diameter in m
        kinematic_viscosity: Water kinematic viscosity in m²/s

    Returns:
        Reynolds number (dimensionless)
    """
    return velocity * diameter / kinematic_viscosity


def calculate_velocity(flow_m3s, diameter):
    """
    Calculate flow velocity from volumetric flow rate

    v = Q / A = Q / (π * D² / 4)

    Args:
        flow_m3s: Volumetric flow rate in m³/s
        diameter: Pipe internal diameter in m

    Returns:
        Flow velocity in m/s
    """
    area = math.pi * diameter**2 / 4
    return flow_m3s / area


def solve_colebrook_white(reynolds, diameter, roughness, max_iterations=100, tolerance=1e-6):
    """
    Solve the Colebrook-White equation for friction factor using Newton-Raphson method

    1/√f = -2 * log10(ε/(3.7*D) + 2.51/(Re*√f))

    Args:
        reynolds: Reynolds number
        diameter: Pipe internal diameter in m
        roughness: Pipe absolute roughness in m
        max_iterations: Maximum number of iterations
        tolerance: Convergence tolerance

    Returns:
        Friction factor f (dimensionless)
    """
    # Initial guess using Swamee-Jain approximation
    relative_roughness = roughness / diameter
    term1 = relative_roughness / 3.7
    term2 = 5.74 / (reynolds ** 0.9)
    f_guess = 0.25 / (math.log10(term1 + term2) ** 2)

    # Newton-Raphson iteration
    for i in range(max_iterations):
        sqrt_f = math.sqrt(f_guess)

        # Function: F(f) = 1/√f + 2*log10(ε/(3.7*D) + 2.51/(Re*√f))
        term_a = relative_roughness / 3.7
        term_b = 2.51 / (reynolds * sqrt_f)
        F = 1/sqrt_f + 2 * math.log10(term_a + term_b)

        # Derivative: F'(f) = -0.5*f^(-3/2) - 2.51/(Re*f*√f*ln(10)*(ε/(3.7*D) + 2.51/(Re*√f)))
        dF = -0.5 * (f_guess ** (-1.5)) - (2.51 / (reynolds * f_guess * sqrt_f * math.log(10) * (term_a + term_b)))

        # Newton-Raphson update
        f_new = f_guess - F / dF

        # Check convergence
        if abs(f_new - f_guess) < tolerance:
            return f_new

        f_guess = f_new

    # If not converged, return current estimate
    return f_guess


def calculate_darcy_weisbach(friction_factor, length, diameter, velocity, g=9.81):
    """
    Calculate head loss due to friction using Darcy-Weisbach equation

    h_f = f * (L/D) * (v²/2g)

    Args:
        friction_factor: Darcy friction factor (dimensionless)
        length: Pipe length in m
        diameter: Pipe internal diameter in m
        velocity: Flow velocity in m/s
        g: Gravitational acceleration in m/s² (default: 9.81)

    Returns:
        Head loss in meters of water column
    """
    return friction_factor * (length / diameter) * (velocity**2 / (2 * g))


def calculate_laminar_friction_factor(reynolds):
    """
    Calculate friction factor for laminar flow using the analytical solution

    f = 64/Re

    Args:
        reynolds: Reynolds number

    Returns:
        Friction factor f (dimensionless)
    """
    return 64.0 / reynolds


def check_flow_regime(reynolds):
    """
    Check the flow regime based on Reynolds number

    Args:
        reynolds: Reynolds number

    Returns:
        Tuple (regime_name, is_valid_for_colebrook_white)
    """
    if reynolds < 2000:
        return "Laminar", False
    elif reynolds < 4000:
        return "Transitional", False
    else:
        return "Turbulent", True


def calculate_christiansen_coefficient(num_outlets, m=2.0):
    """
    Calculate Christiansen reduction factor for friction loss in laterals with multiple outlets

    F = 1/(m+1) + 1/(2N) + sqrt(m-1)/(6N²)

    Args:
        num_outlets: Total number of outlets (N)
        m: Flow regime exponent (m=2 for Darcy-Weisbach turbulent, m=1.75 for Hazen-Williams)

    Returns:
        Christiansen coefficient F (dimensionless)
    """
    N = num_outlets

    term1 = 1.0 / (m + 1.0)
    term2 = 1.0 / (2.0 * N)
    term3 = math.sqrt(m - 1.0) / (6.0 * N * N)

    F = term1 + term2 + term3

    return F
