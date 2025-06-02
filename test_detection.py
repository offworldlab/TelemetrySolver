"""
Test detection module
"""
import json
import tempfile
from detection import Detection, DetectionPair, load_detections


def test_detection_creation():
    """Test creating a detection"""
    det = Detection(
        sensor_lat=40.0,
        sensor_lon=-74.0,
        ioo_lat=40.5,
        ioo_lon=-73.5,
        freq_mhz=100.0,
        timestamp=1234567890,
        bistatic_range_km=50.0,
        doppler_hz=-100.0
    )
    assert det.validate() == True
    print("✓ Detection creation test passed")


def test_detection_validation():
    """Test detection validation"""
    # Invalid latitude
    det = Detection(
        sensor_lat=100.0,  # Invalid
        sensor_lon=-74.0,
        ioo_lat=40.5,
        ioo_lon=-73.5,
        freq_mhz=100.0,
        timestamp=1234567890,
        bistatic_range_km=50.0,
        doppler_hz=-100.0
    )
    assert det.validate() == False
    
    # Invalid range
    det.sensor_lat = 40.0
    det.bistatic_range_km = -1.0
    assert det.validate() == False
    print("✓ Detection validation test passed")


def test_detection_pair_json():
    """Test JSON parsing"""
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
            "sensor_lat": 41.0,
            "sensor_lon": -73.0,
            "ioo_lat": 40.5,
            "ioo_lon": -73.5,
            "freq_mhz": 200.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 60.0,
            "doppler_hz": 50.0
        }
    }
    
    json_string = json.dumps(test_json)
    pair = DetectionPair.from_json(json_string)
    
    assert pair.detection1.sensor_lat == 40.0
    assert pair.detection2.freq_mhz == 200.0
    print("✓ JSON parsing test passed")


def test_enu_origin():
    """Test ENU origin calculation"""
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
            "sensor_lat": 42.0,
            "sensor_lon": -72.0,
            "ioo_lat": 40.5,
            "ioo_lon": -73.5,
            "freq_mhz": 200.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 60.0,
            "doppler_hz": 50.0
        }
    }
    
    json_string = json.dumps(test_json)
    pair = DetectionPair.from_json(json_string)
    lat, lon, alt = pair.get_enu_origin()
    
    assert lat == 41.0  # Midpoint
    assert lon == -73.0  # Midpoint
    assert alt == 0
    print("✓ ENU origin test passed")


def test_load_detections():
    """Test loading from file"""
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
            "sensor_lat": 41.0,
            "sensor_lon": -73.0,
            "ioo_lat": 40.5,
            "ioo_lon": -73.5,
            "freq_mhz": 200.0,
            "timestamp": 1234567890,
            "bistatic_range_km": 60.0,
            "doppler_hz": 50.0
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_json, f)
        temp_file = f.name
    
    pair = load_detections(temp_file)
    assert pair.detection1.sensor_lat == 40.0
    print("✓ File loading test passed")


if __name__ == "__main__":
    test_detection_creation()
    test_detection_validation()
    test_detection_pair_json()
    test_enu_origin()
    test_load_detections()
    print("\nAll detection tests passed!")