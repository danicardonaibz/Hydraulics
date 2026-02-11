"""Dripping artery calculation model"""

from hydraulics.models.zones import IrrigationZone, TransportZone
from hydraulics.calculators.segment import calculate_section_loss, calculate_christiansen_head_loss
from hydraulics.core.pipes import get_pipe_internal_diameter, get_adjacent_pipe_sizes
from hydraulics.core.properties import WaterProperties
from hydraulics.io.config import config


class DrippingArtery:
    """Main class for dripping artery calculation"""

    def __init__(self, total_flow, pipe_designation):
        self.total_flow = total_flow  # in configured units
        self.pipe_designation = pipe_designation
        self.zones = []
        self.results = []

    def add_zone(self, zone):
        """Add a zone to the artery"""
        self.zones.append(zone)

    def validate_flow_conservation(self):
        """Validate that sum of irrigation flows equals total flow"""
        total_irrigation_flow = sum(
            zone.target_flow for zone in self.zones
            if isinstance(zone, IrrigationZone)
        )

        tolerance = 0.01  # 1% tolerance
        if abs(total_irrigation_flow - self.total_flow) > tolerance * self.total_flow:
            raise ValueError(
                f"Flow conservation error: Sum of irrigation flows ({total_irrigation_flow} {config.flow_unit}) "
                f"does not match total flow ({self.total_flow} {config.flow_unit})"
            )

    def _calculate_for_diameter(self, diameter):
        """
        Internal method to calculate head losses for a specific diameter

        Args:
            diameter: Pipe internal diameter in meters

        Returns:
            Dictionary with calculation results
        """
        roughness = WaterProperties.hdpe_roughness

        # Initialize
        zone_results = []
        cumulative_head_loss = 0.0
        cumulative_length = 0.0
        current_flow = config.convert_flow_to_m3s(self.total_flow)

        # Calculate for each zone
        for i, zone in enumerate(self.zones):
            zone_length_m = config.convert_length_to_m(zone.length)

            if isinstance(zone, TransportZone):
                # Transport zone - constant flow
                result = calculate_section_loss(current_flow, diameter, zone_length_m, roughness)
                result['zone_type'] = 'transport'
                result['zone_number'] = i + 1
                result['length'] = zone_length_m
                result['flow_m3s'] = current_flow
                result['cumulative_length'] = cumulative_length + zone_length_m
                result['cumulative_head_loss'] = cumulative_head_loss + result['head_loss']

                cumulative_head_loss = result['cumulative_head_loss']
                cumulative_length = result['cumulative_length']

            elif isinstance(zone, IrrigationZone):
                # Irrigation zone - flow decreases along the zone
                # We'll calculate losses segment by segment between drippers
                zone_flow_total = config.convert_flow_to_m3s(zone.target_flow)
                segment_length = zone_length_m / zone.num_drippers
                flow_per_dripper = zone_flow_total / zone.num_drippers

                zone_head_loss = 0.0
                segment_results = []

                for j in range(zone.num_drippers):
                    # Flow at the start of this segment
                    segment_flow = current_flow - j * flow_per_dripper

                    # Calculate loss for this segment
                    seg_result = calculate_section_loss(segment_flow, diameter, segment_length, roughness)
                    zone_head_loss += seg_result['head_loss']

                    segment_results.append({
                        'segment': j + 1,
                        'flow_m3s': segment_flow,
                        'velocity': seg_result['velocity'],
                        'reynolds': seg_result['reynolds'],
                        'flow_regime': seg_result['flow_regime'],
                        'friction_factor': seg_result['friction_factor'],
                        'friction_method': seg_result['friction_method'],
                        'head_loss': seg_result['head_loss'],
                        'is_valid': seg_result['is_valid']
                    })

                # Store aggregated result for this zone
                result = {
                    'zone_type': 'irrigation',
                    'zone_number': i + 1,
                    'length': zone_length_m,
                    'num_drippers': zone.num_drippers,
                    'flow_start_m3s': current_flow,
                    'flow_end_m3s': current_flow - zone_flow_total,
                    'head_loss': zone_head_loss,
                    'cumulative_length': cumulative_length + zone_length_m,
                    'cumulative_head_loss': cumulative_head_loss + zone_head_loss,
                    'segments': segment_results,
                    'is_valid': all(seg_result['is_valid'] for seg_result in segment_results)
                }

                # Update current flow (flow decreases after irrigation zone)
                current_flow -= zone_flow_total
                cumulative_head_loss = result['cumulative_head_loss']
                cumulative_length = result['cumulative_length']

            zone_results.append(result)

        # Calculate simplified model (all flow exits at the end)
        total_length = cumulative_length
        initial_flow = config.convert_flow_to_m3s(self.total_flow)
        simplified_result = calculate_section_loss(initial_flow, diameter, total_length, roughness)

        # Calculate total number of outlets (drippers)
        total_outlets = sum(
            zone.num_drippers for zone in self.zones
            if isinstance(zone, IrrigationZone)
        )

        # Calculate Christiansen approximation
        christiansen_result = None
        if total_outlets > 0:
            christiansen_result = calculate_christiansen_head_loss(
                initial_flow, diameter, total_length, roughness, total_outlets, m=2.0
            )

        return {
            'diameter': diameter,
            'roughness': roughness,
            'total_length': total_length,
            'total_head_loss': cumulative_head_loss,
            'simplified_head_loss': simplified_result['head_loss'],
            'christiansen': christiansen_result,
            'zones': zone_results
        }

    def calculate(self):
        """Calculate head losses for the entire artery using the selected pipe designation"""
        # Validate flow conservation
        self.validate_flow_conservation()

        # Get pipe properties
        diameter = get_pipe_internal_diameter(self.pipe_designation)

        # Perform calculation
        results = self._calculate_for_diameter(diameter)

        # Store results for backward compatibility
        self.results = results['zones']

        return results

    def calculate_with_dn_comparison(self):
        """
        Calculate head losses for multiple DN sizes for comparison

        Returns:
            Dictionary with:
            - 'selected': Results for the user-selected DN
            - 'dn_comparison': List of results for adjacent DN sizes
        """
        # Validate flow conservation
        self.validate_flow_conservation()

        # Get adjacent pipe sizes (2 smaller, 1 larger)
        adjacent_sizes = get_adjacent_pipe_sizes(self.pipe_designation, num_smaller=2, num_larger=1)

        # Collect all DN sizes to calculate
        all_dns = adjacent_sizes['smaller'] + [adjacent_sizes['selected']] + adjacent_sizes['larger']

        # Calculate for each DN size
        dn_results = []
        for dn in all_dns:
            diameter = get_pipe_internal_diameter(dn)
            result = self._calculate_for_diameter(diameter)

            dn_results.append({
                'pipe_designation': dn,
                'is_selected': (dn == self.pipe_designation),
                'internal_diameter_mm': diameter * 1000,
                'full_calculation': result['total_head_loss'],
                'christiansen': result['christiansen']['head_loss'] if result['christiansen'] else None,
                'simplified': result['simplified_head_loss'],
                'full_result': result  # Complete result for detailed reporting
            })

        # Get the selected DN result for backward compatibility
        selected_result = next(r['full_result'] for r in dn_results if r['is_selected'])
        self.results = selected_result['zones']

        return {
            'selected': selected_result,
            'dn_comparison': dn_results
        }
