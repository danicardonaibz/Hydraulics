"""Interactive wizards for user input"""

from hydraulics.models.zones import TransportZone, IrrigationZone
from hydraulics.models.artery import DrippingArtery
from hydraulics.core.pipes import list_available_pipes, display_pipe_table
from hydraulics.core.properties import display_water_properties
from hydraulics.io.config import config
from hydraulics.io.reports import generate_report


def run_dripping_artery_wizard():
    """Interactive wizard for dripping artery calculation"""
    print("\n" + "="*60)
    print("DRIPPING ARTERY CALCULATOR")
    print("="*60)

    # Display water properties
    display_water_properties()

    # Display available pipes
    display_pipe_table()

    # Get total flow
    print(f"Enter the total flow at the pump (in {config.flow_unit}):")
    total_flow = float(input("> "))

    # Get pipe designation
    print(f"\nAvailable pipes: {', '.join(list_available_pipes())}")
    print("Enter pipe designation (e.g., N20):")
    pipe_designation = input("> ").strip().upper()

    if pipe_designation not in list_available_pipes():
        print(f"Invalid pipe designation: {pipe_designation}")
        return

    # Create artery
    artery = DrippingArtery(total_flow, pipe_designation)

    # Add zones
    print("\n--- Zone Input ---")
    print("Enter zones in sequence from pump to end.")
    print("Type 'transport' for transport zone, 'irrigation' for irrigation zone, 'done' to finish.")

    zone_count = 0
    while True:
        zone_count += 1
        print(f"\nZone {zone_count} - Enter type (transport/irrigation/done):")
        zone_type = input("> ").strip().lower()

        if zone_type == "done":
            break
        elif zone_type == "transport":
            print(f"Enter length (in {config.length_unit}):")
            length = float(input("> "))
            artery.add_zone(TransportZone(length))
            print(f"[OK] Added transport zone: {length} {config.length_unit}")

        elif zone_type == "irrigation":
            print(f"Enter length (in {config.length_unit}):")
            length = float(input("> "))
            print("Enter number of drippers (equidistant):")
            num_drippers = int(input("> "))
            print(f"Enter target flow for this zone (in {config.flow_unit}):")
            target_flow = float(input("> "))
            artery.add_zone(IrrigationZone(length, num_drippers, target_flow))
            print(f"[OK] Added irrigation zone: {length} {config.length_unit}, {num_drippers} drippers, {target_flow} {config.flow_unit}")
        else:
            print("Invalid input. Please enter 'transport', 'irrigation', or 'done'.")
            zone_count -= 1

    # Validate and calculate
    try:
        print("\n" + "="*60)
        print("CALCULATING...")
        print("="*60)

        results = artery.calculate()

        # Display results
        display_results(results, artery)

        # Generate report
        print("\nGenerating report...")
        report_path = generate_report(results, artery)
        print(f"[OK] Report saved to: {report_path}")

    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nCalculation error: {e}")


def display_results(results, artery):
    """Display calculation results"""
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
            print(f"  Head loss: {config.convert_pressure_from_m(result['head_loss']):.3f} {config.pressure_unit}")
            print(f"  Cumulative head loss: {config.convert_pressure_from_m(result['cumulative_head_loss']):.3f} {config.pressure_unit}")
            if not result['is_valid']:
                print("  [!] WARNING: Flow regime not suitable for Darcy-Weisbach!")
        else:
            print(f"\nIrrigation Zone {result['zone_number']}:")
            print(f"  Length: {result['length']:.2f} m")
            print(f"  Number of drippers: {result['num_drippers']}")
            print(f"  Flow (start -> end): {result['flow_start_m3s']*3600000:.1f} -> {result['flow_end_m3s']*3600000:.1f} l/h")
            print(f"  Head loss: {config.convert_pressure_from_m(result['head_loss']):.3f} {config.pressure_unit}")
            print(f"  Cumulative head loss: {config.convert_pressure_from_m(result['cumulative_head_loss']):.3f} {config.pressure_unit}")
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
        print(f"\n   Difference: {difference:.4f} {config.pressure_unit} ({pct_diff:.2f}%)")

    simplified_loss = config.convert_pressure_from_m(results['simplified_head_loss'])
    print(f"\n3. Simplified Model (constant flow):")
    print(f"   Total head loss: {simplified_loss:.3f} {config.pressure_unit}")
    print(f"   Difference from full calculation: {abs(total_loss - simplified_loss):.3f} {config.pressure_unit} ({abs(total_loss - simplified_loss)/total_loss*100:.1f}%)")
