#!/usr/bin/env python3
"""
Test script for pump pressure table feature

This script tests the new pump pressure range table functionality
that shows min/max pump pressures across different DN sizes.
"""

from hydraulics.models import DrippingArtery, TransportZone, IrrigationZone
from hydraulics.io import config
from hydraulics.io.reports import generate_report

def test_pump_pressure_table():
    """Test the pump pressure table feature"""
    print("="*60)
    print("TEST - Pump Pressure Table Feature")
    print("="*60)

    # Configure units
    config.set_flow_unit("l/h")
    config.set_length_unit("m")
    config.set_pressure_unit("bar")

    # Create a test artery (same as smoke test)
    print("\nTest parameters:")
    print("- Total flow: 1500 l/h")
    print("- Pipe: HDPE N20")
    print("- Transport zone 1: 10 m")
    print("- Irrigation zone 1: 80 m, 12 drippers, 500 l/h")
    print("- Transport zone 2: 50 m")
    print("- Irrigation zone 2: 160 m, 125 drippers, 1000 l/h")
    print()

    artery = DrippingArtery(total_flow=1500, pipe_designation="N20")

    # Add zones
    artery.add_zone(TransportZone(length=10))
    artery.add_zone(IrrigationZone(length=80, num_drippers=12, target_flow=500))
    artery.add_zone(TransportZone(length=50))
    artery.add_zone(IrrigationZone(length=160, num_drippers=125, target_flow=1000))

    # Calculate with DN comparison
    print("Calculating with DN comparison...")
    results_dict = artery.calculate_with_dn_comparison()

    selected_results = results_dict['selected']
    dn_comparison = results_dict['dn_comparison']

    # Display pump pressure table in console
    print("\n" + "="*60)
    print("PUMP PRESSURE TABLE")
    print("="*60)
    print(f"\n{'Pipe DN':<10} {'Internal D (mm)':<18} {'Min Pump (bar)':<18} {'Max Pump (bar)':<18}")
    print("-" * 64)

    for dn_result in dn_comparison:
        pipe_dn = dn_result['pipe_designation']
        internal_d = dn_result['internal_diameter_mm']
        head_loss = config.convert_pressure_from_m(dn_result['full_calculation'])

        min_pump = 1.5 + head_loss
        max_pump = 4.0 + head_loss

        marker = "**" if dn_result['is_selected'] else "  "
        print(f"{marker}{pipe_dn:<8}{marker} {internal_d:<18.1f} {min_pump:<18.2f} {max_pump:<18.2f}")

    print("\nNotes:")
    print("- ** indicates selected pipe")
    print("- Min pump: at 1.5 bar dripper pressure")
    print("- Max pump: at 4.0 bar dripper pressure")
    print("- Pump pressure = Dripper pressure + Head loss")

    # Generate full report
    print("\n" + "="*60)
    print("Generating full report with pump pressure table...")
    report_path = generate_report(selected_results, artery, dn_comparison=dn_comparison)
    print(f"[OK] Report saved to: {report_path}")
    print("="*60)

    # Verify the report contains the pump pressure table
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
        if "Required Pump Pressure by Pipe Diameter" in report_content:
            print("\n[OK] Pump pressure table found in report!")
        else:
            print("\n[FAIL] Pump pressure table NOT found in report!")
            return False

        if "Min Pump Pressure" in report_content and "Max Pump Pressure" in report_content:
            print("[OK] Table headers are correct!")
        else:
            print("[FAIL] Table headers are missing!")
            return False

    return True


if __name__ == "__main__":
    try:
        success = test_pump_pressure_table()
        if success:
            print("\n" + "="*60)
            print("[OK] PUMP PRESSURE TABLE TEST PASSED")
            print("="*60)
        else:
            print("\n[FAIL] PUMP PRESSURE TABLE TEST FAILED")
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
