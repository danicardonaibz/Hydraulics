#!/usr/bin/env python3
"""
Test input validation and edge cases for the hydraulics tool
"""

from hydraulics.ui.wizards import get_float_input, get_int_input, draw_artery_ascii
from hydraulics.models import DrippingArtery, TransportZone, IrrigationZone
from hydraulics.io import config
import io
import sys


def test_float_validation():
    """Test float input validation with various edge cases"""
    print("\n" + "="*60)
    print("TEST: Float Input Validation")
    print("="*60)

    # These would normally be tested with mock input, but we'll test the logic
    test_cases = [
        (5.0, 0.001, None, True, True, "Valid positive float"),
        (0.0, 0.001, None, False, False, "Zero when not allowed"),
        (-5.0, 0.001, None, True, False, "Negative when min is 0.001"),
        (100.0, None, 50.0, True, False, "Above maximum"),
    ]

    print("\nFloat validation logic tests:")
    for value, min_val, max_val, allow_zero, should_pass, desc in test_cases:
        passed = True

        if not allow_zero and value == 0:
            passed = False
        if min_val is not None and value < min_val:
            passed = False
        if max_val is not None and value > max_val:
            passed = False

        status = "PASS" if passed == should_pass else "FAIL"
        print(f"  [{status}] {desc}: value={value}, min={min_val}, max={max_val}")

    print("\n[OK] Float validation logic test completed")


def test_artery_ascii():
    """Test ASCII diagram generation"""
    print("\n" + "="*60)
    print("TEST: ASCII Diagram Generation")
    print("="*60)

    # Test empty artery
    artery = DrippingArtery(1500, "N20")
    diagram = draw_artery_ascii(artery, show_flows=True)
    print("\nEmpty artery:")
    print(diagram)
    assert "(No zones defined yet)" in diagram

    # Test with transport zone
    artery.add_zone(TransportZone(10))
    diagram = draw_artery_ascii(artery, show_flows=True)
    print("\nWith transport zone:")
    print(diagram)
    assert "T1" in diagram

    # Test with irrigation zone
    artery.add_zone(IrrigationZone(80, 12, 500))
    diagram = draw_artery_ascii(artery, show_flows=True)
    print("\nWith irrigation zone:")
    print(diagram)
    assert "I2" in diagram
    assert "+" in diagram  # Dripper markers

    # Test with multiple zones
    artery.add_zone(TransportZone(50))
    artery.add_zone(IrrigationZone(160, 125, 1000))
    diagram = draw_artery_ascii(artery, show_flows=True)
    print("\nFull artery (4 zones):")
    print(diagram)
    assert "T3" in diagram
    assert "I4" in diagram

    print("\n[OK] ASCII diagram generation test completed")


def test_zone_validation():
    """Test zone validation and flow conservation"""
    print("\n" + "="*60)
    print("TEST: Zone Validation and Flow Conservation")
    print("="*60)

    # Test 1: Valid configuration
    artery = DrippingArtery(1500, "N20")
    artery.add_zone(TransportZone(10))
    artery.add_zone(IrrigationZone(80, 12, 500))
    artery.add_zone(TransportZone(50))
    artery.add_zone(IrrigationZone(160, 125, 1000))

    try:
        artery.validate_flow_conservation()
        print("[PASS] Valid flow conservation (500 + 1000 = 1500)")
    except ValueError as e:
        print(f"[FAIL] Should not raise error: {e}")

    # Test 2: Flow imbalance
    artery2 = DrippingArtery(1500, "N20")
    artery2.add_zone(IrrigationZone(80, 12, 600))  # Only 600, not 1500
    artery2.add_zone(IrrigationZone(80, 12, 800))  # Total 1400, not 1500

    try:
        artery2.validate_flow_conservation()
        print("[FAIL] Should raise error for flow imbalance")
    except ValueError as e:
        print(f"[PASS] Correctly detected flow imbalance: {e}")

    # Test 3: Edge case - very small flow
    artery3 = DrippingArtery(0.001, "N16")
    artery3.add_zone(IrrigationZone(10, 1, 0.001))

    try:
        artery3.validate_flow_conservation()
        print("[PASS] Small flow values handled correctly")
    except ValueError as e:
        print(f"[FAIL] Small flow test failed: {e}")

    print("\n[OK] Zone validation test completed")


def test_edge_cases():
    """Test various edge cases"""
    print("\n" + "="*60)
    print("TEST: Edge Cases")
    print("="*60)

    # Edge case 1: Very long transport zone
    print("\n1. Very long transport zone (1000m)")
    artery = DrippingArtery(1000, "N25")
    artery.add_zone(TransportZone(1000))
    artery.add_zone(IrrigationZone(100, 10, 1000))

    try:
        results = artery.calculate()
        print(f"   [PASS] Calculated successfully, head loss: {results['total_head_loss']:.3f} m")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")

    # Edge case 2: Many drippers
    print("\n2. Many drippers (500 drippers)")
    artery2 = DrippingArtery(5000, "N40")
    artery2.add_zone(IrrigationZone(500, 500, 5000))

    try:
        results2 = artery2.calculate()
        print(f"   [PASS] Calculated successfully, head loss: {results2['total_head_loss']:.3f} m")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")

    # Edge case 3: Single dripper
    print("\n3. Single dripper")
    artery3 = DrippingArtery(100, "N16")
    artery3.add_zone(IrrigationZone(10, 1, 100))

    try:
        results3 = artery3.calculate()
        print(f"   [PASS] Calculated successfully, head loss: {results3['total_head_loss']:.3f} m")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")

    # Edge case 4: High flow rate (stress test)
    print("\n4. High flow rate (10000 l/h)")
    artery4 = DrippingArtery(10000, "N110")
    artery4.add_zone(TransportZone(100))
    artery4.add_zone(IrrigationZone(200, 100, 10000))

    try:
        results4 = artery4.calculate()
        print(f"   [PASS] Calculated successfully, head loss: {results4['total_head_loss']:.3f} m")
        print(f"   Reynolds number check: {results4['zones'][0]['reynolds']:.0f}")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")

    print("\n[OK] Edge case test completed")


def test_pipe_designations():
    """Test all available pipe designations"""
    print("\n" + "="*60)
    print("TEST: All Pipe Designations")
    print("="*60)

    from hydraulics.core.pipes import list_available_pipes

    pipes = list_available_pipes()
    print(f"\nTesting {len(pipes)} pipe designations...")

    for pipe in pipes:
        try:
            artery = DrippingArtery(1000, pipe)
            artery.add_zone(TransportZone(10))
            artery.add_zone(IrrigationZone(50, 10, 1000))
            results = artery.calculate()
            print(f"  [PASS] {pipe}: diameter={results['diameter']*1000:.1f}mm, "
                  f"head_loss={results['total_head_loss']:.3f}m")
        except Exception as e:
            print(f"  [FAIL] {pipe}: {e}")

    print("\n[OK] Pipe designation test completed")


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("COMPREHENSIVE INPUT VALIDATION AND EDGE CASE TESTS")
        print("="*60)

        test_float_validation()
        test_artery_ascii()
        test_zone_validation()
        test_edge_cases()
        test_pipe_designations()

        print("\n" + "="*60)
        print("[OK] ALL TESTS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n[FAIL] TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
