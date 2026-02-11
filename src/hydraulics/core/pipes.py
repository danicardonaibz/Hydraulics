"""HDPE pipe specifications - European nominal diameters"""

# HDPE Pipe specifications with PN grade variants (ISO 4427 standard)
# Data for PN6 (6 bar), PN10 (10 bar), PN16 (16 bar) pressure ratings
# Each DN has different internal diameters based on wall thickness
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
    "N25": {
        "nominal": 25,
        "pn_grades": {
            "PN6": {"internal_diameter": 28.0},
            "PN10": {"internal_diameter": 26.2},
            "PN16": {"internal_diameter": 23.2}
        }
    },
    "N32": {
        "nominal": 32,
        "pn_grades": {
            "PN6": {"internal_diameter": 35.4},
            "PN10": {"internal_diameter": 32.6},
            "PN16": {"internal_diameter": 29.0}
        }
    },
    "N40": {
        "nominal": 40,
        "pn_grades": {
            "PN6": {"internal_diameter": 44.2},
            "PN10": {"internal_diameter": 40.8},
            "PN16": {"internal_diameter": 36.2}
        }
    },
    "N50": {
        "nominal": 50,
        "pn_grades": {
            "PN6": {"internal_diameter": 58.2},
            "PN10": {"internal_diameter": 55.8},
            "PN16": {"internal_diameter": 51.4}
        }
    },
    "N63": {
        "nominal": 63,
        "pn_grades": {
            "PN6": {"internal_diameter": 69.2},
            "PN10": {"internal_diameter": 66.4},
            "PN16": {"internal_diameter": 61.4}
        }
    },
    "N75": {
        "nominal": 75,
        "pn_grades": {
            "PN6": {"internal_diameter": 83.0},
            "PN10": {"internal_diameter": 79.8},
            "PN16": {"internal_diameter": 73.6}
        }
    },
    "N90": {
        "nominal": 90,
        "pn_grades": {
            "PN6": {"internal_diameter": 101.6},
            "PN10": {"internal_diameter": 97.4},
            "PN16": {"internal_diameter": 90.0}
        }
    },
    "N110": {
        "nominal": 110,
        "pn_grades": {
            "PN6": {"internal_diameter": 115.4},
            "PN10": {"internal_diameter": 110.8},
            "PN16": {"internal_diameter": 102.2}
        }
    },
    "N125": {
        "nominal": 125,
        "pn_grades": {
            "PN6": {"internal_diameter": 129.2},
            "PN10": {"internal_diameter": 124.0},
            "PN16": {"internal_diameter": 114.6}
        }
    },
    "N140": {
        "nominal": 140,
        "pn_grades": {
            "PN6": {"internal_diameter": 147.6},
            "PN10": {"internal_diameter": 141.8},
            "PN16": {"internal_diameter": 130.8}
        }
    },
    "N160": {
        "nominal": 160,
        "pn_grades": {
            "PN6": {"internal_diameter": 166.2},
            "PN10": {"internal_diameter": 159.6},
            "PN16": {"internal_diameter": 147.2}
        }
    }
}


def get_default_pn_grade():
    """
    Get the default PN grade for backward compatibility

    Returns:
        String: Default PN grade ("PN10")
    """
    return "PN10"


def list_available_pn_grades(nominal_designation):
    """
    List available PN grades for a given pipe designation

    Args:
        nominal_designation: String like "N20", "N25", etc.

    Returns:
        List of available PN grade strings (e.g., ["PN6", "PN10", "PN16"])
    """
    if nominal_designation not in HDPE_PIPES:
        raise ValueError(f"Unknown pipe designation: {nominal_designation}")

    return sorted(HDPE_PIPES[nominal_designation]["pn_grades"].keys())


def get_pipe_internal_diameter(nominal_designation, pn_grade=None):
    """
    Get internal diameter in meters for a given nominal designation and PN grade

    Args:
        nominal_designation: String like "N20", "N25", etc.
        pn_grade: PN grade string like "PN6", "PN10", "PN16" (default: PN10)

    Returns:
        Internal diameter in meters

    Raises:
        ValueError: If pipe designation or PN grade is invalid
    """
    if nominal_designation not in HDPE_PIPES:
        raise ValueError(f"Unknown pipe designation: {nominal_designation}")

    # Use default PN grade if not specified (backward compatibility)
    if pn_grade is None:
        pn_grade = get_default_pn_grade()

    pipe_data = HDPE_PIPES[nominal_designation]

    if pn_grade not in pipe_data["pn_grades"]:
        available = list_available_pn_grades(nominal_designation)
        raise ValueError(
            f"PN grade {pn_grade} not available for {nominal_designation}. "
            f"Available grades: {', '.join(available)}"
        )

    return pipe_data["pn_grades"][pn_grade]["internal_diameter"] / 1000.0  # Convert mm to m


def list_available_pipes():
    """List all available pipe designations"""
    return sorted(HDPE_PIPES.keys(), key=lambda x: HDPE_PIPES[x]["nominal"])


def get_adjacent_pipe_sizes(nominal_designation, num_smaller=2, num_larger=1):
    """
    Get adjacent pipe sizes for comparison purposes

    Args:
        nominal_designation: String like "N20", "N25", etc.
        num_smaller: Number of smaller pipe sizes to return
        num_larger: Number of larger pipe sizes to return

    Returns:
        Dictionary with keys 'smaller', 'selected', 'larger' containing pipe designations
        Returns None for missing sizes if at boundaries
    """
    if nominal_designation not in HDPE_PIPES:
        raise ValueError(f"Unknown pipe designation: {nominal_designation}")

    # Get sorted list of all pipe designations
    sorted_pipes = list_available_pipes()
    current_idx = sorted_pipes.index(nominal_designation)

    # Get smaller pipes (up to num_smaller)
    smaller = []
    for i in range(1, num_smaller + 1):
        idx = current_idx - i
        if idx >= 0:
            smaller.insert(0, sorted_pipes[idx])  # Insert at beginning to maintain order

    # Get larger pipes (up to num_larger)
    larger = []
    for i in range(1, num_larger + 1):
        idx = current_idx + i
        if idx < len(sorted_pipes):
            larger.append(sorted_pipes[idx])

    return {
        'smaller': smaller,
        'selected': nominal_designation,
        'larger': larger
    }


def display_pipe_table(pn_grade=None):
    """
    Display a table of available pipes

    Args:
        pn_grade: Optional PN grade to display. If None, shows all PN grades.
    """
    if pn_grade:
        # Display single PN grade
        print(f"\n=== HDPE PIPE SPECIFICATIONS ({pn_grade}) ===")
        print(f"{'Designation':<15} {'Nominal D (mm)':<20} {'Internal D (mm)':<20}")
        print("-" * 55)
        for designation in list_available_pipes():
            pipe = HDPE_PIPES[designation]
            if pn_grade in pipe["pn_grades"]:
                internal_d = pipe["pn_grades"][pn_grade]["internal_diameter"]
                print(f"{designation:<15} {pipe['nominal']:<20} {internal_d:<20}")
            else:
                print(f"{designation:<15} {pipe['nominal']:<20} {'N/A':<20}")
        print()
    else:
        # Display all PN grades
        print("\n=== HDPE PIPE SPECIFICATIONS (ALL PN GRADES) ===")
        print(f"{'Designation':<12} {'Nominal':<10} {'PN6 ID':<12} {'PN10 ID':<12} {'PN16 ID':<12}")
        print(f"{'':12} {'(mm)':<10} {'(mm)':<12} {'(mm)':<12} {'(mm)':<12}")
        print("-" * 60)
        for designation in list_available_pipes():
            pipe = HDPE_PIPES[designation]
            pn6 = pipe["pn_grades"].get("PN6", {}).get("internal_diameter", "N/A")
            pn10 = pipe["pn_grades"].get("PN10", {}).get("internal_diameter", "N/A")
            pn16 = pipe["pn_grades"].get("PN16", {}).get("internal_diameter", "N/A")

            pn6_str = f"{pn6:.1f}" if isinstance(pn6, (int, float)) else pn6
            pn10_str = f"{pn10:.1f}" if isinstance(pn10, (int, float)) else pn10
            pn16_str = f"{pn16:.1f}" if isinstance(pn16, (int, float)) else pn16

            print(f"{designation:<12} {pipe['nominal']:<10} {pn6_str:<12} {pn10_str:<12} {pn16_str:<12}")
        print()
