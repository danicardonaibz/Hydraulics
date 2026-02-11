#!/usr/bin/env python3
"""
Smoke test for the DN comparison feature

Test case:
- 1500 l/h artery made of HDPE N40
- Transport zone 1: 10m
- Irrigation zone 1: 80m, dripping 500 l/h in 12 drippers
- Transport zone 2: 50m
- Irrigation zone 2: 160m, dripping 1000 l/h in 125 drippers

This test demonstrates the new multi-DN comparison feature that calculates
head losses for adjacent pipe sizes.
"""

from hydraulics.models import DrippingArtery, TransportZone, IrrigationZone
from hydraulics.io import config
from hydraulics.io.reports import generate_report
from hydraulics.core.properties import display_water_properties


def run_dn_comparison_test():
    """Run the DN comparison test"""
    print("="*60)
    print("DN COMPARISON FEATURE TEST")
    print("="*60)

    # Configure units
    config.set_flow_unit("l/h")
    config.set_length_unit("m")
    config.set_pressure_unit("bar")

    # Display water properties
    display_water_properties()

    # Create the artery (using N40 to have room for comparison)
    print("Test parameters:")
    print("- Total flow: 1500 l/h")
    print("- Pipe: HDPE N40 (will compare with N25, N32, N50)")
    print("- Transport zone 1: 10 m")
    print("- Irrigation zone 1: 80 m, 12 drippers, 500 l/h")
    print("- Transport zone 2: 50 m")
    print("- Irrigation zone 2: 160 m, 125 drippers, 1000 l/h")
    print()

    artery = DrippingArtery(total_flow=1500, pipe_designation="N40")

    # Add zones
    artery.add_zone(TransportZone(length=10))
    artery.add_zone(IrrigationZone(length=80, num_drippers=12, target_flow=500))
    artery.add_zone(TransportZone(length=50))
    artery.add_zone(IrrigationZone(length=160, num_drippers=125, target_flow=1000))

    # Calculate with DN comparison
    print("Calculating with DN comparison...")
    comparison_results = artery.calculate_with_dn_comparison()
    results = comparison_results['selected']
    dn_comparison = comparison_results['dn_comparison']

    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    print(f"\nPipe: {artery.pipe_designation}")
    print(f"Internal diameter: {results['diameter']*1000:.1f} mm")
    print(f"Total length: {results['total_length']:.2f} m")
    print(f"Initial flow: {artery.total_flow} {config.flow_unit}")

    # Display DN comparison table
    print("\n--- DN Size Comparison ---")
    print(f"{'Pipe DN':<10} {'Int D (mm)':<12} {'Full Calc':<15} {'Christiansen':<15} {'Simplified':<15}")
    print("-" * 70)
    for dn_result in dn_comparison:
        pipe_dn = dn_result['pipe_designation']
        internal_d = dn_result['internal_diameter_mm']
        full_loss = config.convert_pressure_from_m(dn_result['full_calculation'])
        christiansen_loss = config.convert_pressure_from_m(dn_result['christiansen']) if dn_result['christiansen'] else None
        simplified_loss = config.convert_pressure_from_m(dn_result['simplified'])

        chris_str = f"{christiansen_loss:.4f}" if christiansen_loss else "N/A"
        marker = " *" if dn_result['is_selected'] else ""

        print(f"{pipe_dn:<10}{marker} {internal_d:<12.1f} {full_loss:<15.4f} {chris_str:<15} {simplified_loss:<15.4f}")

    print(f"\n* = Selected pipe (all values in {config.pressure_unit})")

    # Display summary for selected pipe
    total_loss = config.convert_pressure_from_m(results['total_head_loss'])
    print(f"\n--- Selected Pipe ({artery.pipe_designation}) Summary ---")
    print(f"Total head loss (full calculation): {total_loss:.4f} {config.pressure_unit}")

    if results.get('christiansen'):
        chris = results['christiansen']
        chris_loss = config.convert_pressure_from_m(chris['head_loss'])
        difference = abs(total_loss - chris_loss)
        pct_diff = (difference / total_loss * 100) if total_loss > 0 else 0
        print(f"Christiansen approximation: {chris_loss:.4f} {config.pressure_unit} (diff: {pct_diff:.2f}%)")

    print("\n--- Dripper Pressure Check ---")
    print("Pressure-compensated drippers require 1.5-4 bar to function properly.")
    print(f"Required pump pressure range: {1.5 + total_loss:.2f} - {4.0 + total_loss:.2f} bar")

    # Generate report with DN comparison
    print("\n" + "="*60)
    print("Generating report with DN comparison table...")
    report_path = generate_report(results, artery, dn_comparison)
    print(f"[OK] Report saved to: {report_path}")
    print("="*60)

    # Verify DN comparison data integrity
    print("\n--- Verification ---")
    assert len(dn_comparison) == 4, f"Expected 4 DN sizes, got {len(dn_comparison)}"
    assert dn_comparison[0]['pipe_designation'] == 'N25', "First DN should be N25"
    assert dn_comparison[1]['pipe_designation'] == 'N32', "Second DN should be N32"
    assert dn_comparison[2]['pipe_designation'] == 'N40', "Third DN should be N40 (selected)"
    assert dn_comparison[3]['pipe_designation'] == 'N50', "Fourth DN should be N50"
    assert dn_comparison[2]['is_selected'] == True, "N40 should be marked as selected"

    # Verify that smaller DN has higher loss
    assert dn_comparison[0]['full_calculation'] > dn_comparison[1]['full_calculation'], \
        "Smaller DN should have higher head loss"
    assert dn_comparison[1]['full_calculation'] > dn_comparison[2]['full_calculation'], \
        "Smaller DN should have higher head loss"
    assert dn_comparison[2]['full_calculation'] > dn_comparison[3]['full_calculation'], \
        "Smaller DN should have higher head loss"

    print("[OK] All DN comparison data verified")

    return True


if __name__ == "__main__":
    try:
        run_dn_comparison_test()
        print("\n[OK] DN COMPARISON TEST PASSED")
    except Exception as e:
        print(f"\n[FAIL] DN COMPARISON TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
