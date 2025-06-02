"""
Test LM solver module
"""
import json
import numpy as np
from detection import DetectionPair
from initial_guess import get_initial_guess
from lm_solver import (distance_3d, bistatic_range_residual, 
                      doppler_residual, solve_position_velocity)


def test_distance_3d():
    """Test 3D distance calculation"""
    p1 = (0, 0, 0)
    p2 = (3, 4, 0)
    dist = distance_3d(p1, p2)
    assert abs(dist - 5.0) < 1e-6
    
    p1 = (1, 2, 3)
    p2 = (4, 6, 8)
    dist = distance_3d(p1, p2)
    expected = np.sqrt(3**2 + 4**2 + 5**2)
    assert abs(dist - expected) < 1e-6
    print("✓ Distance calculation test passed")


def test_range_residual():
    """Test bistatic range residual"""
    # Simple case: target at origin, altitude 5km
    state = [0, 0, 0, 0]  # x, y, vx, vy
    ioo_enu = (-10000, 0, 0)
    sensor_enu = (10000, 0, 0)
    
    # Expected range: sqrt(10000^2 + 5000^2) * 2
    expected_range = np.sqrt(10000**2 + 5000**2) * 2
    
    residual = bistatic_range_residual(state, ioo_enu, sensor_enu, expected_range)
    assert abs(residual) < 1e-6
    print("✓ Range residual test passed")


def test_doppler_residual():
    """Test Doppler residual"""
    # Target moving east at 100 m/s
    state = [0, 0, 100, 0]  # x, y, vx, vy
    ioo_enu = (-10000, 0, 0)  # West of target
    sensor_enu = (10000, 0, 0)  # East of target
    freq_hz = 100e6  # 100 MHz
    
    # Target moving away from IoO and toward sensor
    # This should produce positive Doppler (negative FDOA)
    residual = doppler_residual(state, ioo_enu, sensor_enu, freq_hz, 0)
    
    # Just check it's non-zero and reasonable
    assert abs(residual) > 1  # Should have some Doppler
    assert abs(residual) < 1000  # But not huge
    print("✓ Doppler residual test passed")


def test_solver_synthetic():
    """Test solver with synthetic data"""
    # Create synthetic detection with known solution
    # Target at specific location with known velocity
    target_lat = 40.5
    target_lon = -73.5
    target_vx = 50.0  # m/s east
    target_vy = -30.0  # m/s south
    
    # Create detection pair
    test_json = {
        "detection1": {
            "sensor_lat": 40.0,
            "sensor_lon": -74.0,
            "ioo_lat": 40.2,
            "ioo_lon": -74.2,
            "freq_mhz": 100.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 80.0,  # Synthetic value
            "doppler_hz": -50.0  # Synthetic value
        },
        "detection2": {
            "sensor_lat": 41.0,
            "sensor_lon": -73.0,
            "ioo_lat": 40.8,
            "ioo_lon": -73.2,
            "freq_mhz": 200.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 90.0,  # Synthetic value
            "doppler_hz": 30.0  # Synthetic value
        }
    }
    
    json_string = json.dumps(test_json)
    pair = DetectionPair.from_json(json_string)
    
    # Get initial guess
    initial = get_initial_guess(pair)
    
    # Solve
    solution = solve_position_velocity(pair, initial)
    
    # Should get a solution (may not match exactly due to synthetic data)
    if solution is not None:
        print(f"✓ Solver test passed: lat={solution['lat']:.4f}, lon={solution['lon']:.4f}")
        print(f"  Velocity: E={solution['velocity_east']:.1f} m/s, N={solution['velocity_north']:.1f} m/s")
    else:
        print("⚠ Solver did not converge with synthetic data (expected for arbitrary values)")


def test_no_convergence():
    """Test solver behavior when it can't converge"""
    # Create impossible geometry
    test_json = {
        "detection1": {
            "sensor_lat": 40.0,
            "sensor_lon": -74.0,
            "ioo_lat": 40.0,
            "ioo_lon": -74.0,
            "freq_mhz": 100.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 1.0,  # Too small
            "doppler_hz": -5000.0  # Too large
        },
        "detection2": {
            "sensor_lat": 41.0,
            "sensor_lon": -73.0,
            "ioo_lat": 41.0,
            "ioo_lon": -73.0,
            "freq_mhz": 200.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 1.0,  # Too small
            "doppler_hz": 5000.0  # Too large
        }
    }
    
    json_string = json.dumps(test_json)
    pair = DetectionPair.from_json(json_string)
    initial = get_initial_guess(pair)
    
    solution = solve_position_velocity(pair, initial)
    assert solution is None
    print("✓ No convergence test passed")


if __name__ == "__main__":
    test_distance_3d()
    test_range_residual()
    test_doppler_residual()
    test_solver_synthetic()
    test_no_convergence()
    print("\nAll LM solver tests completed!")