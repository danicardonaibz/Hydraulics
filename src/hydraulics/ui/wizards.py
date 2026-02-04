"""Interactive wizards for user input"""

from hydraulics.models.zones import TransportZone, IrrigationZone
from hydraulics.models.artery import DrippingArtery
from hydraulics.core.pipes import list_available_pipes, display_pipe_table
from hydraulics.core.properties import display_water_properties
from hydraulics.io.config import config
from hydraulics.io.reports import generate_report


def get_float_input(prompt, min_value=None, max_value=None, allow_zero=True):
    """
    Get validated float input from user with retry logic

    Args:
        prompt: Prompt to display to user
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        allow_zero: Whether zero is allowed

    Returns:
        Valid float value
    """
    while True:
        try:
            value = float(input(prompt))

            # Validate range
            if not allow_zero and value == 0:
                print("  [!] Error: Value cannot be zero. Please try again.")
                continue

            if min_value is not None and value < min_value:
                print(f"  [!] Error: Value must be at least {min_value}. Please try again.")
                continue

            if max_value is not None and value > max_value:
                print(f"  [!] Error: Value must be at most {max_value}. Please try again.")
                continue

            return value

        except ValueError:
            print("  [!] Error: Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            raise


def get_int_input(prompt, min_value=None, max_value=None):
    """
    Get validated integer input from user with retry logic

    Args:
        prompt: Prompt to display to user
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        Valid integer value
    """
    while True:
        try:
            value = int(input(prompt))

            # Validate range
            if min_value is not None and value < min_value:
                print(f"  [!] Error: Value must be at least {min_value}. Please try again.")
                continue

            if max_value is not None and value > max_value:
                print(f"  [!] Error: Value must be at most {max_value}. Please try again.")
                continue

            return value

        except ValueError:
            print("  [!] Error: Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            raise


def draw_artery_ascii(artery, show_flows=True):
    """
    Draw ASCII diagram of the artery configuration

    Args:
        artery: DrippingArtery object
        show_flows: Whether to show flow information

    Returns:
        String containing ASCII diagram
    """
    if not artery.zones:
        return "  (No zones defined yet)"

    lines = []
    lines.append("\n  Artery Configuration:")
    lines.append("  " + "="*56)

    # Build diagram
    top_line = "  PUMP <-"
    main_line = "         "
    bottom_line = "         "

    cumulative_flow = artery.total_flow if show_flows else None

    for i, zone in enumerate(artery.zones):
        zone_num = i + 1

        if zone.zone_type == "transport":
            # Transport zone representation
            length_display = int(zone.length) if zone.length < 100 else 99
            segment_width = max(8, min(length_display // 5, 20))
            segment = "-" * segment_width

            top_line += segment + "-"
            main_line += f" T{zone_num}({zone.length}{config.length_unit}) "
            if cumulative_flow is not None:
                bottom_line += f" {cumulative_flow:.0f}{config.flow_unit} ".center(len(segment) + 1)
            else:
                bottom_line += " " * (len(segment) + 1)

        else:  # irrigation zone
            # Irrigation zone representation
            num_drippers = zone.num_drippers
            segment_width = max(12, min(num_drippers * 2, 30))

            # Create dripper visualization
            dripper_spacing = max(1, segment_width // num_drippers)
            segment = ""
            for j in range(num_drippers):
                if j == 0:
                    segment += "+"
                else:
                    segment += "-" * (dripper_spacing - 1) + "+"
            segment += "-" * (segment_width - len(segment))

            top_line += segment + "-"
            main_line += f" I{zone_num}({zone.num_drippers}d,{zone.length}{config.length_unit}) "

            if cumulative_flow is not None:
                flow_start = cumulative_flow
                flow_end = cumulative_flow - zone.target_flow
                bottom_line += f" {flow_start:.0f}->{flow_end:.0f}{config.flow_unit} ".center(len(segment) + 1)
                cumulative_flow = flow_end
            else:
                bottom_line += " " * (len(segment) + 1)

    lines.append(top_line)
    lines.append(main_line)
    if show_flows:
        lines.append(bottom_line)

    lines.append("  " + "="*56)
    lines.append("  Legend: T# = Transport zone, I#(Xd,Ym) = Irrigation zone")
    lines.append("          + = Dripper location")

    return "\n".join(lines)


def display_zone_list(artery):
    """Display numbered list of zones"""
    print("\n  Current Zones:")
    print("  " + "-"*56)

    if not artery.zones:
        print("  (No zones defined yet)")
    else:
        total_irrigation_flow = 0
        for i, zone in enumerate(artery.zones, 1):
            if zone.zone_type == "transport":
                print(f"  {i}. Transport: {zone.length} {config.length_unit}")
            else:
                print(f"  {i}. Irrigation: {zone.length} {config.length_unit}, "
                      f"{zone.num_drippers} drippers, {zone.target_flow} {config.flow_unit}")
                total_irrigation_flow += zone.target_flow

        print("  " + "-"*56)
        print(f"  Total flow specified: {artery.total_flow} {config.flow_unit}")
        print(f"  Sum of irrigation flows: {total_irrigation_flow} {config.flow_unit}")

        # Flow balance check
        flow_diff = abs(artery.total_flow - total_irrigation_flow)
        if flow_diff > artery.total_flow * 0.01:  # More than 1% difference
            print(f"  [!] WARNING: Flow imbalance of {flow_diff:.1f} {config.flow_unit}")


def review_and_edit_artery(artery):
    """
    Allow user to review and edit the artery configuration before calculation

    Args:
        artery: DrippingArtery object

    Returns:
        True if user wants to proceed with calculation, False otherwise
    """
    while True:
        print("\n" + "="*60)
        print("REVIEW ARTERY CONFIGURATION")
        print("="*60)

        # Show ASCII diagram
        print(draw_artery_ascii(artery, show_flows=True))

        # Show detailed list
        display_zone_list(artery)

        print("\n  Options:")
        print("  [C] Calculate - Proceed with calculation")
        print("  [A] Add zone - Add another zone")
        print("  [E] Edit zone - Modify an existing zone")
        print("  [D] Delete zone - Remove a zone")
        print("  [R] Restart - Clear all zones and start over")
        print("  [Q] Quit - Exit without calculating")

        choice = input("\n  Select option: ").strip().upper()

        if choice == 'C':
            if not artery.zones:
                print("  [!] Error: No zones defined. Please add at least one zone.")
                continue
            return True

        elif choice == 'A':
            add_zone_interactive(artery)

        elif choice == 'E':
            if not artery.zones:
                print("  [!] No zones to edit.")
                continue
            edit_zone_interactive(artery)

        elif choice == 'D':
            if not artery.zones:
                print("  [!] No zones to delete.")
                continue
            delete_zone_interactive(artery)

        elif choice == 'R':
            confirm = input("  Are you sure you want to clear all zones? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                artery.zones.clear()
                print("  [OK] All zones cleared.")

        elif choice == 'Q':
            return False

        else:
            print("  [!] Invalid option. Please try again.")


def add_zone_interactive(artery):
    """Interactively add a zone to the artery"""
    print("\n  Add Zone")
    print("  --------")
    print("  Type: [T]ransport, [I]rrigation, or [C]ancel")

    zone_type = input("  > ").strip().lower()

    # Handle abbreviations
    if zone_type in ['t', 'transport']:
        length = get_float_input(f"  Enter length (in {config.length_unit}): ", min_value=0.001, allow_zero=False)
        artery.add_zone(TransportZone(length))
        print(f"  [OK] Added transport zone: {length} {config.length_unit}")

    elif zone_type in ['i', 'irrigation']:
        length = get_float_input(f"  Enter length (in {config.length_unit}): ", min_value=0.001, allow_zero=False)
        num_drippers = get_int_input("  Enter number of drippers: ", min_value=1)
        target_flow = get_float_input(f"  Enter target flow for this zone (in {config.flow_unit}): ",
                                      min_value=0.001, allow_zero=False)
        artery.add_zone(IrrigationZone(length, num_drippers, target_flow))
        print(f"  [OK] Added irrigation zone: {length} {config.length_unit}, {num_drippers} drippers, {target_flow} {config.flow_unit}")

    elif zone_type in ['c', 'cancel']:
        print("  [OK] Cancelled.")
    else:
        print("  [!] Invalid zone type.")


def edit_zone_interactive(artery):
    """Interactively edit a zone"""
    zone_num = get_int_input("  Enter zone number to edit: ", min_value=1, max_value=len(artery.zones))
    zone_idx = zone_num - 1
    zone = artery.zones[zone_idx]

    print(f"\n  Editing Zone {zone_num}:")
    if zone.zone_type == "transport":
        print(f"  Current: Transport, {zone.length} {config.length_unit}")
        new_length = get_float_input(f"  Enter new length (or press Enter to keep {zone.length}): ",
                                     min_value=0.001, allow_zero=False)
        zone.length = new_length
        print(f"  [OK] Updated zone {zone_num}")
    else:
        print(f"  Current: Irrigation, {zone.length} {config.length_unit}, {zone.num_drippers} drippers, {zone.target_flow} {config.flow_unit}")

        new_length = get_float_input(f"  Enter new length (or 0 to keep {zone.length}): ", min_value=0)
        if new_length > 0:
            zone.length = new_length

        new_drippers = get_int_input(f"  Enter new number of drippers (or 0 to keep {zone.num_drippers}): ", min_value=0)
        if new_drippers > 0:
            zone.num_drippers = new_drippers

        new_flow = get_float_input(f"  Enter new target flow (or 0 to keep {zone.target_flow}): ", min_value=0)
        if new_flow > 0:
            zone.target_flow = new_flow

        print(f"  [OK] Updated zone {zone_num}")


def delete_zone_interactive(artery):
    """Interactively delete a zone"""
    zone_num = get_int_input("  Enter zone number to delete: ", min_value=1, max_value=len(artery.zones))
    zone_idx = zone_num - 1

    zone = artery.zones[zone_idx]
    if zone.zone_type == "transport":
        print(f"  Deleting: Transport zone, {zone.length} {config.length_unit}")
    else:
        print(f"  Deleting: Irrigation zone, {zone.length} {config.length_unit}, {zone.num_drippers} drippers")

    confirm = input("  Confirm deletion? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        artery.zones.pop(zone_idx)
        print(f"  [OK] Zone {zone_num} deleted.")
    else:
        print("  [OK] Deletion cancelled.")


def run_dripping_artery_wizard():
    """Interactive wizard for dripping artery calculation"""
    print("\n" + "="*60)
    print("DRIPPING ARTERY CALCULATOR")
    print("="*60)

    # Display water properties
    display_water_properties()

    # Display available pipes
    display_pipe_table()

    # Get total flow with validation
    total_flow = get_float_input(
        f"Enter the total flow at the pump (in {config.flow_unit}): ",
        min_value=0.001,
        allow_zero=False
    )

    # Get pipe designation with validation
    while True:
        print(f"\nAvailable pipes: {', '.join(list_available_pipes())}")
        pipe_designation = input("Enter pipe designation (e.g., N20): ").strip().upper()

        if pipe_designation in list_available_pipes():
            break
        else:
            print(f"[!] Invalid pipe designation: {pipe_designation}")
            print("    Please choose from the available pipes listed above.")

    # Create artery
    artery = DrippingArtery(total_flow, pipe_designation)

    # Add zones with abbreviation support
    print("\n" + "="*60)
    print("ZONE INPUT")
    print("="*60)
    print("Enter zones in sequence from pump to end.")
    print("Type: [T]ransport, [I]rrigation, or [D]one")
    print("(You can use abbreviations: t, i, d)")

    while True:
        print(f"\nZone {len(artery.zones) + 1}")
        zone_type = input("Enter type (t/i/d): ").strip().lower()

        # Handle abbreviations and full names
        if zone_type in ['d', 'done']:
            break

        elif zone_type in ['t', 'transport']:
            length = get_float_input(
                f"  Enter length (in {config.length_unit}): ",
                min_value=0.001,
                allow_zero=False
            )
            artery.add_zone(TransportZone(length))
            print(f"  [OK] Added transport zone: {length} {config.length_unit}")

        elif zone_type in ['i', 'irrigation']:
            length = get_float_input(
                f"  Enter length (in {config.length_unit}): ",
                min_value=0.001,
                allow_zero=False
            )
            num_drippers = get_int_input(
                "  Enter number of drippers: ",
                min_value=1
            )
            target_flow = get_float_input(
                f"  Enter target flow for this zone (in {config.flow_unit}): ",
                min_value=0.001,
                allow_zero=False
            )
            artery.add_zone(IrrigationZone(length, num_drippers, target_flow))
            print(f"  [OK] Added irrigation zone: {length} {config.length_unit}, "
                  f"{num_drippers} drippers, {target_flow} {config.flow_unit}")

        else:
            print("  [!] Invalid input. Please enter 't' (transport), 'i' (irrigation), or 'd' (done).")

    # Review and edit phase
    if not review_and_edit_artery(artery):
        print("\nCalculation cancelled by user.")
        return

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
        print(f"\n[!] Error: {e}")
        print("    Please check your input values and try again.")
    except Exception as e:
        print(f"\n[!] Calculation error: {e}")
        import traceback
        traceback.print_exc()


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
