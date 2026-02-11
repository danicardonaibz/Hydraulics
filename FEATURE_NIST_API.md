# Feature: NIST Water Properties API Integration

## Overview

This feature replaces hardcoded water properties with dynamic lookup based on temperature using the IAPWS (International Association for the Properties of Water and Steam) Python library. This allows for more accurate hydraulic calculations across different operating temperatures.

## Background

Previously, the hydraulics package used hardcoded water properties at 20°C:
- Density: 998.2 kg/m³
- Dynamic viscosity: 1.002 mPa·s
- Kinematic viscosity: 1.004 mm²/s

These properties vary significantly with temperature, affecting Reynolds numbers and friction factors in hydraulic calculations.

## Implementation

### New Components

1. **`src/hydraulics/core/water_api.py`** - New module containing `WaterAPIClient`
   - Fetches water properties using IAPWS-95 formulation
   - Handles errors gracefully with fallback to default 20°C values
   - Validates temperature range (0-100°C for liquid water)

2. **Enhanced `WaterProperties` class** - Modified in `src/hydraulics/core/properties.py`
   - `set_temperature(temperature_celsius)` - Sets properties based on temperature
   - `reset_to_defaults()` - Resets to default 20°C values
   - Tracks data source (`'iapws'` or `'default'`)

3. **Wizard Integration** - Modified `src/hydraulics/ui/wizards.py`
   - Added temperature input prompt at the start of the wizard
   - Default value is 20°C (press Enter to skip)
   - Validates temperature range

4. **Report Updates** - Modified `src/hydraulics/io/reports.py`
   - Reports now include actual temperature used
   - Shows data source (IAPWS or default)

### Dependencies

Added `iapws>=1.5.0` to project dependencies:
- `requirements.txt`
- `pyproject.toml`

## Usage

### Interactive Wizard

When running the dripping artery wizard, users are now prompted for water temperature:

```
--- Water Temperature ---
Enter water temperature (default is 20C).
Press Enter to use default, or enter temperature (0-100C).
Water temperature (C) [20]:
```

Examples:
- Press Enter → Uses default 20°C
- Enter `15` → Fetches properties for 15°C water
- Enter `25` → Fetches properties for 25°C water

### Programmatic Usage

```python
from hydraulics.core.properties import WaterProperties

# Set water temperature to 15°C
WaterProperties.set_temperature(15.0)

# Properties are now updated for 15°C
print(f"Density: {WaterProperties.density:.2f} kg/m³")
print(f"Kinematic viscosity: {WaterProperties.kinematic_viscosity*1e6:.3f} mm²/s")

# Reset to defaults (20°C)
WaterProperties.reset_to_defaults()
```

## Temperature Effects on Properties

Example property variations with temperature:

| Temperature | Density (kg/m³) | Dynamic Viscosity (mPa·s) | Kinematic Viscosity (mm²/s) |
|-------------|-----------------|---------------------------|------------------------------|
| 10°C        | 999.70          | 1.306                     | 1.306                        |
| 15°C        | 999.10          | 1.139                     | 1.139                        |
| 20°C        | 998.21          | 1.002                     | 1.003                        |
| 25°C        | 997.05          | 0.890                     | 0.893                        |
| 30°C        | 995.65          | 0.797                     | 0.801                        |

### Impact on Calculations

- **Higher temperatures** (warmer water):
  - Lower density
  - Lower viscosity
  - **Higher Reynolds numbers** (more turbulent flow)
  - **Lower friction factors**
  - Lower head losses

- **Lower temperatures** (colder water):
  - Higher density
  - Higher viscosity
  - **Lower Reynolds numbers** (more laminar flow)
  - **Higher friction factors**
  - Higher head losses

## Error Handling

The implementation includes robust error handling:

1. **Invalid temperature range**: Raises `ValueError` with clear message
2. **IAPWS library not installed**: Falls back to default 20°C with warning
3. **API calculation failure**: Falls back to default 20°C with warning

All warnings are displayed to the user via Python's `warnings` module.

## Testing

Comprehensive test suite in `tests/test_water_api.py`:

- `TestWaterAPIClient`: Tests API client functionality
  - Property fetching at various temperatures (10°C, 20°C, 30°C)
  - Error handling for invalid temperatures
  - Default property fallback

- `TestWaterProperties`: Tests WaterProperties class
  - Default properties
  - Temperature setting
  - Reset to defaults
  - Constants unchanged after temperature changes

Run tests:
```bash
pytest tests/test_water_api.py -v
```

All 10 tests pass successfully.

## Technical Details

### IAPWS-95 Formulation

The IAPWS-95 formulation is the international standard for water properties:
- Accurate for liquid water from 0°C to 374°C
- Valid at atmospheric pressure (0.101325 MPa)
- Provides density, viscosity, and other thermodynamic properties

### SI Unit Consistency

All calculations remain in SI units:
- Temperature: Converted from °C to K for IAPWS (T_K = T_C + 273.15)
- Density: kg/m³
- Dynamic viscosity: Pa·s
- Kinematic viscosity: m²/s (calculated as μ/ρ)

## Future Enhancements

Possible future improvements:
1. Support for non-atmospheric pressures
2. Caching of frequently used temperatures
3. Configuration file for default temperature
4. Temperature validation against local climate data

## References

- [IAPWS Python Library](https://pypi.org/project/iapws/) - Official PyPI package
- [IAPWS Documentation](https://iapws.readthedocs.io/) - Full API documentation
- [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/fluid/) - Original data source reference
- [GitHub: jjgomera/iapws](https://github.com/jjgomera/iapws) - Source code repository

## Author

Implemented by the API integrator team member as part of the hydraulics-enhancement project.

## Version

Added in version 2.1.0
