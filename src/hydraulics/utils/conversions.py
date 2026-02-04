"""Unit conversion utilities"""


def convert_flow_to_m3s(flow, from_unit):
    """
    Convert flow from specified unit to m³/s

    Args:
        flow: Flow rate value
        from_unit: Source unit ('m3/s', 'l/s', 'l/h')

    Returns:
        Flow rate in m³/s
    """
    if from_unit == "m3/s":
        return flow
    elif from_unit == "l/s":
        return flow / 1000.0
    elif from_unit == "l/h":
        return flow / 3600000.0
    else:
        raise ValueError(f"Unknown flow unit: {from_unit}")


def convert_length_to_m(length, from_unit):
    """
    Convert length from specified unit to meters

    Args:
        length: Length value
        from_unit: Source unit ('m', 'mm')

    Returns:
        Length in meters
    """
    if from_unit == "m":
        return length
    elif from_unit == "mm":
        return length / 1000.0
    else:
        raise ValueError(f"Unknown length unit: {from_unit}")


def convert_pressure_from_m(pressure_m, to_unit):
    """
    Convert pressure from meters of water column to specified unit

    Args:
        pressure_m: Pressure in meters of water column
        to_unit: Target unit ('mwc', 'bar', 'atm')

    Returns:
        Pressure in target unit
    """
    if to_unit == "mwc":
        return pressure_m
    elif to_unit == "bar":
        return pressure_m * 0.0980665  # 1 mwc = 0.0980665 bar
    elif to_unit == "atm":
        return pressure_m * 0.0967841  # 1 mwc = 0.0967841 atm
    else:
        raise ValueError(f"Unknown pressure unit: {to_unit}")
