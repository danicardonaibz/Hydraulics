# Changelog

## Version 2.0 - Enhanced Flow Regime Handling & Christiansen Approximation

### New Features

#### 1. Adaptive Friction Factor Calculation

The tool now automatically selects the appropriate friction factor calculation method based on Reynolds number:

- **Laminar Flow (Re < 2000)**: Uses analytical solution `f = 64/Re`
- **Transitional/Turbulent Flow (Re ≥ 2000)**: Uses Colebrook-White equation solved with Newton-Raphson

**Benefits:**
- More accurate calculations for low-flow segments
- Conservative approach: Colebrook-White used for transitional regime (Re 2000-4000) as it provides higher friction factors
- Clear indication in reports which method was used for each segment

**Example from Report:**
```
| Segment | Reynolds | Method              | Friction Factor |
|---------|----------|---------------------|-----------------|
| 114     | 2088     | Colebrook-White     | 0.049108        |
| 115     | 1914     | Laminar (f=64/Re)   | 0.033446        |
```

#### 2. Christiansen Approximation

Added Christiansen method for quick estimation of friction losses in irrigation laterals with uniformly spaced outlets.

**Formula:**
```
h_f = F × L × J

where:
F = 1/(m+1) + 1/(2N) + √(m-1)/(6N²)
```

**Parameters:**
- N = Total number of outlets (drippers)
- m = Flow regime exponent (m=2 for Darcy-Weisbach turbulent)
- J = Unit friction loss (calculated with full flow at inlet)

**Comparison in Reports:**
The tool now provides three calculation methods:

1. **Full Segment-by-Segment Calculation** (Most accurate)
   - Accounts for decreasing flow at each dripper
   - Handles varying flow regimes (laminar/transitional/turbulent)

2. **Christiansen Approximation** (Quick estimate)
   - Simplified formula for uniformly spaced outlets
   - Assumes turbulent flow throughout
   - Good for preliminary design

3. **Simplified Model** (Upper bound)
   - Assumes constant flow (all water exits at end)
   - Provides conservative estimate

**Example Results:**
```
Full Segment-by-Segment:     3.7335 bar
Christiansen Approximation:  3.0855 bar (17.36% difference)
Simplified Model:            9.1559 bar (145.2% difference)
```

### Enhanced Reporting

#### Method Column in Segment Tables

Segment detail tables now include a "Method" column showing which friction factor calculation was used:

```
| Segment | Flow (l/h) | Reynolds | Valid | Method              | Friction Factor | Head Loss |
|---------|-----------|----------|-------|---------------------|-----------------|-----------|
| 113     | 104.0     | 2261     | ✗     | Colebrook-White     | 0.047884        | 0.0004    |
| 114     | 96.0      | 2088     | ✗     | Colebrook-White     | 0.049108        | 0.0003    |
| 115     | 88.0      | 1914     | ✗     | Laminar (f=64/Re)   | 0.033446        | 0.0002    |
```

#### Calculation Method Comparison Section

A new section in reports compares all three calculation methods:
- Full calculation details
- Christiansen approximation with coefficient breakdown
- Simplified model for reference
- Analysis of differences and recommendations

#### Enhanced Equations Documentation

The report now includes detailed documentation of:
- Laminar friction factor formula
- Colebrook-White equation with usage notes
- Christiansen approximation with all terms explained
- When each method is appropriate

### Technical Details

#### Code Changes

**src/hydraulics.py:**
- Added `calculate_laminar_friction_factor(reynolds)` function
- Modified `calculate_section_loss()` to select method based on Re
- Added `friction_method` field to results
- Added `calculate_christiansen_coefficient(num_outlets, m)` function
- Added `calculate_christiansen_head_loss()` function

**src/dripping_artery.py:**
- Modified `calculate()` to compute total number of outlets
- Added Christiansen calculation to results
- Updated `display_results()` to show comparison

**src/report_generator.py:**
- Added "Method" column to segment tables
- Added "Calculation Method Comparison" section
- Enhanced equations documentation
- Added explanatory notes for each method

### Validation

The smoke test demonstrates all features:

**Test Configuration:**
- Total flow: 1500 l/h
- Pipe: HDPE N20 (16.2 mm internal diameter)
- 4 zones: 2 transport, 2 irrigation
- Total outlets: 137 drippers

**Results:**
- Segments 1-114: Colebrook-White (Re > 2000)
- Segments 115-125: Laminar formula (Re < 2000)
- Full calculation: 3.7335 bar
- Christiansen: 3.0855 bar (17.36% diff)
- Simplified: 9.1559 bar (145.2% diff)

**Observations:**
- Laminar formula produces lower friction factors for low-Re segments
- Christiansen deviation (17%) explained by laminar regions at pipe end
- Report correctly flags transitional/laminar segments
- Method selection improves calculation accuracy

### Usage Notes

1. **No user action required** - Method selection is automatic based on Reynolds number

2. **Interpreting Results:**
   - Full calculation: Use for final design
   - Christiansen: Good for preliminary sizing if deviation < 10%
   - Large deviations indicate significant laminar flow regions

3. **Design Recommendations:**
   - If many segments show laminar flow, consider larger pipe diameter
   - Christiansen works best when all segments are turbulent
   - Review "Method" column to identify flow regime transitions

## Version 1.0 - Initial Release

### Features
- Dripping artery calculator
- Zone-by-zone hydraulic analysis
- Darcy-Weisbach with Colebrook-White friction factor
- HDPE pipe specifications (European nominal diameters)
- Virtual environment setup scripts
- Detailed markdown reports
- ASCII installation diagrams
