# Hydraulics

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Version](https://img.shields.io/badge/version-2.0.0-green.svg)

A professional Python package for calculating friction losses in irrigation piping systems using Darcy-Weisbach and Colebrook-White equations.

## Features

- **Dripping Artery Calculator**: Calculate friction losses in irrigation systems with pressure-compensated drippers
- **Adaptive Friction Factor Calculation**:
  - Laminar flow (Re < 2000): Uses f = 64/Re
  - Turbulent/Transitional (Re ≥ 2000): Uses Colebrook-White equation
  - Automatic method selection based on Reynolds number
- **Christiansen Approximation**: Quick estimation method for uniformly spaced outlets with comparison to full calculation
- **Accurate Hydraulics**: Uses Darcy-Weisbach equation with Newton-Raphson solver
- **HDPE Pipe Support**: Built-in European nominal diameter specifications (PN 10)
- **Flow Validation**: Ensures flow conservation throughout the system
- **Unit Configuration**: Support for multiple unit systems (bar/atm/mwc, l/h/l/s/m³/s, m/mm)
- **Detailed Reports**: Generates markdown reports with:
  - Zone-by-zone calculations
  - Segment tables with friction factor method indicators
  - Calculation method comparison (Full, Christiansen, Simplified)
  - ASCII installation diagrams
  - Pressure requirements
- **NIST Water Properties**: Uses accurate water properties at 20°C

## Quick Start

### Installation

#### From Source

```bash
git clone https://github.com/USERNAME/Hydraulics.git
cd Hydraulics
pip install -e .
```

#### Using Virtual Environment

**Windows:**
```bash
setup.bat
run.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

### Usage

#### Command Line Interface

```bash
hydro-calc
```

#### As a Python Library

```python
from hydraulics import DrippingArtery, TransportZone, IrrigationZone

# Create a dripping artery system
artery = DrippingArtery(total_flow=1500, pipe_designation="N20")

# Add zones
artery.add_zone(TransportZone(length=10))
artery.add_zone(IrrigationZone(length=80, num_drippers=12, target_flow=500))
artery.add_zone(TransportZone(length=50))
artery.add_zone(IrrigationZone(length=160, num_drippers=125, target_flow=1000))

# Calculate
results = artery.calculate()
print(f"Total head loss: {results['total_head_loss']:.3f} m")
```

### Run Tests

```bash
# Run smoke test
python tests/integration/test_smoke.py

# Run with pytest
pytest tests/
```

## Documentation

- [Getting Started](docs/getting_started.md) - Quick start guide
- [Contributing](docs/contributing.md) - How to contribute to this project
- [API Reference](docs/) - Detailed API documentation

## Calculation Methods

### Darcy-Weisbach Equation
```
h_f = f × (L/D) × (v²/2g)
```

### Friction Factor Calculation

**Laminar Flow (Re < 2000):**
```
f = 64/Re
```

**Transitional/Turbulent (Re ≥ 2000):**
```
1/√f = -2 × log₁₀(ε/(3.7D) + 2.51/(Re√f))
```
Solved using Newton-Raphson method. Colebrook-White is used for transitional flow (Re < 4000) as it provides conservative (higher) friction factors.

### Christiansen Approximation
```
h_f = F × L × J
F = 1/(m+1) + 1/(2N) + √(m-1)/(6N²)
```
Where:
- N = Number of outlets
- m = Flow regime exponent (m=2 for Darcy-Weisbach)
- J = Unit friction loss (calculated with full flow)

## HDPE Pipe Specifications

Supported European nominal diameters (PN 10):
- N16, N20, N25, N32, N40, N50, N63, N75, N90, N110, N125, N140, N160

## Water Properties (NIST at 20°C)

- Density: 998.2 kg/m³
- Dynamic viscosity: 1.002 mPa·s
- Kinematic viscosity: 1.004 mm²/s
- HDPE roughness: 0.007 mm

## Project Structure

```
Hydraulics/
├── src/hydraulics/          # Main package
│   ├── core/               # Core calculation modules
│   ├── models/             # Data models
│   ├── calculators/        # Calculation engines
│   ├── ui/                 # User interface
│   ├── io/                 # Input/Output
│   └── utils/              # Utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example scripts
└── scripts/                # Utility scripts
```

## Contributing

Contributions are welcome! Please read the [Contributing Guide](docs/contributing.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in academic work, please cite:

```bibtex
@software{hydraulics2026,
  title = {Hydraulics: Hydraulic Piping Calculation Tool},
  author = {Hydraulics Contributors},
  year = {2026},
  url = {https://github.com/USERNAME/Hydraulics},
  version = {2.0.0}
}
```

## Acknowledgments

- NIST for accurate water property data
- European standards for HDPE pipe specifications
- The open-source community for tools and libraries

## Support

- Report bugs: [GitHub Issues](https://github.com/USERNAME/Hydraulics/issues)
- Ask questions: [GitHub Discussions](https://github.com/USERNAME/Hydraulics/discussions)
