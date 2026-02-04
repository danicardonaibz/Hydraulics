"""Zone classes for dripping artery systems"""


class Zone:
    """Base class for pipe zones"""

    def __init__(self, length, zone_type):
        self.length = length  # in configured units
        self.zone_type = zone_type  # "transport" or "irrigation"


class TransportZone(Zone):
    """Transport zone - no drippers"""

    def __init__(self, length):
        super().__init__(length, "transport")
        self.flow = None  # Will be set during calculation


class IrrigationZone(Zone):
    """Irrigation zone - with pressure-compensated drippers"""

    def __init__(self, length, num_drippers, target_flow):
        super().__init__(length, "irrigation")
        self.num_drippers = num_drippers
        self.target_flow = target_flow  # Total flow for this zone in configured units
        self.flow = None  # Will be set during calculation
