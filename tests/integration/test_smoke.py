#!/usr/bin/env python3
"""
Smoke test for the hydraulic calculation tool

Test case:
- 1500 l/h artery made of HDPE N20
- Transport zone 1: 10m
- Irrigation zone 1: 80m, dripping 500 l/h in 12 drippers
- Transport zone 2: 50m
- Irrigation zone 2: 160m, dripping 1000 l/h in 125 drippers
"""

from hydraulics.models import DrippingArtery, TransportZone, IrrigationZone
from hydraulics.io import config
from hydraulics.io.reports import generate_report
from hydraulics.core.properties import display_water_properties


def run_smoke_test():
    """Run the smoke test"""
    print("="*60)
    print("SMOKE TEST - Dripping Artery Calculator")
    print("="*60)

    # Configure units
    config.set_flow_unit("l/h")
    config.set_length_unit("m")
    config.set_pressure_unit("bar")

    # Display water properties
    display_water_properties()

    # Create the artery
    print("Test parameters:")
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

    # Calculate
    print("Calculating...")
    results = artery.calculate()

    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    print(f"\nPipe: {artery.pipe_designation}")
    print(f"Internal diameter: {results['diameter']*1000:.1f} mm")
    print(f"Total length: {results['total_length']:.2f} m")
    print(f"Initial flow: {artery.total_flow} {config.flow_unit}")

    print("\n--- Zone-by-Zone Results ---")
    for result in results['zones']:
        if result['zone_type'] == 'transport':
            print(f"\nTransport Zone {result['zone_number']}:")
            print(f"  Length: {result['length']:.2f} m")
            print(f"  Flow: {result['flow_m3s']*3600000:.1f} l/h ({result['velocity']:.3f} m/s)")
            print(f"  Reynolds: {result['reynolds']:.0f} ({result['flow_regime']})")
            print(f"  Friction factor: {result['friction_factor']:.6f}")
            print(f"  Head loss: {config.convert_pressure_from_m(result['head_loss']):.4f} {config.pressure_unit}")
            print(f"  Cumulative head loss: {config.convert_pressure_from_m(result['cumulative_head_loss']):.4f} {config.pressure_unit}")
            if not result['is_valid']:
                print("  [!] WARNING: Flow regime not suitable for Darcy-Weisbach!")
        else:
            print(f"\nIrrigation Zone {result['zone_number']}:")
            print(f"  Length: {result['length']:.2f} m")
            print(f"  Number of drippers: {result['num_drippers']}")
            print(f"  Flow (start -> end): {result['flow_start_m3s']*3600000:.1f} -> {result['flow_end_m3s']*3600000:.1f} l/h")
            print(f"  Head loss: {config.convert_pressure_from_m(result['head_loss']):.4f} {config.pressure_unit}")
            print(f"  Cumulative head loss: {config.convert_pressure_from_m(result['cumulative_head_loss']):.4f} {config.pressure_unit}")
            if not result['is_valid']:
                print("  [!] WARNING: Some segments have unsuitable flow regime!")

    print("\n--- Calculation Method Comparison ---")
    total_loss = config.convert_pressure_from_m(results['total_head_loss'])

    print(f"\n1. Full Segment-by-Segment Calculation:")
    print(f"   Total head loss: {total_loss:.4f} {config.pressure_unit}")

    if results.get('christiansen'):
        chris = results['christiansen']
        chris_loss = config.convert_pressure_from_m(chris['head_loss'])
        print(f"\n2. Christiansen Approximation:")
        print(f"   Christiansen coefficient (F): {chris['christiansen_coefficient']:.4f}")
        print(f"   Number of outlets: {chris['num_outlets']}")
        print(f"   Total head loss: {chris_loss:.4f} {config.pressure_unit}")

        difference = abs(total_loss - chris_loss)
        pct_diff = (difference / total_loss * 100) if total_loss > 0 else 0
        print(f"   Difference: {difference:.4f} {config.pressure_unit} ({pct_diff:.2f}%)")

    simplified_loss = config.convert_pressure_from_m(results['simplified_head_loss'])
    print(f"\n3. Simplified Model (constant flow):")
    print(f"   Total head loss: {simplified_loss:.4f} {config.pressure_unit}")
    print(f"   Difference from full: {abs(total_loss - simplified_loss):.4f} {config.pressure_unit} ({abs(total_loss - simplified_loss)/total_loss*100:.1f}%)")

    print("\n--- Dripper Pressure Check ---")
    print("Pressure-compensated drippers require 1.5-4 bar to function properly.")
    print(f"Required pump pressure range: {1.5 + total_loss:.2f} - {4.0 + total_loss:.2f} bar")

    # Check if drippers will work properly
    if total_loss > 2.5:
        print("[!] WARNING: Head loss is significant. Consider larger pipe diameter.")
    else:
        print("[OK] Head loss is within acceptable range for dripper operation.")

    # Generate report
    print("\n" + "="*60)
    print("Generating report...")
    report_path = generate_report(results, artery)
    print(f"[OK] Report saved to: {report_path}")
    print("="*60)

    return True


if __name__ == "__main__":
    try:
        run_smoke_test()
        print("\n[OK] SMOKE TEST PASSED")
    except Exception as e:
        print(f"\n[FAIL] SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
