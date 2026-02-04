# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hydraulics is a Python package for calculating friction losses in irrigation piping systems using Darcy-Weisbach and Colebrook-White equations. It calculates pressure drops in drip irrigation systems with pressure-compensated drippers, considering varying flow rates through pipe segments.

## Development Commands

### Setup and Installation
```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Testing
```bash
# Run smoke test (integration test with known good values)
python tests/integration/test_smoke.py

# Run all tests with pytest
pytest tests/

# Run specific test
pytest tests/integration/test_smoke.py -v

# Run with coverage
pytest tests/ --cov=hydraulics --cov-report=term
```

### Code Quality
```bash
# Format code (line length: 100)
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Running the CLI
```bash
# Use installed entry point
hydro-calc

# Or run directly
python hydro_calc.py
```

## Architecture

### Core Calculation Flow

The package uses a **layered architecture** with clear separation of concerns:

1. **`hydraulics.core`** - Pure hydraulic equations and constants
   - `equations.py`: Mathematical functions (Reynolds, Darcy-Weisbach, Colebrook-White solver)
   - `properties.py`: Physical constants (NIST water properties at 20°C, HDPE roughness)
   - `pipes.py`: HDPE pipe specifications database (European PN 10 standard)

2. **`hydraulics.calculators`** - Calculation engines that apply core equations
   - `segment.py`: Main calculation engine
     - `calculate_section_loss()`: Calculates head loss for a single pipe segment
     - `calculate_christiansen_head_loss()`: Approximation for uniformly spaced outlets
   - Automatically selects friction factor method based on Reynolds number:
     - Re < 2000: Laminar (f = 64/Re)
     - Re ≥ 2000: Colebrook-White (Newton-Raphson solver)

3. **`hydraulics.models`** - Domain models representing physical system
   - `zones.py`: Zone types (TransportZone, IrrigationZone)
   - `artery.py`: DrippingArtery orchestrates the full calculation
     - Validates flow conservation (sum of irrigation flows = total flow)
     - Calculates zone-by-zone with decreasing flow in irrigation zones
     - Produces three results: full segment-by-segment, Christiansen approximation, simplified constant-flow

4. **`hydraulics.io`** - Input/Output and configuration
   - `config.py`: Global Config singleton for unit conversions (bar/mwc/atm, l/h/l/s/m³/s)
   - `reports.py`: Markdown report generator with ASCII diagrams

5. **`hydraulics.ui`** - User interface
   - `cli.py`: Main menu system, configuration dialogs
   - `wizards.py`: Interactive dripping artery wizard, result display

6. **`hydraulics.utils`** - Utilities
   - `conversions.py`: Unit conversion functions

### Key Design Patterns

**Segment-by-Segment Calculation**: For irrigation zones with drippers, flow decreases incrementally. The calculator divides zones into segments between drippers and calculates head loss for each segment with its specific flow rate. This is more accurate than assuming constant flow.

**Unit Abstraction**: User inputs are in configured units (e.g., l/h, bar), but all calculations happen in SI units (m³/s, m). The `config` singleton handles all conversions transparently.

**Flow Conservation Validation**: Before calculation, `DrippingArtery.validate_flow_conservation()` ensures the sum of irrigation zone flows equals total flow (within 1% tolerance). This catches user input errors early.

**Friction Factor Selection**: The calculator automatically selects between laminar and turbulent equations based on Reynolds number. For transitional flow (Re < 4000), it conservatively uses Colebrook-White which gives higher (safer) friction factors.

### Important Constants (WaterProperties)

All calculations use **NIST water properties at 20°C**:
- Density: 998.2 kg/m³
- Kinematic viscosity: 1.004e-6 m²/s
- HDPE roughness: 0.007 mm

These are critical for accurate Reynolds number and friction factor calculations.

### Unit System

**Internal**: All calculations are in SI units (m, m/s, m³/s, Pa, m of head)
**External**: Users configure units via `config` object:
- Pressure: bar (default), mwc, atm
- Flow: l/h (default), l/s, m³/s
- Length: m (default), mm

Unit conversions happen at the boundaries (input/output) only.

## Branch Strategy

- `main`: Production code (protected)
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

Always create PRs to `develop`, not `main`.

## Commit Message Format

Use Conventional Commits:
```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Examples:
  feat(core): add Hazen-Williams equation
  fix(calculators): handle zero flow edge case
  docs(readme): update installation steps
```

## Testing Strategy

**Smoke Test** (`tests/integration/test_smoke.py`): Full system test with known good values (1500 l/h system with 4 zones). This must pass before any commit.

**Unit Tests**: Place in `tests/test_*/` matching source structure. Focus on:
- Edge cases (zero flow, very high/low Reynolds numbers)
- Unit conversions
- Flow conservation validation

## Code Style

- **Line length**: 100 characters (configured in black)
- **Docstrings**: Required for all functions/classes, include equations in docstring when relevant
- **Type hints**: Use where appropriate
- **Import order**: stdlib → third-party → local (hydraulics.*)

## Unicode Handling

**IMPORTANT**: Console output must be ASCII-compatible for Windows cmd.exe. Use ASCII representations instead of Greek letters:
- Good: `rho`, `mu`, `nu`, `epsilon`, `deg C`
- Bad: `ρ`, `μ`, `ν`, `ε`, `°C` (causes UnicodeEncodeError on Windows)

## Package Entry Points

The package provides a CLI entry point `hydro-calc` that maps to `hydraulics.ui.cli:main`. This is defined in `pyproject.toml` under `[project.scripts]`.

## Version Management

Version is defined in **three places** (must be synchronized):
1. `src/hydraulics/__init__.py` (`__version__`)
2. `pyproject.toml` (`version`)
3. `CHANGELOG.md`

## Common Pitfalls

1. **Mixing unit systems**: Always convert to SI before calculations, convert back for display
2. **Flow conservation**: Irrigation zone flows must sum to total flow
3. **Reynolds number thresholds**: Re < 2000 (laminar), 2000-4000 (transitional), > 4000 (turbulent)
4. **Segment division**: Irrigation zones divide into equal segments (length / num_drippers)
5. **Windows encoding**: Use ASCII in console output, Unicode OK in markdown reports
