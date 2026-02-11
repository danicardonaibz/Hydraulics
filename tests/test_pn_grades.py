"""Tests for PN grade support in HDPE pipes"""

import pytest
from hydraulics.core.pipes import (
    get_pipe_internal_diameter,
    list_available_pn_grades,
    get_default_pn_grade,
    HDPE_PIPES
)
from hydraulics.models.artery import DrippingArtery
from hydraulics.models.zones import TransportZone, IrrigationZone


class TestPNGradeDatabase:
    """Test PN grade database integrity"""

    def test_all_pipes_have_pn10(self):
        """All DN sizes must have PN10 (default grade)"""
        for dn in HDPE_PIPES.keys():
            assert "PN10" in HDPE_PIPES[dn]["pn_grades"], \
                f"{dn} missing PN10 grade"

    def test_all_pipes_have_pn16(self):
        """All DN sizes must have PN16 (high pressure grade)"""
        for dn in HDPE_PIPES.keys():
            assert "PN16" in HDPE_PIPES[dn]["pn_grades"], \
                f"{dn} missing PN16 grade"

    def test_most_pipes_have_pn6(self):
        """Most DN sizes should have PN6 (low pressure grade)"""
        # DN16 doesn't have PN6, but others should
        for dn in HDPE_PIPES.keys():
            if dn != "N16":
                assert "PN6" in HDPE_PIPES[dn]["pn_grades"], \
                    f"{dn} missing PN6 grade"

    def test_internal_diameter_consistency(self):
        """Internal diameter should decrease with higher PN (thicker walls)"""
        for dn, data in HDPE_PIPES.items():
            pn_grades = data["pn_grades"]

            # If has both PN6 and PN10
            if "PN6" in pn_grades and "PN10" in pn_grades:
                assert pn_grades["PN6"]["internal_diameter"] > pn_grades["PN10"]["internal_diameter"], \
                    f"{dn}: PN6 should have larger ID than PN10"

            # If has both PN10 and PN16
            if "PN10" in pn_grades and "PN16" in pn_grades:
                assert pn_grades["PN10"]["internal_diameter"] > pn_grades["PN16"]["internal_diameter"], \
                    f"{dn}: PN10 should have larger ID than PN16"

            # If has all three
            if "PN6" in pn_grades and "PN10" in pn_grades and "PN16" in pn_grades:
                assert pn_grades["PN6"]["internal_diameter"] > pn_grades["PN10"]["internal_diameter"] > pn_grades["PN16"]["internal_diameter"], \
                    f"{dn}: ID should decrease PN6 > PN10 > PN16"

    def test_nominal_diameter_values(self):
        """Nominal diameters should be positive integers"""
        for dn, data in HDPE_PIPES.items():
            assert data["nominal"] > 0, f"{dn} has invalid nominal diameter"
            assert isinstance(data["nominal"], int), f"{dn} nominal should be integer"

    def test_internal_diameter_values(self):
        """Internal diameters should be positive and reasonable"""
        for dn, data in HDPE_PIPES.items():
            for pn_grade, pn_data in data["pn_grades"].items():
                internal_d = pn_data["internal_diameter"]
                assert internal_d > 0, f"{dn}-{pn_grade} has non-positive ID"
                # Internal diameter should be reasonable (less than 200mm for our range)
                assert internal_d < 200, f"{dn}-{pn_grade} ID suspiciously large"


class TestPNGradeFunctions:
    """Test PN grade utility functions"""

    def test_get_default_pn_grade(self):
        """Default PN grade should be PN10"""
        assert get_default_pn_grade() == "PN10"

    def test_list_available_pn_grades(self):
        """Should list available PN grades for a pipe"""
        # N20 has all three grades
        grades = list_available_pn_grades("N20")
        assert "PN6" in grades
        assert "PN10" in grades
        assert "PN16" in grades

        # N16 doesn't have PN6
        grades_n16 = list_available_pn_grades("N16")
        assert "PN6" not in grades_n16
        assert "PN10" in grades_n16
        assert "PN16" in grades_n16

    def test_list_available_pn_grades_invalid_dn(self):
        """Should raise ValueError for invalid DN"""
        with pytest.raises(ValueError, match="Unknown pipe designation"):
            list_available_pn_grades("N999")

    def test_get_pipe_internal_diameter_with_pn_grade(self):
        """Should return correct diameter for DN + PN grade"""
        # N40-PN10 should have 40.8mm ID
        diameter = get_pipe_internal_diameter("N40", "PN10")
        assert abs(diameter - 0.0408) < 1e-6  # 40.8mm in meters

        # N40-PN16 should have 36.2mm ID (smaller due to thicker walls)
        diameter_pn16 = get_pipe_internal_diameter("N40", "PN16")
        assert abs(diameter_pn16 - 0.0362) < 1e-6  # 36.2mm in meters

        # PN16 should be smaller than PN10
        assert diameter_pn16 < diameter

    def test_get_pipe_internal_diameter_default_pn10(self):
        """Should default to PN10 if no PN grade specified"""
        diameter_default = get_pipe_internal_diameter("N40")
        diameter_pn10 = get_pipe_internal_diameter("N40", "PN10")
        assert diameter_default == diameter_pn10

    def test_get_pipe_internal_diameter_invalid_pn(self):
        """Should raise ValueError for invalid PN grade"""
        with pytest.raises(ValueError, match="PN grade PN99 not available"):
            get_pipe_internal_diameter("N40", "PN99")

    def test_get_pipe_internal_diameter_unavailable_pn(self):
        """Should raise ValueError for unavailable PN grade"""
        with pytest.raises(ValueError, match="PN grade PN6 not available for N16"):
            get_pipe_internal_diameter("N16", "PN6")


class TestDrippingArteryPNGrade:
    """Test DrippingArtery with PN grade support"""

    def test_dripping_artery_default_pn10(self):
        """DrippingArtery should default to PN10"""
        artery = DrippingArtery(1500, "N40")
        assert artery.pn_grade == "PN10"

    def test_dripping_artery_with_pn_grade(self):
        """DrippingArtery should accept PN grade parameter"""
        artery = DrippingArtery(1500, "N40", pn_grade="PN16")
        assert artery.pn_grade == "PN16"

    def test_calculation_uses_correct_diameter(self):
        """Calculation should use diameter corresponding to PN grade"""
        # Create two arteries with same DN but different PN grades
        artery_pn10 = DrippingArtery(1500, "N40", pn_grade="PN10")
        artery_pn16 = DrippingArtery(1500, "N40", pn_grade="PN16")

        # Add same zones to both
        artery_pn10.add_zone(TransportZone(50))
        artery_pn10.add_zone(IrrigationZone(100, 50, 1500))

        artery_pn16.add_zone(TransportZone(50))
        artery_pn16.add_zone(IrrigationZone(100, 50, 1500))

        # Calculate
        results_pn10 = artery_pn10.calculate()
        results_pn16 = artery_pn16.calculate()

        # PN16 has smaller diameter, so higher head loss
        assert results_pn16['total_head_loss'] > results_pn10['total_head_loss'], \
            "PN16 (smaller ID) should have higher head loss than PN10"

        # Check diameters
        diameter_pn10 = get_pipe_internal_diameter("N40", "PN10")
        diameter_pn16 = get_pipe_internal_diameter("N40", "PN16")
        assert results_pn10['diameter'] == diameter_pn10
        assert results_pn16['diameter'] == diameter_pn16

    def test_dn_comparison_preserves_pn_grade(self):
        """DN comparison should use same PN grade across all DN sizes"""
        artery = DrippingArtery(1500, "N40", pn_grade="PN16")
        artery.add_zone(TransportZone(50))
        artery.add_zone(IrrigationZone(100, 50, 1500))

        comparison_results = artery.calculate_with_dn_comparison()
        dn_comparison = comparison_results['dn_comparison']

        # All results should have PN16
        for dn_result in dn_comparison:
            assert dn_result['pn_grade'] == "PN16", \
                f"{dn_result['pipe_designation']} should use PN16"

        # Verify diameters match PN16 specification
        for dn_result in dn_comparison:
            dn = dn_result['pipe_designation']
            expected_diameter = get_pipe_internal_diameter(dn, "PN16") * 1000  # mm
            actual_diameter = dn_result['internal_diameter_mm']
            assert abs(expected_diameter - actual_diameter) < 0.1, \
                f"{dn} diameter mismatch for PN16"


class TestBackwardCompatibility:
    """Test backward compatibility with old code"""

    def test_old_style_api_defaults_to_pn10(self):
        """Old API calls without PN grade should default to PN10"""
        # Old-style artery creation (no PN grade)
        artery = DrippingArtery(1500, "N40")
        artery.add_zone(TransportZone(50))
        artery.add_zone(IrrigationZone(100, 50, 1500))

        results = artery.calculate()

        # Should use PN10 diameter (40.8mm)
        expected_diameter = get_pipe_internal_diameter("N40", "PN10")
        assert results['diameter'] == expected_diameter

    def test_old_get_diameter_call(self):
        """Old get_pipe_internal_diameter calls should work"""
        # Old-style call (no PN grade parameter)
        diameter = get_pipe_internal_diameter("N40")

        # Should return PN10 diameter
        expected = 0.0408  # 40.8mm in meters
        assert abs(diameter - expected) < 1e-6


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_invalid_dn(self):
        """Invalid DN should raise ValueError"""
        with pytest.raises(ValueError):
            get_pipe_internal_diameter("N999", "PN10")

    def test_none_pn_grade_defaults(self):
        """None PN grade should default to PN10"""
        diameter_none = get_pipe_internal_diameter("N40", None)
        diameter_pn10 = get_pipe_internal_diameter("N40", "PN10")
        assert diameter_none == diameter_pn10

    def test_empty_string_pn_grade_raises(self):
        """Empty PN grade should raise ValueError"""
        with pytest.raises(ValueError):
            get_pipe_internal_diameter("N40", "")

    def test_case_sensitivity(self):
        """PN grade should be case-sensitive"""
        # Uppercase should work
        diameter_upper = get_pipe_internal_diameter("N40", "PN10")
        assert diameter_upper is not None

        # Lowercase should fail
        with pytest.raises(ValueError):
            get_pipe_internal_diameter("N40", "pn10")
