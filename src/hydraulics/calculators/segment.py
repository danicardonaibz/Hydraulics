"""Segment-by-segment hydraulic calculation engine"""

from hydraulics.core.equations import (
    calculate_velocity,
    calculate_reynolds,
    check_flow_regime,
    calculate_laminar_friction_factor,
    solve_colebrook_white,
    calculate_darcy_weisbach,
    calculate_christiansen_coefficient
)
from hydraulics.core.properties import WaterProperties


def calculate_section_loss(flow_m3s, diameter, length, roughness=None):
    """
    Calculate head loss for a pipe section

    Args:
        flow_m3s: Volumetric flow rate in m³/s
        diameter: Pipe internal diameter in m
        length: Pipe length in m
        roughness: Pipe absolute roughness in m (default: HDPE roughness)

    Returns:
        Dictionary with calculation results
    """
    if roughness is None:
        roughness = WaterProperties.hdpe_roughness

    # Calculate velocity
    velocity = calculate_velocity(flow_m3s, diameter)

    # Calculate Reynolds number
    reynolds = calculate_reynolds(velocity, diameter, WaterProperties.kinematic_viscosity)

    # Check flow regime
    regime, is_valid = check_flow_regime(reynolds)

    # Determine friction factor calculation method
    if reynolds < 2000:
        # Laminar flow - use analytical solution f = 64/Re
        friction_factor = calculate_laminar_friction_factor(reynolds)
        friction_method = "Laminar (f=64/Re)"
    else:
        # Transitional or turbulent - use Colebrook-White (safer for transitional)
        friction_factor = solve_colebrook_white(reynolds, diameter, roughness)
        friction_method = "Colebrook-White"

    # Calculate head loss
    head_loss = calculate_darcy_weisbach(friction_factor, length, diameter, velocity, WaterProperties.g)

    return {
        "velocity": velocity,
        "reynolds": reynolds,
        "flow_regime": regime,
        "is_valid": is_valid,
        "friction_factor": friction_factor,
        "friction_method": friction_method,
        "head_loss": head_loss
    }


def calculate_christiansen_head_loss(total_flow_m3s, diameter, total_length, roughness=None, num_outlets=1, m=2.0):
    """
    Calculate head loss using Christiansen approximation for uniformly spaced outlets

    Total loss = total_length × unit_loss × F
    where unit_loss is calculated assuming all flow reaches the end

    Args:
        total_flow_m3s: Total flow rate at the inlet in m³/s
        diameter: Pipe internal diameter in m
        total_length: Total pipe length in m
        roughness: Pipe absolute roughness in m (default: HDPE roughness)
        num_outlets: Total number of outlets
        m: Flow regime exponent (default 2.0 for Darcy-Weisbach)

    Returns:
        Dictionary with Christiansen calculation results
    """
    if roughness is None:
        roughness = WaterProperties.hdpe_roughness

    # Calculate unit loss assuming constant flow throughout
    result = calculate_section_loss(total_flow_m3s, diameter, total_length, roughness)

    # Unit loss per meter
    unit_loss = result['head_loss'] / total_length

    # Calculate Christiansen coefficient
    F = calculate_christiansen_coefficient(num_outlets, m)

    # Calculate adjusted head loss
    christiansen_head_loss = total_length * unit_loss * F

    return {
        "christiansen_coefficient": F,
        "unit_loss_m_per_m": unit_loss,
        "head_loss": christiansen_head_loss,
        "velocity": result['velocity'],
        "reynolds": result['reynolds'],
        "friction_factor": result['friction_factor'],
        "friction_method": result['friction_method'],
        "num_outlets": num_outlets,
        "m_exponent": m
    }
