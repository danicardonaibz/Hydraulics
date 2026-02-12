#!/usr/bin/env python3
"""
Test script for pump pressure table with different unit systems
"""

from hydraulics.models import DrippingArtery, TransportZone, IrrigationZone
from hydraulics.io import config
from hydraulics.io.reports import generate_report

def test_with_units(pressure_unit):
    """Test pump pressure table with specific pressure unit"""
    print(f"\n{'='*60}")
    print(f"Testing with pressure unit: {pressure_unit}")
    print(f"{'='*60}")

    # Configure units
    config.set_flow_unit("l/h")
    config.set_length_unit("m")
    config.set_pressure_unit(pressure_unit)

    # Create test artery
    artery = DrippingArtery(total_flow=1500, pipe_designation="N20")
    artery.add_zone(TransportZone(length=10))
    artery.add_zone(IrrigationZone(length=80, num_drippers=12, target_flow=500))
    artery.add_zone(TransportZone(length=50))
    artery.add_zone(IrrigationZone(length=160, num_drippers=125, target_flow=1000))

    # Calculate with DN comparison
    results_dict = artery.calculate_with_dn_comparison()
    dn_comparison = results_dict['dn_comparison']

    # Display pump pressure table
    print(f"\n{'Pipe DN':<10} {'Min Pump':<15} {'Max Pump':<15}")
    print("-" * 40)

    for dn_result in dn_comparison:
        pipe_dn = dn_result['pipe_designation']
        head_loss = config.convert_pressure_from_m(dn_result['full_calculation'])

        # Convert dripper pressures to current unit
        if pressure_unit == "bar":
            min_dripper = 1.5
            max_dripper = 4.0
        elif pressure_unit == "mwc":
            min_dripper = 1.5 / 0.0980665  # bar to mwc
            max_dripper = 4.0 / 0.0980665
        elif pressure_unit == "atm":
            min_dripper = 1.5 / 1.01325  # bar to atm
            max_dripper = 4.0 / 1.01325

        min_pump = min_dripper + head_loss
        max_pump = max_dripper + head_loss

        marker = "**" if dn_result['is_selected'] else "  "
        print(f"{marker}{pipe_dn:<8}{marker} {min_pump:<15.2f} {max_pump:<15.2f}")

    print(f"\nUnit: {pressure_unit}")
    return True


if __name__ == "__main__":
    try:
        # Test with all supported pressure units
        for unit in ["bar", "mwc", "atm"]:
            test_with_units(unit)

        print("\n" + "="*60)
        print("[OK] ALL UNIT TESTS PASSED")
        print("="*60)
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
