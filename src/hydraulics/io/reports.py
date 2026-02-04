"""Report generator - creates markdown reports with installation details"""

import os
from datetime import datetime
from hydraulics.io.config import config
from hydraulics.core.properties import WaterProperties


def generate_ascii_diagram(artery):
    """Generate ASCII diagram of the installation"""
    diagram = []
    diagram.append("\n```")
    diagram.append("Installation Diagram:")
    diagram.append("")

    # Build diagram
    top_line = "         "
    main_line = "PUMP <- "
    bottom_line = "         "
    labels_line = "         "

    for i, zone in enumerate(artery.zones):
        zone_num = i + 1

        if zone.zone_type == "transport":
            # Transport zone
            length = int(zone.length)
            segment = "-" * max(10, length // 5)
            top_line += " " * len(segment) + "  "
            main_line += segment + "--"
            bottom_line += " " * len(segment) + "  "
            labels_line += f"T{zone_num}".center(len(segment)) + "  "
        else:
            # Irrigation zone
            num_drippers = zone.num_drippers
            segment_width = max(3, 15 // num_drippers)
            segment = ""
            top_segment = ""
            bottom_segment = ""

            for j in range(num_drippers):
                segment += "+" + "-" * (segment_width - 1)
                top_segment += "|" + " " * (segment_width - 1)
                bottom_segment += "d" + " " * (segment_width - 1)

            top_line += top_segment + "  "
            main_line += segment + "--"
            bottom_line += bottom_segment + "  "
            labels_line += f"I{zone_num}({num_drippers}d)".center(len(segment)) + "  "

    diagram.append(labels_line)
    diagram.append(top_line)
    diagram.append(main_line)
    diagram.append(bottom_line)
    diagram.append("")
    diagram.append("Legend:")
    diagram.append("  T# = Transport zone #")
    diagram.append("  I#(Xd) = Irrigation zone # with X drippers")
    diagram.append("  + = Dripper connection point")
    diagram.append("  d = Dripper")
    diagram.append("```")

    return "\n".join(diagram)


def generate_report(results, artery):
    """Generate markdown report"""

    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dripping_artery_report_{timestamp}.md"
    filepath = os.path.join(reports_dir, filename)

    # Build report content
    lines = []
    lines.append("# Dripping Artery Hydraulic Calculation Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n---\n")

    # Installation overview
    lines.append("## Installation Overview")
    lines.append(f"- **Pipe designation:** {artery.pipe_designation}")
    lines.append(f"- **Internal diameter:** {results['diameter']*1000:.1f} mm")
    lines.append(f"- **Total length:** {results['total_length']:.2f} m")
    lines.append(f"- **Initial flow:** {artery.total_flow} {config.flow_unit}")
    lines.append(f"- **Number of zones:** {len(artery.zones)}")

    # ASCII diagram
    lines.append("\n## Installation Diagram")
    lines.append(generate_ascii_diagram(artery))

    # Water properties
    lines.append("\n## Water Properties (NIST data at 20°C)")
    lines.append(f"- **Density (ρ):** {WaterProperties.density} kg/m³")
    lines.append(f"- **Dynamic viscosity (μ):** {WaterProperties.dynamic_viscosity*1000:.3f} mPa·s")
    lines.append(f"- **Kinematic viscosity (ν):** {WaterProperties.kinematic_viscosity*1e6:.3f} mm²/s")
    lines.append(f"- **Gravitational acceleration (g):** {WaterProperties.g} m/s²")
    lines.append(f"- **HDPE pipe roughness (ε):** {WaterProperties.hdpe_roughness*1000:.4f} mm")

    # Zone-by-zone results
    lines.append("\n## Zone-by-Zone Analysis")

    for result in results['zones']:
        if result['zone_type'] == 'transport':
            lines.append(f"\n### Transport Zone {result['zone_number']}")
            lines.append(f"- **Length:** {result['length']:.2f} m")
            lines.append(f"- **Flow rate:** {result['flow_m3s']*3600000:.1f} l/h")
            lines.append(f"- **Velocity:** {result['velocity']:.3f} m/s")
            lines.append(f"- **Reynolds number:** {result['reynolds']:.0f}")
            lines.append(f"- **Flow regime:** {result['flow_regime']}")
            lines.append(f"- **Friction factor (f):** {result['friction_factor']:.6f}")
            lines.append(f"- **Head loss:** {config.convert_pressure_from_m(result['head_loss']):.3f} {config.pressure_unit}")
            lines.append(f"- **Cumulative head loss:** {config.convert_pressure_from_m(result['cumulative_head_loss']):.3f} {config.pressure_unit}")
            lines.append(f"- **Cumulative length:** {result['cumulative_length']:.2f} m")
            if not result['is_valid']:
                lines.append(f"- ⚠️ **WARNING:** Flow regime not suitable for Darcy-Weisbach equation")
        else:
            lines.append(f"\n### Irrigation Zone {result['zone_number']}")
            lines.append(f"- **Length:** {result['length']:.2f} m")
            lines.append(f"- **Number of drippers:** {result['num_drippers']}")
            lines.append(f"- **Flow at start:** {result['flow_start_m3s']*3600000:.1f} l/h")
            lines.append(f"- **Flow at end:** {result['flow_end_m3s']*3600000:.1f} l/h")
            lines.append(f"- **Total zone flow:** {(result['flow_start_m3s']-result['flow_end_m3s'])*3600000:.1f} l/h")
            lines.append(f"- **Flow per dripper:** {(result['flow_start_m3s']-result['flow_end_m3s'])/result['num_drippers']*3600000:.1f} l/h")
            lines.append(f"- **Head loss:** {config.convert_pressure_from_m(result['head_loss']):.3f} {config.pressure_unit}")
            lines.append(f"- **Cumulative head loss:** {config.convert_pressure_from_m(result['cumulative_head_loss']):.3f} {config.pressure_unit}")
            lines.append(f"- **Cumulative length:** {result['cumulative_length']:.2f} m")
            if not result['is_valid']:
                lines.append(f"- ⚠️ **WARNING:** Some segments have unsuitable flow regime")

            # Segment details
            lines.append(f"\n#### Segment Details")
            lines.append(f"\n| Segment | Flow (l/h) | Velocity (m/s) | Reynolds | Valid | Method | Friction Factor | Head Loss ({config.pressure_unit}) |")
            lines.append("|---------|-----------|----------------|----------|-------|--------|-----------------|------------|")
            for seg in result['segments']:
                flow_lh = seg['flow_m3s'] * 3600000
                head_loss_unit = config.convert_pressure_from_m(seg['head_loss'])
                valid_flag = "✓" if seg['is_valid'] else "✗"
                method = seg.get('friction_method', 'Colebrook-White')
                lines.append(f"| {seg['segment']} | {flow_lh:.1f} | {seg['velocity']:.3f} | {seg['reynolds']:.0f} | {valid_flag} | {method} | {seg['friction_factor']:.6f} | {head_loss_unit:.4f} |")

            lines.append(f"\n**Note:** Valid = ✓ (Turbulent, Re > 4000) or ✗ (Laminar/Transitional, Re < 4000).")
            lines.append(f"Method indicates friction factor calculation: 'Laminar (f=64/Re)' for Re < 2000, 'Colebrook-White' otherwise.")

    # Calculation Method Comparison
    lines.append("\n## Calculation Method Comparison")
    lines.append("\nTwo methods have been used to calculate the total head loss in this irrigation artery:")

    total_loss = config.convert_pressure_from_m(results['total_head_loss'])
    lines.append(f"\n### 1. Full Segment-by-Segment Calculation")
    lines.append(f"This method calculates the friction loss for each pipe segment individually,")
    lines.append(f"accounting for the decreasing flow as water exits through each dripper outlet.")
    lines.append(f"- **Total head loss:** {total_loss:.4f} {config.pressure_unit}")

    if results.get('christiansen'):
        chris = results['christiansen']
        chris_loss = config.convert_pressure_from_m(chris['head_loss'])
        lines.append(f"\n### 2. Christiansen Approximation")
        lines.append(f"This simplified method uses the Christiansen reduction factor to estimate")
        lines.append(f"friction losses in pipes with uniformly spaced outlets.")
        lines.append(f"- **Christiansen coefficient (F):** {chris['christiansen_coefficient']:.4f}")
        lines.append(f"- **Number of outlets:** {chris['num_outlets']}")
        lines.append(f"- **Flow regime exponent (m):** {chris['m_exponent']:.1f} (Darcy-Weisbach turbulent)")
        lines.append(f"- **Unit loss:** {chris['unit_loss_m_per_m']*1000:.4f} m/km")
        lines.append(f"- **Total head loss:** {chris_loss:.4f} {config.pressure_unit}")

        # Comparison
        difference = abs(total_loss - chris_loss)
        pct_diff = (difference / total_loss * 100) if total_loss > 0 else 0
        lines.append(f"\n### Comparison")
        lines.append(f"- **Difference:** {difference:.4f} {config.pressure_unit} ({pct_diff:.2f}%)")
        if pct_diff < 5:
            lines.append(f"- The Christiansen approximation provides excellent agreement with the full calculation.")
        elif pct_diff < 10:
            lines.append(f"- The Christiansen approximation provides good agreement with the full calculation.")
        else:
            lines.append(f"- The Christiansen approximation shows significant deviation, likely due to varying flow regimes along the artery.")

    # Summary
    lines.append("\n## Summary")
    total_loss = config.convert_pressure_from_m(results['total_head_loss'])
    simplified_loss = config.convert_pressure_from_m(results['simplified_head_loss'])
    difference_abs = abs(total_loss - simplified_loss)
    difference_pct = difference_abs / total_loss * 100 if total_loss > 0 else 0

    lines.append(f"- **Total head loss (accurate model):** {total_loss:.3f} {config.pressure_unit}")
    lines.append(f"- **Total head loss (simplified model):** {simplified_loss:.3f} {config.pressure_unit}")
    lines.append(f"- **Difference:** {difference_abs:.3f} {config.pressure_unit} ({difference_pct:.1f}%)")

    lines.append("\n### Pressure Requirements")
    lines.append(f"For pressure-compensated drippers operating at 1.5-4 bar:")
    pump_pressure_min = 1.5 + total_loss
    pump_pressure_max = 4.0 + total_loss
    lines.append(f"- **Minimum pump pressure:** {pump_pressure_min:.2f} {config.pressure_unit}")
    lines.append(f"- **Maximum pump pressure:** {pump_pressure_max:.2f} {config.pressure_unit}")

    # Equations used
    lines.append("\n## Calculation Methods")

    lines.append("\n### Darcy-Weisbach Equation")
    lines.append("$$h_f = f \\cdot \\frac{L}{D} \\cdot \\frac{v^2}{2g}$$")

    lines.append("\n### Friction Factor Calculation")
    lines.append("\n**For Laminar Flow (Re < 2000):**")
    lines.append("$$f = \\frac{64}{Re}$$")

    lines.append("\n**For Transitional and Turbulent Flow (Re ≥ 2000):**")
    lines.append("\nColebrook-White Equation:")
    lines.append("$$\\frac{1}{\\sqrt{f}} = -2 \\log_{10} \\left( \\frac{\\epsilon}{3.7 D} + \\frac{2.51}{Re \\sqrt{f}} \\right)$$")
    lines.append("\nSolved using Newton-Raphson method. Colebrook-White is used for transitional flow (Re < 4000) as it provides conservative (higher) friction factors.")

    lines.append("\n### Reynolds Number")
    lines.append("$$Re = \\frac{v \\cdot D}{\\nu}$$")

    lines.append("\n### Christiansen Approximation")
    lines.append("\nFor irrigation laterals with uniformly spaced outlets:")
    lines.append("$$h_f = F \\cdot L \\cdot J$$")
    lines.append("\nWhere:")
    lines.append("- F = Christiansen reduction factor")
    lines.append("- L = Total pipe length")
    lines.append("- J = Unit friction loss (calculated with full flow)")
    lines.append("\n**Christiansen Coefficient:**")
    lines.append("$$F = \\frac{1}{m+1} + \\frac{1}{2N} + \\frac{\\sqrt{m-1}}{6N^2}$$")
    lines.append("\nWhere:")
    lines.append("- N = Number of outlets")
    lines.append("- m = Flow regime exponent (m=2 for Darcy-Weisbach turbulent, m=1.75 for Hazen-Williams)")

    lines.append("\n---")
    lines.append("\n*Report generated by Hydraulic Piping Calculation Tool*")

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return filepath
