"""HDPE pipe specifications - European nominal diameters"""

# HDPE Pipe specifications (nominal diameter: internal diameter in mm)
# Data for PN 10 (pressure rating 10 bar)
HDPE_PIPES = {
    "N16": {"nominal": 16, "internal_diameter": 13.0},
    "N20": {"nominal": 20, "internal_diameter": 16.2},
    "N25": {"nominal": 25, "internal_diameter": 20.4},
    "N32": {"nominal": 32, "internal_diameter": 26.0},
    "N40": {"nominal": 40, "internal_diameter": 32.6},
    "N50": {"nominal": 50, "internal_diameter": 40.8},
    "N63": {"nominal": 63, "internal_diameter": 51.4},
    "N75": {"nominal": 75, "internal_diameter": 61.2},
    "N90": {"nominal": 90, "internal_diameter": 73.6},
    "N110": {"nominal": 110, "internal_diameter": 89.8},
    "N125": {"nominal": 125, "internal_diameter": 102.0},
    "N140": {"nominal": 140, "internal_diameter": 114.4},
    "N160": {"nominal": 160, "internal_diameter": 130.8},
}


def get_pipe_internal_diameter(nominal_designation):
    """
    Get internal diameter in meters for a given nominal designation

    Args:
        nominal_designation: String like "N20", "N25", etc.

    Returns:
        Internal diameter in meters
    """
    if nominal_designation not in HDPE_PIPES:
        raise ValueError(f"Unknown pipe designation: {nominal_designation}")

    return HDPE_PIPES[nominal_designation]["internal_diameter"] / 1000.0  # Convert mm to m


def list_available_pipes():
    """List all available pipe designations"""
    return sorted(HDPE_PIPES.keys(), key=lambda x: HDPE_PIPES[x]["nominal"])


def display_pipe_table():
    """Display a table of available pipes"""
    print("\n=== HDPE PIPE SPECIFICATIONS (PN 10) ===")
    print(f"{'Designation':<15} {'Nominal D (mm)':<20} {'Internal D (mm)':<20}")
    print("-" * 55)
    for designation in list_available_pipes():
        pipe = HDPE_PIPES[designation]
        print(f"{designation:<15} {pipe['nominal']:<20} {pipe['internal_diameter']:<20}")
    print()
