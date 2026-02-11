# Multi-DN Comparison Feature

## Overview

This feature automatically calculates and displays head losses for multiple DN (nominal diameter) pipe sizes in the final report, allowing engineers to compare options without re-running calculations.

## Implementation

### Files Modified

1. **src/hydraulics/core/pipes.py**
   - Added `get_adjacent_pipe_sizes()` function to retrieve 2 smaller and 1 larger DN sizes for comparison

2. **src/hydraulics/models/artery.py**
   - Refactored `calculate()` to use internal `_calculate_for_diameter()` method
   - Added `calculate_with_dn_comparison()` method that:
     - Identifies adjacent DN sizes (2 smaller, 1 larger)
     - Calculates head losses for all 4 DN sizes
     - Returns results for all 3 calculation methods per DN

3. **src/hydraulics/io/reports.py**
   - Added `generate_dn_comparison_table()` function to create markdown comparison table
   - Updated `generate_report()` to accept optional `dn_comparison` parameter
   - DN comparison table is inserted right after Installation Overview section

4. **src/hydraulics/ui/wizards.py**
   - Updated `run_dripping_artery_wizard()` to use `calculate_with_dn_comparison()`
   - Updated `display_results()` to show DN comparison table in console output
   - Added visual marker (*) to indicate user-selected pipe

### Calculation Methods

For each DN size, the feature calculates head losses using three methods:

1. **Full Calculation**: Segment-by-segment with Darcy-Weisbach/Colebrook-White (most accurate)
2. **Christiansen Approximation**: Approximation for uniformly spaced outlets
3. **Simplified Model**: Constant flow assumption (conservative upper bound)

## Output Format

### Console Output

```
--- DN Size Comparison ---
Pipe DN    Int D (mm)   Full Calc       Christiansen    Simplified
----------------------------------------------------------------------
N25        20.4         1.2313          1.0125          3.0047
N32        26.0         0.3855          0.3156          0.9366
N40        * 32.6         0.1311          0.1069          0.3173
N50        40.8         0.0451          0.0367          0.1089

* = Selected pipe (all values in bar)
```

### Markdown Report

The DN comparison table appears in the markdown report with:
- Bold formatting for the selected pipe row
- Helpful interpretation notes
- All values in the configured pressure unit

## Benefits

- **Time Savings**: Engineers can see alternatives without recalculating
- **Better Decisions**: Easy comparison helps optimize pipe selection
- **Cost Analysis**: Shows trade-off between DN size and head loss
- **Safety Margin**: Multiple options help ensure adequate system design

## Testing

Created comprehensive test suite:
- **tests/integration/test_dn_comparison.py**: Full integration test
- Verifies correct DN size selection (2 smaller, 1 larger)
- Validates that smaller DNs have higher head losses
- Confirms all 3 calculation methods work for each DN
- Original smoke test still passes (backward compatibility)

## Backward Compatibility

The original `calculate()` method still works without changes. The new feature is activated by:
- Using `calculate_with_dn_comparison()` instead of `calculate()`
- Passing `dn_comparison` parameter to `generate_report()`

Existing code continues to work unchanged.

## Edge Cases Handled

- **Smallest DN (N16)**: Only shows 1 smaller or no smaller sizes
- **Largest DN (N160)**: Only shows available larger sizes
- **No DN options**: Gracefully handles boundary cases

## Example Usage

```python
from hydraulics.models import DrippingArtery, IrrigationZone

artery = DrippingArtery(total_flow=1500, pipe_designation="N40")
artery.add_zone(IrrigationZone(length=100, num_drippers=20, target_flow=1000))

# Calculate with DN comparison
comparison_results = artery.calculate_with_dn_comparison()
results = comparison_results['selected']
dn_comparison = comparison_results['dn_comparison']

# Generate report with comparison table
from hydraulics.io.reports import generate_report
report_path = generate_report(results, artery, dn_comparison)
```

## Future Enhancements

Possible improvements:
- Allow user to specify number of DN sizes to compare
- Add cost estimation per DN size
- Show velocity ranges for each DN
- Add Reynolds number checks per DN
