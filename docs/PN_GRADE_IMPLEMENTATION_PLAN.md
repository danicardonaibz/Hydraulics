# PN Grade Implementation Plan

## Overview
This document outlines the implementation plan for adding PN (Pressure Nominal) grade support to the hydraulics package. This feature will allow users to select different pressure ratings (PN6, PN10, PN16) for HDPE pipes, which have different wall thicknesses and internal diameters.

## Objectives
1. Expand the HDPE pipe database to support multiple PN grades per DN size
2. Allow users to select PN grade during the wizard workflow
3. Maintain PN grade consistency in DN comparison calculations
4. Ensure backward compatibility (default to PN10)
5. Update reports to clearly show PN grade information

## Technical Background

### HDPE Pipe PN Grades
Based on ISO 4427 standard for PE pipes for water supply:

- **PN6**: Low pressure (6 bar working pressure) - thinner walls, larger internal diameter
- **PN10**: Medium pressure (10 bar working pressure) - standard thickness, medium internal diameter
- **PN16**: High pressure (16 bar working pressure) - thicker walls, smaller internal diameter

### Impact on Hydraulics
For the same nominal diameter (DN), different PN grades have:
- Different internal diameters (ID)
- Different wall thicknesses
- Same external diameter (OD)
- Different flow capacity and head loss characteristics

**Example**: DN40 (OD=50mm)
- PN6: ID = 44.2mm (larger capacity, lower head loss)
- PN10: ID = 40.8mm (current implementation)
- PN16: ID = 36.2mm (smaller capacity, higher head loss)

## Data Source

Complete HDPE pipe dimensions extracted from ISO 4427 standard (Engineering ToolBox):

| DN | Nominal OD (mm) | PN6 ID (mm) | PN10 ID (mm) | PN16 ID (mm) |
|----|-----------------|-------------|--------------|--------------|
| 16 | 20 | N/A | 16.0 | 14.4 |
| 20 | 25 | 21.0 | 20.4 | 18.0 |
| 25 | 32 | 28.0 | 26.2 | 23.2 |
| 32 | 40 | 35.4 | 32.6 | 29.0 |
| 40 | 50 | 44.2 | 40.8 | 36.2 |
| 50 | 63 | 58.2 | 55.8 | 51.4 |
| 63 | 75 | 69.2 | 66.4 | 61.4 |
| 75 | 90 | 83.0 | 79.8 | 73.6 |
| 90 | 110 | 101.6 | 97.4 | 90.0 |
| 110 | 125 | 115.4 | 110.8 | 102.2 |
| 125 | 140 | 129.2 | 124.0 | 114.6 |
| 140 | 160 | 147.6 | 141.8 | 130.8 |
| 160 | 180 | 166.2 | 159.6 | 147.2 |

**Note**: DN16 PN6 is not commonly available (N/A in data).

## Implementation Plan

### Phase 1: Database Restructuring

#### File: `src/hydraulics/core/pipes.py`

**Current Structure**:
```python
HDPE_PIPES = {
    "N16": {"nominal": 16, "internal_diameter": 13.0},
    "N20": {"nominal": 20, "internal_diameter": 16.2},
    ...
}
```

**New Structure**:
```python
HDPE_PIPES = {
    "N16": {
        "nominal": 16,
        "pn_grades": {
            "PN10": {"internal_diameter": 16.0},
            "PN16": {"internal_diameter": 14.4}
        }
    },
    "N20": {
        "nominal": 20,
        "pn_grades": {
            "PN6": {"internal_diameter": 21.0},
            "PN10": {"internal_diameter": 20.4},
            "PN16": {"internal_diameter": 18.0}
        }
    },
    ...
}
```

**Changes Required**:
1. Restructure `HDPE_PIPES` dictionary to nest PN grades
2. Update `get_pipe_internal_diameter()` to accept PN grade parameter
3. Add `list_available_pn_grades(nominal_designation)` function
4. Add `get_default_pn_grade()` function (returns "PN10")
5. Update `get_adjacent_pipe_sizes()` to work with PN grades
6. Update `display_pipe_table()` to show all PN grades

**Backward Compatibility**:
- Make PN grade parameter optional (default="PN10")
- Support legacy pipe designation format ("N20" defaults to "N20-PN10")
- Add deprecation warning for old-style calls

### Phase 2: Model Updates

#### File: `src/hydraulics/models/artery.py`

**Changes to `DrippingArtery` class**:
1. Add `pn_grade` attribute to `__init__`
2. Update `__init__` signature: `def __init__(self, total_flow, pipe_designation, pn_grade="PN10")`
3. Pass PN grade to `get_pipe_internal_diameter()` in `calculate()` method
4. Update `calculate_with_dn_comparison()` to preserve PN grade across DN comparisons

**Key Logic for DN Comparison**:
```python
def calculate_with_dn_comparison(self):
    """Calculate with same PN grade across different DN sizes"""
    # Get adjacent DN sizes (2 smaller, 1 larger)
    adjacent_sizes = get_adjacent_pipe_sizes(self.pipe_designation, num_smaller=2, num_larger=1)

    # For each DN, use the SAME PN grade as user selected
    for dn in all_dns:
        diameter = get_pipe_internal_diameter(dn, self.pn_grade)  # <-- Pass PN grade
        result = self._calculate_for_diameter(diameter)
        ...
```

### Phase 3: UI Wizard Updates

#### File: `src/hydraulics/ui/wizards.py`

**New Functions**:
1. `select_pn_grade_interactive(pipe_designation)` - Interactive PN grade selector
2. Update `display_pipe_table()` to show PN variants

**Changes to `run_dripping_artery_wizard()`**:
```python
def run_dripping_artery_wizard():
    # ... existing code for total flow ...

    # Step 1: Select DN size
    pipe_designation = input("Enter pipe designation (e.g., N20): ").strip().upper()

    # Step 2: Select PN grade (NEW)
    pn_grade = select_pn_grade_interactive(pipe_designation)

    # Step 3: Create artery with PN grade
    artery = DrippingArtery(total_flow, pipe_designation, pn_grade)

    # ... rest of wizard ...
```

**PN Grade Selection Dialog**:
```
Available PN grades for N40:
  1. PN6  - ID: 44.2mm (Low pressure, larger flow capacity)
  2. PN10 - ID: 40.8mm (Standard pressure) [DEFAULT]
  3. PN16 - ID: 36.2mm (High pressure, smaller flow capacity)

Select PN grade (1-3) or press Enter for default [2]:
```

### Phase 4: Report Updates

#### File: `src/hydraulics/io/reports.py`

**Changes Required**:
1. Update markdown report to show PN grade in header
2. Update DN comparison table to show PN grade
3. Add PN grade explanation section

**Example Report Header**:
```markdown
# Hydraulics Calculation Report

## System Configuration
- **Pipe**: N40-PN10
- **Internal Diameter**: 40.8 mm
- **Pressure Rating**: PN10 (10 bar)
- **Total Flow**: 1500 l/h
...
```

**DN Comparison Table** (updated):
```
| DN Size | PN Grade | Int D (mm) | Full Calc | Christiansen | Simplified |
|---------|----------|------------|-----------|--------------|------------|
| N25     | PN10     | 26.2       | 0.1234    | 0.1245       | 0.1300     |
| N32     | PN10     | 32.6       | 0.0856    | 0.0862       | 0.0900     |
| N40     | PN10*    | 40.8       | 0.0567    | 0.0571       | 0.0600     |
| N50     | PN10     | 55.8       | 0.0234    | 0.0236       | 0.0250     |

* = Selected configuration
```

### Phase 5: Display Updates

#### File: `src/hydraulics/ui/wizards.py` (display functions)

**Update `display_results()`**:
- Show PN grade with pipe designation
- Update DN comparison table to include PN grade column

**Update `draw_artery_ascii()`**:
- Include PN grade in configuration summary (optional, if space permits)

### Phase 6: Testing

#### New Test File: `tests/test_pn_grades.py`

**Test Cases**:
1. **Test PN grade database integrity**
   - All DN sizes have at least PN10 and PN16
   - DN20-DN160 have PN6 variant
   - Internal diameters are consistent (smaller for higher PN)

2. **Test backward compatibility**
   - Old-style API calls default to PN10
   - Results match previous version for PN10

3. **Test DN comparison with PN grades**
   - Comparison uses same PN grade across all DN sizes
   - Results differ appropriately based on internal diameter

4. **Test edge cases**
   - Invalid PN grade raises ValueError
   - DN16 + PN6 raises ValueError (not available)
   - Empty/None PN grade defaults to PN10

#### Integration Test Update: `tests/integration/test_smoke.py`

**Add New Test**:
```python
def test_smoke_with_pn16():
    """Test known system with PN16 pipes (smaller ID = higher head loss)"""
    artery = DrippingArtery(1500, "N40", pn_grade="PN16")
    # Add same zones as original smoke test
    # Verify head loss is HIGHER than PN10 (due to smaller ID)
```

### Phase 7: Documentation

**Files to Update**:
1. `README.md` - Add PN grade feature to feature list
2. `CHANGELOG.md` - Add entry for v2.2.0 with PN grade support
3. `CLAUDE.md` - Update architecture section with PN grade info
4. `docs/USER_GUIDE.md` (if exists) - Add PN grade selection guide

**CHANGELOG.md Entry**:
```markdown
## [2.2.0] - 2026-02-XX

### Added
- PN grade support for HDPE pipes (PN6, PN10, PN16)
- Interactive PN grade selection in wizard
- PN grade preserved across DN comparison calculations
- Complete ISO 4427 pipe database (DN16-DN160, all PN grades)

### Changed
- HDPE_PIPES database restructured to include PN grade variants
- DrippingArtery constructor now accepts optional pn_grade parameter
- DN comparison table includes PN grade column
- Reports show PN grade information

### Backward Compatibility
- Default PN grade is PN10 (maintains previous behavior)
- Old-style API calls work without modification
```

## Implementation Checklist

- [ ] **Phase 1**: Database restructuring
  - [ ] Restructure HDPE_PIPES with PN grade nesting
  - [ ] Update get_pipe_internal_diameter() signature
  - [ ] Add list_available_pn_grades()
  - [ ] Add get_default_pn_grade()
  - [ ] Update get_adjacent_pipe_sizes()
  - [ ] Update display_pipe_table()
  - [ ] Add backward compatibility handling

- [ ] **Phase 2**: Model updates
  - [ ] Add pn_grade to DrippingArtery.__init__
  - [ ] Update calculate() to pass PN grade
  - [ ] Update calculate_with_dn_comparison() to preserve PN grade
  - [ ] Update _calculate_for_diameter() if needed

- [ ] **Phase 3**: UI wizard updates
  - [ ] Add select_pn_grade_interactive()
  - [ ] Update run_dripping_artery_wizard()
  - [ ] Update display_pipe_table()
  - [ ] Add PN grade help text

- [ ] **Phase 4**: Report updates
  - [ ] Update report header with PN grade
  - [ ] Update DN comparison table
  - [ ] Add PN grade explanation section

- [ ] **Phase 5**: Display updates
  - [ ] Update display_results() for PN grade
  - [ ] Update DN comparison table output
  - [ ] Update ASCII diagram (if space permits)

- [ ] **Phase 6**: Testing
  - [ ] Create test_pn_grades.py
  - [ ] Test database integrity
  - [ ] Test backward compatibility
  - [ ] Test DN comparison
  - [ ] Test edge cases
  - [ ] Update smoke test with PN16 variant
  - [ ] Run full test suite

- [ ] **Phase 7**: Documentation
  - [ ] Update README.md
  - [ ] Update CHANGELOG.md
  - [ ] Update CLAUDE.md
  - [ ] Update version numbers (v2.2.0)

## Risk Assessment

### Low Risk
- Database expansion (data is well-defined from ISO standard)
- UI additions (isolated new functions)
- Documentation updates

### Medium Risk
- Backward compatibility (mitigated by default parameter values)
- DN comparison logic (requires careful testing)

### High Risk
- None identified (feature is well-scoped and isolated)

## Rollback Plan

If issues arise:
1. Feature is opt-in (pn_grade parameter is optional)
2. Default behavior (PN10) matches previous version
3. Can disable PN selection in wizard, use PN10 only
4. Database can be reverted to flat structure with PN10 only

## Timeline Estimate

- Phase 1: 2-3 hours (database restructuring + backward compat)
- Phase 2: 1-2 hours (model updates)
- Phase 3: 2-3 hours (UI wizard updates + UX polish)
- Phase 4: 1 hour (report updates)
- Phase 5: 1 hour (display updates)
- Phase 6: 3-4 hours (comprehensive testing)
- Phase 7: 1 hour (documentation)

**Total**: 11-15 hours

## Success Criteria

1. Users can select PN6, PN10, or PN16 for supported DN sizes
2. DN comparison uses same PN grade across all DN sizes
3. Reports clearly show PN grade selection
4. All existing tests pass (backward compatibility)
5. New tests cover PN grade functionality
6. Documentation is complete and accurate

## References

- ISO 4427:2019 - Polyethylene (PE) pipes for water supply
- [Engineering ToolBox - PE Pipe Dimensions](https://www.engineeringtoolbox.com/pe-pipe-dimensions-d_321.html)
- Current codebase: src/hydraulics/core/pipes.py
- Current wizard: src/hydraulics/ui/wizards.py
- Current model: src/hydraulics/models/artery.py
