# Quick Start Guide

## Installation

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

This creates a virtual environment and installs all dependencies.

## Running the Tool

### Quick Run

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

### Manual Run
```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python hydro_calc.py
```

### Menu Options

1. **Dripping Artery Calculator** - Calculate friction losses for irrigation systems
2. **Configuration** - Set units (pressure: bar/mwc/atm, flow: m3/s/l/s/l/h, length: m/mm)
3. **View Pipe Specifications** - See available HDPE pipes
4. **View Water Properties** - Display NIST water properties
5. **Exit** - Quit the application

### Running the Smoke Test

**Windows:**
```bash
test.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
python smoke_test.py
```

## Example: Dripping Artery Calculation

The tool will guide you through:

1. Enter total flow at pump (e.g., 1500 l/h)
2. Select pipe designation (e.g., N20)
3. Add zones in sequence:
   - **Transport zones**: No drippers (enter length)
   - **Irrigation zones**: With drippers (enter length, number of drippers, target flow)
4. Type 'done' when finished

### Example Input
```
Total flow: 1500 l/h
Pipe: N20
Zone 1: transport, 10 m
Zone 2: irrigation, 80 m, 12 drippers, 500 l/h
Zone 3: transport, 50 m
Zone 4: irrigation, 160 m, 125 drippers, 1000 l/h
```

### Output

The tool provides:
- Zone-by-zone hydraulic analysis
- Reynolds numbers and flow regimes
- Friction factors (Colebrook-White)
- Head losses (Darcy-Weisbach)
- Cumulative pressure drops
- Comparison with simplified model
- Pressure requirements for drippers
- Markdown report with detailed results

### Reports

Reports are saved in the `reports/` directory with:
- Installation diagram (ASCII)
- Complete calculations for each zone
- Segment-by-segment analysis for irrigation zones
- Pressure requirements
- Validation warnings

## Key Features

- **Flow conservation validation**: Ensures irrigation flows sum to total flow
- **Accurate hydraulics**: Newton-Raphson solver for Colebrook-White equation
- **Flow regime checking**: Warns if Darcy-Weisbach assumptions are violated
- **HDPE pipe database**: European nominal diameters (N16-N160)
- **NIST water properties**: Accurate density and viscosity at 20°C
- **Detailed reporting**: Markdown format with equations and diagrams

## Understanding the Results

### Reynolds Number
- Re < 2000: Laminar (warning issued)
- 2000 < Re < 4000: Transitional (warning issued)
- Re > 4000: Turbulent (valid for Darcy-Weisbach)

### Pressure Requirements
For pressure-compensated drippers (1.5-4 bar operating range):
- Pump pressure = Dripper pressure + Total head loss
- Example: 3.73 bar head loss → pump needs 5.23-7.73 bar

### Model Comparison
The tool compares:
- **Accurate model**: Flow decreases along irrigation zones
- **Simplified model**: All flow exits at the end

The difference shows why proper calculation is important for long irrigation runs.
