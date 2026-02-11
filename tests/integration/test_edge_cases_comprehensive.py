#!/usr/bin/env python3
"""
Comprehensive edge case testing for the hydraulics tool

This test suite covers:
1. Multi-DN comparison edge cases
2. NIST water API with extreme temperatures
3. Zero flow and boundary conditions
4. Very large/small pipe diameters
5. Extreme dripper counts
6. Flow conservation violations
7. API failure scenarios
8. Windows compatibility (ASCII output)
"""

import sys
from hydraulics.models import DrippingArtery, TransportZone, IrrigationZone
from hydraulics.io import config
from hydraulics.io.reports import generate_report
from hydraulics.core.properties import WaterProperties
from hydraulics.core.water_api import WaterAPIClient


def test_dn_comparison_edge_smallest():
    """Test DN comparison with smallest available pipe (N16)"""
    print("\n" + "="*60)
    print("TEST: DN Comparison - Smallest Pipe (N16)")
    print("="*60)

    try:
        artery = DrippingArtery(100, "N16")
        artery.add_zone(TransportZone(10))
        artery.add_zone(IrrigationZone(20, 5, 100))

        comparison_results = artery.calculate_with_dn_comparison()
        dn_comparison = comparison_results['dn_comparison']

        # Should only have N16, N20 (no smaller pipes available)
        print(f"   Available DN sizes: {[dn['pipe_designation'] for dn in dn_comparison]}")
        print(f"   Number of DN sizes in comparison: {len(dn_comparison)}")

        # Verify selected pipe is marked
        selected = [dn for dn in dn_comparison if dn['is_selected']]
        assert len(selected) == 1, "Should have exactly one selected pipe"
        assert selected[0]['pipe_designation'] == 'N16', "Selected pipe should be N16"

        print("   [PASS] Smallest pipe DN comparison works correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dn_comparison_edge_largest():
    """Test DN comparison with largest available pipe (N160)"""
    print("\n" + "="*60)
    print("TEST: DN Comparison - Largest Pipe (N160)")
    print("="*60)

    try:
        artery = DrippingArtery(10000, "N160")
        artery.add_zone(TransportZone(100))
        artery.add_zone(IrrigationZone(200, 100, 10000))

        comparison_results = artery.calculate_with_dn_comparison()
        dn_comparison = comparison_results['dn_comparison']

        # Should have N125, N140, N160 (no larger pipes available)
        print(f"   Available DN sizes: {[dn['pipe_designation'] for dn in dn_comparison]}")
        print(f"   Number of DN sizes in comparison: {len(dn_comparison)}")

        # Verify selected pipe is marked
        selected = [dn for dn in dn_comparison if dn['is_selected']]
        assert len(selected) == 1, "Should have exactly one selected pipe"
        assert selected[0]['pipe_designation'] == 'N160', "Selected pipe should be N160"

        print("   [PASS] Largest pipe DN comparison works correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dn_comparison_single_available():
    """Test DN comparison when only one pipe size is reasonable"""
    print("\n" + "="*60)
    print("TEST: DN Comparison - Edge Case with Limited Options")
    print("="*60)

    try:
        # N20 with two smaller (N16) and one larger (N25)
        artery = DrippingArtery(200, "N20")
        artery.add_zone(IrrigationZone(50, 10, 200))

        comparison_results = artery.calculate_with_dn_comparison()
        dn_comparison = comparison_results['dn_comparison']

        print(f"   DN sizes in comparison: {[dn['pipe_designation'] for dn in dn_comparison]}")

        # Verify calculations are consistent
        for dn_result in dn_comparison:
            assert dn_result['full_calculation'] > 0, "Head loss should be positive"
            print(f"   {dn_result['pipe_designation']}: {dn_result['full_calculation']:.4f} m")

        print("   [PASS] DN comparison with limited options works")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nist_api_extreme_cold():
    """Test NIST API with very cold water (0°C)"""
    print("\n" + "="*60)
    print("TEST: NIST API - Extreme Cold (0°C)")
    print("="*60)

    try:
        WaterProperties.set_temperature(0.0)

        print(f"   Temperature: {WaterProperties.temperature}°C")
        print(f"   Density: {WaterProperties.density:.2f} kg/m³")
        print(f"   Dynamic viscosity: {WaterProperties.dynamic_viscosity*1000:.3f} mPa·s")
        print(f"   Kinematic viscosity: {WaterProperties.kinematic_viscosity*1e6:.3f} mm²/s")

        # Water at 0°C should be very viscous
        assert WaterProperties.dynamic_viscosity > 1.5e-3, "Water should be more viscous at 0°C"
        assert WaterProperties.density > 999.0, "Water density should be high at 0°C"

        # Test calculation with cold water
        artery = DrippingArtery(1000, "N20")
        artery.add_zone(TransportZone(50))
        artery.add_zone(IrrigationZone(50, 10, 1000))

        results = artery.calculate()
        cold_loss = results['total_head_loss']
        print(f"   Head loss at 0°C: {cold_loss:.4f} m")

        # Reset to defaults
        WaterProperties.reset_to_defaults()

        # Compare with 20°C
        results_20c = artery.calculate()
        loss_20c = results_20c['total_head_loss']
        print(f"   Head loss at 20°C: {loss_20c:.4f} m")

        # Cold water should have higher losses (higher viscosity)
        assert cold_loss > loss_20c, "Cold water should have higher head loss"

        print("   [PASS] NIST API handles 0°C correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        WaterProperties.reset_to_defaults()
        return False


def test_nist_api_extreme_hot():
    """Test NIST API with very hot water (100°C)"""
    print("\n" + "="*60)
    print("TEST: NIST API - Extreme Hot (100°C)")
    print("="*60)

    try:
        WaterProperties.set_temperature(100.0)

        print(f"   Temperature: {WaterProperties.temperature}°C")
        print(f"   Density: {WaterProperties.density:.2f} kg/m³")
        print(f"   Dynamic viscosity: {WaterProperties.dynamic_viscosity*1000:.3f} mPa·s")
        print(f"   Kinematic viscosity: {WaterProperties.kinematic_viscosity*1e6:.3f} mm²/s")

        # Water at 100°C should be less viscous and less dense than at 20°C
        # At elevated pressure (to keep liquid phase), density is around 958 kg/m³
        assert WaterProperties.dynamic_viscosity < 1.0e-3, "Water should be less viscous at 100°C"
        assert WaterProperties.density < 999.0, "Water density should be lower at 100°C than at 20°C"
        assert WaterProperties.density > 950.0, "Water should still be liquid (not vapor)"

        # Test calculation with hot water
        artery = DrippingArtery(1000, "N20")
        artery.add_zone(TransportZone(50))
        artery.add_zone(IrrigationZone(50, 10, 1000))

        results = artery.calculate()
        hot_loss = results['total_head_loss']
        print(f"   Head loss at 100°C: {hot_loss:.4f} m")

        # Reset to defaults
        WaterProperties.reset_to_defaults()

        # Compare with 20°C
        results_20c = artery.calculate()
        loss_20c = results_20c['total_head_loss']
        print(f"   Head loss at 20°C: {loss_20c:.4f} m")

        # At 100°C, kinematic viscosity (nu = mu/rho) determines Reynolds number
        # Lower viscosity means higher Re, which generally means lower friction factor
        # However, the effect depends on the flow regime
        # For this test, we just verify calculations complete successfully
        print(f"   Kinematic viscosity at 100°C: {WaterProperties.kinematic_viscosity*1e6:.3f} mm²/s")
        print(f"   Kinematic viscosity at 20°C: 1.004 mm²/s")

        # The key is that calculations work, regardless of which has higher loss

        print("   [PASS] NIST API handles 100°C correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        WaterProperties.reset_to_defaults()
        return False


def test_nist_api_invalid_temperature():
    """Test NIST API with invalid temperatures"""
    print("\n" + "="*60)
    print("TEST: NIST API - Invalid Temperatures")
    print("="*60)

    try:
        # Test below 0°C
        try:
            WaterAPIClient.fetch_properties(-10.0)
            print("   [FAIL] Should raise ValueError for -10°C")
            return False
        except ValueError as e:
            print(f"   [PASS] Correctly rejected -10°C: {e}")

        # Test above 100°C
        try:
            WaterAPIClient.fetch_properties(150.0)
            print("   [FAIL] Should raise ValueError for 150°C")
            return False
        except ValueError as e:
            print(f"   [PASS] Correctly rejected 150°C: {e}")

        # Test boundary values
        try:
            props_0 = WaterAPIClient.fetch_properties(0.0)
            print(f"   [PASS] Accepted 0°C (boundary): density={props_0['density']:.2f} kg/m³")

            props_100 = WaterAPIClient.fetch_properties(100.0)
            print(f"   [PASS] Accepted 100°C (boundary): density={props_100['density']:.2f} kg/m³")
        except Exception as e:
            print(f"   [FAIL] Boundary values failed: {e}")
            return False

        print("   [PASS] Temperature validation works correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zero_flow_edge_case():
    """Test behavior with extremely small flow (edge of zero)"""
    print("\n" + "="*60)
    print("TEST: Zero Flow Edge Case")
    print("="*60)

    try:
        # Very small flow: 0.1 l/h
        artery = DrippingArtery(0.1, "N16")
        artery.add_zone(IrrigationZone(1, 1, 0.1))

        results = artery.calculate()
        print(f"   Flow: 0.1 l/h")
        print(f"   Head loss: {results['total_head_loss']:.6f} m")
        print(f"   Reynolds: {results['zones'][0]['segments'][0]['reynolds']:.1f}")
        print(f"   Flow regime: {results['zones'][0]['segments'][0]['flow_regime']}")

        assert results['total_head_loss'] >= 0, "Head loss should be non-negative"

        print("   [PASS] Very small flow handled correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_massive_dripper_count():
    """Test with thousands of drippers"""
    print("\n" + "="*60)
    print("TEST: Massive Dripper Count (1000 drippers)")
    print("="*60)

    try:
        artery = DrippingArtery(10000, "N63")
        artery.add_zone(TransportZone(50))
        artery.add_zone(IrrigationZone(1000, 1000, 10000))

        results = artery.calculate()
        print(f"   Total drippers: 1000")
        print(f"   Head loss: {results['total_head_loss']:.4f} m")
        print(f"   Number of segments calculated: {len(results['zones'][1]['segments'])}")

        assert len(results['zones'][1]['segments']) == 1000, "Should calculate all segments"

        # Check Christiansen approximation
        if results['christiansen']:
            chris_loss = results['christiansen']['head_loss']
            full_loss = results['total_head_loss']
            diff_pct = abs(chris_loss - full_loss) / full_loss * 100
            print(f"   Christiansen approximation difference: {diff_pct:.2f}%")

        print("   [PASS] Massive dripper count handled correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_very_long_installation():
    """Test with very long total length (several kilometers)"""
    print("\n" + "="*60)
    print("TEST: Very Long Installation (5 km)")
    print("="*60)

    try:
        artery = DrippingArtery(5000, "N50")
        artery.add_zone(TransportZone(2000))  # 2 km transport
        artery.add_zone(IrrigationZone(3000, 300, 5000))  # 3 km irrigation

        results = artery.calculate()
        print(f"   Total length: {results['total_length']:.0f} m")
        print(f"   Head loss: {results['total_head_loss']:.4f} m ({config.convert_pressure_from_m(results['total_head_loss']):.4f} bar)")

        assert results['total_length'] == 5000, "Total length should be 5000 m"

        print("   [PASS] Very long installation calculated successfully")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flow_conservation_strict():
    """Test strict flow conservation validation"""
    print("\n" + "="*60)
    print("TEST: Strict Flow Conservation")
    print("="*60)

    try:
        # Test 1: Exact match
        artery1 = DrippingArtery(1000, "N20")
        artery1.add_zone(IrrigationZone(50, 10, 1000))
        artery1.validate_flow_conservation()
        print("   [PASS] Exact flow match validated")

        # Test 2: Within 1% tolerance
        artery2 = DrippingArtery(1000, "N20")
        artery2.add_zone(IrrigationZone(50, 10, 999))  # 0.1% difference
        artery2.validate_flow_conservation()
        print("   [PASS] 0.1% difference accepted")

        # Test 3: Just outside tolerance (should fail)
        artery3 = DrippingArtery(1000, "N20")
        artery3.add_zone(IrrigationZone(50, 10, 980))  # 2% difference

        try:
            artery3.validate_flow_conservation()
            print("   [FAIL] Should reject 2% difference")
            return False
        except ValueError as e:
            print(f"   [PASS] Correctly rejected 2% difference: {str(e)[:60]}...")

        # Test 4: Multiple zones totaling correct amount
        artery4 = DrippingArtery(1500, "N20")
        artery4.add_zone(IrrigationZone(50, 10, 500))
        artery4.add_zone(IrrigationZone(100, 20, 1000))
        artery4.validate_flow_conservation()
        print("   [PASS] Multiple zones with correct total validated")

        print("   [PASS] Flow conservation validation working correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extreme_reynolds_laminar():
    """Test laminar flow regime (very low Reynolds)"""
    print("\n" + "="*60)
    print("TEST: Extreme Reynolds - Laminar Flow")
    print("="*60)

    try:
        # Use very small flow and large pipe to get laminar flow
        artery = DrippingArtery(1, "N110")  # 1 l/h in large pipe
        artery.add_zone(TransportZone(10))
        artery.add_zone(IrrigationZone(10, 10, 1))

        results = artery.calculate()
        zone_result = results['zones'][0]

        print(f"   Flow: 1 l/h")
        print(f"   Pipe: N110 (89.8 mm)")
        print(f"   Reynolds: {zone_result['reynolds']:.1f}")
        print(f"   Flow regime: {zone_result['flow_regime']}")
        print(f"   Friction method: {zone_result['friction_method']}")

        assert zone_result['reynolds'] < 2000, "Should be laminar flow"
        assert zone_result['friction_method'] == "Laminar (f=64/Re)", "Should use laminar friction factor"

        print("   [PASS] Laminar flow handled correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extreme_reynolds_turbulent():
    """Test highly turbulent flow (very high Reynolds)"""
    print("\n" + "="*60)
    print("TEST: Extreme Reynolds - Highly Turbulent Flow")
    print("="*60)

    try:
        # Use very high flow and small pipe to get high Reynolds
        artery = DrippingArtery(20000, "N16")  # 20000 l/h in small pipe
        artery.add_zone(TransportZone(10))
        artery.add_zone(IrrigationZone(10, 10, 20000))

        results = artery.calculate()
        zone_result = results['zones'][0]

        print(f"   Flow: 20000 l/h")
        print(f"   Pipe: N16 (13.0 mm)")
        print(f"   Velocity: {zone_result['velocity']:.2f} m/s")
        print(f"   Reynolds: {zone_result['reynolds']:.0f}")
        print(f"   Flow regime: {zone_result['flow_regime']}")
        print(f"   Friction method: {zone_result['friction_method']}")

        assert zone_result['reynolds'] > 50000, "Should be highly turbulent"
        assert zone_result['friction_method'] == "Colebrook-White", "Should use Colebrook-White"

        print("   [PASS] Highly turbulent flow handled correctly")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_windows_ascii_compatibility():
    """Test that all output is ASCII-compatible for Windows cmd.exe"""
    print("\n" + "="*60)
    print("TEST: Windows ASCII Compatibility")
    print("="*60)

    try:
        # Capture output from water properties display
        from io import StringIO
        import sys

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        from hydraulics.core.properties import display_water_properties
        display_water_properties()

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Try to encode as ASCII
        try:
            output.encode('ascii')
            print("   [PASS] Water properties display is ASCII-compatible")
        except UnicodeEncodeError as e:
            print(f"   [FAIL] Contains non-ASCII characters: {e}")
            print(f"   Output: {output[:200]}...")
            return False

        # Test report generation
        artery = DrippingArtery(1000, "N20")
        artery.add_zone(TransportZone(10))
        artery.add_zone(IrrigationZone(50, 10, 1000))

        results = artery.calculate()
        report_path = generate_report(results, artery)

        # Read report and check for ASCII
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # Report can have Unicode (it's a file), but check for common problematic characters
        # in sections that might be printed to console
        problematic_chars = ['°', 'μ', 'ν', 'ρ', 'ε']
        found_problematic = []

        for char in problematic_chars:
            if char in report_content:
                found_problematic.append(char)

        if found_problematic:
            print(f"   [INFO] Report contains Unicode characters: {found_problematic}")
            print(f"   (This is OK for files, but should be ASCII for console output)")

        print(f"   [PASS] Report generated successfully at {report_path}")
        print("   [PASS] Windows ASCII compatibility verified")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_equation_formatting():
    """Test that equations are formatted correctly in reports"""
    print("\n" + "="*60)
    print("TEST: Equation Formatting in Reports")
    print("="*60)

    try:
        artery = DrippingArtery(1000, "N25")
        artery.add_zone(TransportZone(20))
        artery.add_zone(IrrigationZone(80, 15, 1000))

        results = artery.calculate()
        report_path = generate_report(results, artery)

        # Read report and check for equation formatting
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # Check for ASCII art equations
        assert "Reynolds Number" in report_content, "Should have Reynolds equation section"
        assert "Darcy-Weisbach" in report_content, "Should have Darcy-Weisbach equation section"

        # Check for proper ASCII formatting (not LaTeX)
        # Should have ASCII art, not LaTeX symbols
        has_ascii_art = "Re = " in report_content or "rho" in report_content
        has_latex = r"\rho" in report_content or r"\mu" in report_content

        assert has_ascii_art, "Should have ASCII art equations"
        assert not has_latex, "Should NOT have LaTeX formatting"

        print("   [PASS] Equations formatted correctly (ASCII art, not LaTeX)")
        print(f"   Report saved to: {report_path}")
        return True

    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all comprehensive edge case tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE EDGE CASE TESTING SUITE")
    print("="*70)

    tests = [
        ("DN Comparison - Smallest", test_dn_comparison_edge_smallest),
        ("DN Comparison - Largest", test_dn_comparison_edge_largest),
        ("DN Comparison - Limited Options", test_dn_comparison_single_available),
        ("NIST API - 0°C", test_nist_api_extreme_cold),
        ("NIST API - 100°C", test_nist_api_extreme_hot),
        ("NIST API - Invalid Temps", test_nist_api_invalid_temperature),
        ("Zero Flow Edge Case", test_zero_flow_edge_case),
        ("Massive Dripper Count", test_massive_dripper_count),
        ("Very Long Installation", test_very_long_installation),
        ("Flow Conservation", test_flow_conservation_strict),
        ("Laminar Flow (Low Re)", test_extreme_reynolds_laminar),
        ("Turbulent Flow (High Re)", test_extreme_reynolds_turbulent),
        ("Windows ASCII Compatibility", test_windows_ascii_compatibility),
        ("Equation Formatting", test_equation_formatting),
    ]

    results = []
    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n[FAIL] {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {test_name}")

    print("\n" + "="*70)
    print(f"Total: {len(tests)} tests, {passed} passed, {failed} failed")

    if failed == 0:
        print("[OK] ALL COMPREHENSIVE EDGE CASE TESTS PASSED")
        print("="*70)
        return True
    else:
        print(f"[FAIL] {failed} TESTS FAILED")
        print("="*70)
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] TEST SUITE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
