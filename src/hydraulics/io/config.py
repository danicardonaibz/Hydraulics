"""Configuration management for units and system settings"""

from hydraulics.utils.conversions import (
    convert_flow_to_m3s,
    convert_length_to_m,
    convert_pressure_from_m
)


class Config:
    """Global configuration for the hydraulic calculation tool"""

    def __init__(self):
        # Default units
        self.pressure_unit = "bar"  # Options: bar, mwc (meters water column), atm
        self.flow_unit = "l/h"      # Options: m3/s, l/s, l/h
        self.length_unit = "m"      # Options: m, mm

    def set_pressure_unit(self, unit):
        """Set pressure unit"""
        valid_units = ["bar", "mwc", "atm"]
        if unit not in valid_units:
            raise ValueError(f"Invalid pressure unit. Choose from: {valid_units}")
        self.pressure_unit = unit

    def set_flow_unit(self, unit):
        """Set flow unit"""
        valid_units = ["m3/s", "l/s", "l/h"]
        if unit not in valid_units:
            raise ValueError(f"Invalid flow unit. Choose from: {valid_units}")
        self.flow_unit = unit

    def set_length_unit(self, unit):
        """Set length unit"""
        valid_units = ["m", "mm"]
        if unit not in valid_units:
            raise ValueError(f"Invalid length unit. Choose from: {valid_units}")
        self.length_unit = unit

    def convert_flow_to_m3s(self, flow):
        """Convert flow from configured unit to m³/s"""
        return convert_flow_to_m3s(flow, self.flow_unit)

    def convert_length_to_m(self, length):
        """Convert length from configured unit to meters"""
        return convert_length_to_m(length, self.length_unit)

    def convert_pressure_from_m(self, pressure_m):
        """Convert pressure from meters of water column to configured unit"""
        return convert_pressure_from_m(pressure_m, self.pressure_unit)


# Global configuration instance
config = Config()
