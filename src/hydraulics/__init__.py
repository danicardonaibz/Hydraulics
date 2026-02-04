"""
Hydraulics - Hydraulic piping calculation tool for irrigation systems

A Python package for calculating friction losses in irrigation systems using
Darcy-Weisbach and Colebrook-White equations.
"""

__version__ = "2.0.0"
__author__ = "Hydraulics Contributors"
__license__ = "MIT"

# Core functionality
from hydraulics.core import (
    calculate_reynolds,
    calculate_velocity,
    solve_colebrook_white,
    calculate_darcy_weisbach,
    calculate_laminar_friction_factor,
    check_flow_regime,
    calculate_christiansen_coefficient,
    WaterProperties,
    display_water_properties,
    HDPE_PIPES,
    get_pipe_internal_diameter,
    list_available_pipes,
    display_pipe_table,
)

# Calculators
from hydraulics.calculators import (
    calculate_section_loss,
    calculate_christiansen_head_loss,
)

# Models
from hydraulics.models import (
    Zone,
    TransportZone,
    IrrigationZone,
    DrippingArtery,
)

# IO
from hydraulics.io import Config, config

# UI
from hydraulics.ui import main

__all__ = [
    # Version
    '__version__',
    '__author__',
    '__license__',
    # Core
    'calculate_reynolds',
    'calculate_velocity',
    'solve_colebrook_white',
    'calculate_darcy_weisbach',
    'calculate_laminar_friction_factor',
    'check_flow_regime',
    'calculate_christiansen_coefficient',
    'WaterProperties',
    'display_water_properties',
    'HDPE_PIPES',
    'get_pipe_internal_diameter',
    'list_available_pipes',
    'display_pipe_table',
    # Calculators
    'calculate_section_loss',
    'calculate_christiansen_head_loss',
    # Models
    'Zone',
    'TransportZone',
    'IrrigationZone',
    'DrippingArtery',
    # IO
    'Config',
    'config',
    # UI
    'main',
]
