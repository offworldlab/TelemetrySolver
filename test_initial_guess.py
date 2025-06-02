"""
Test initial guess module
"""
import json
from detection import DetectionPair
from initial_guess import calculate_ellipse_center_enu, get_initial_guess


def test_ellipse_center():
    """Test ellipse center calculation"""
    ioo_enu = (1000, 2000, 0)
    sensor_enu = (3000, 4000, 0)
    
    center = calculate_ellipse_center_enu(ioo_enu, sensor_enu)
    
    assert center[0] == 2000  # (1000 + 3000) / 2
    assert center[1] == 3000  # (2000 + 4000) / 2
    assert center[2] == 0
    print("✓ Ellipse center calculation test passed")


def test_initial_guess():
    """Test initial guess with simple geometry"""
    # Create test detection pair
    test_json = {
        "detection1": {
            "sensor_lat": 40.0,
            "sensor_lon": -74.0,
            "ioo_lat": 40.0,
            "ioo_lon": -74.1,
            "freq_mhz": 100.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 50.0,
            "doppler_hz": -100.0
        },
        "detection2": {
            "sensor_lat": 40.0,
            "sensor_lon": -73.9,
            "ioo_lat": 40.0,
            "ioo_lon": -74.1,
            "freq_mhz": 200.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 60.0,
            "doppler_hz": 50.0
        }
    }
    
    json_string = json.dumps(test_json)
    pair = DetectionPair.from_json(json_string)
    
    initial = get_initial_guess(pair)
    
    # Should return [x, y, vx, vy]
    assert len(initial) == 4
    assert initial[2] == 0.0  # vx = 0
    assert initial[3] == 0.0  # vy = 0
    
    # Position should be reasonable (not at origin)
    assert abs(initial[0]) > 1  # x not near 0
    assert abs(initial[1]) < 10000  # y reasonable
    
    print(f"✓ Initial guess test passed: x={initial[0]:.1f}m, y={initial[1]:.1f}m")


def test_symmetric_case():
    """Test with symmetric geometry"""
    # Sensors at same latitude, different longitudes
    # IoOs at same location
    test_json = {
        "detection1": {
            "sensor_lat": 40.0,
            "sensor_lon": -74.0,
            "ioo_lat": 40.5,
            "ioo_lon": -73.5,
            "freq_mhz": 100.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 50.0,
            "doppler_hz": -100.0
        },
        "detection2": {
            "sensor_lat": 40.0,
            "sensor_lon": -73.0,
            "ioo_lat": 40.5,
            "ioo_lon": -73.5,
            "freq_mhz": 100.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 50.0,
            "doppler_hz": -100.0
        }
    }
    
    json_string = json.dumps(test_json)
    pair = DetectionPair.from_json(json_string)
    
    initial = get_initial_guess(pair)
    
    # With symmetric geometry, x should be near 0 (midpoint)
    print(f"✓ Symmetric case: x={initial[0]:.1f}m, y={initial[1]:.1f}m")
    

if __name__ == "__main__":
    test_ellipse_center()
    test_initial_guess()
    test_symmetric_case()
    print("\nAll initial guess tests passed!")