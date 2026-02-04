"""Core hydraulic calculation modules"""

from hydraulics.core.equations import (
    calculate_reynolds,
    calculate_velocity,
    solve_colebrook_white,
    calculate_darcy_weisbach,
    calculate_laminar_friction_factor,
    check_flow_regime,
    calculate_christiansen_coefficient
)
from hydraulics.core.properties import WaterProperties, display_water_properties
from hydraulics.core.pipes import (
    HDPE_PIPES,
    get_pipe_internal_diameter,
    list_available_pipes,
    display_pipe_table
)

__all__ = [
    # Equations
    'calculate_reynolds',
    'calculate_velocity',
    'solve_colebrook_white',
    'calculate_darcy_weisbach',
    'calculate_laminar_friction_factor',
    'check_flow_regime',
    'calculate_christiansen_coefficient',
    # Properties
    'WaterProperties',
    'display_water_properties',
    # Pipes
    'HDPE_PIPES',
    'get_pipe_internal_diameter',
    'list_available_pipes',
    'display_pipe_table',
]
