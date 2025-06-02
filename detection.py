"""
Detection data structures for telemetry solver
"""
import json
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Detection:
    """Single detection data"""
    sensor_lat: float
    sensor_lon: float
    ioo_lat: float
    ioo_lon: float
    freq_mhz: float
    timestamp: int
    bistatic_range_km: float
    doppler_hz: float
    
    def validate(self) -> bool:
        """Check data validity"""
        if not (-90 <= self.sensor_lat <= 90):
            return False
        if not (-180 <= self.sensor_lon <= 180):
            return False
        if not (-90 <= self.ioo_lat <= 90):
            return False
        if not (-180 <= self.ioo_lon <= 180):
            return False
        if self.freq_mhz <= 0:
            return False
        if self.bistatic_range_km <= 0:
            return False
        return True


@dataclass
class DetectionPair:
    """Container for two simultaneous detections"""
    detection1: Detection
    detection2: Detection
    
    @classmethod
    def from_json(cls, json_string: str) -> 'DetectionPair':
        """Parse input JSON"""
        data = json.loads(json_string)
        
        det1_data = data['detection1']
        det1 = Detection(
            sensor_lat=det1_data['sensor_lat'],
            sensor_lon=det1_data['sensor_lon'],
            ioo_lat=det1_data['ioo_lat'],
            ioo_lon=det1_data['ioo_lon'],
            freq_mhz=det1_data['freq_mhz'],
            timestamp=det1_data['timestamp'],
            bistatic_range_km=det1_data['bistatic_range_km'],
            doppler_hz=det1_data['doppler_hz']
        )
        
        det2_data = data['detection2']
        det2 = Detection(
            sensor_lat=det2_data['sensor_lat'],
            sensor_lon=det2_data['sensor_lon'],
            ioo_lat=det2_data['ioo_lat'],
            ioo_lon=det2_data['ioo_lon'],
            freq_mhz=det2_data['freq_mhz'],
            timestamp=det2_data['timestamp'],
            bistatic_range_km=det2_data['bistatic_range_km'],
            doppler_hz=det2_data['doppler_hz']
        )
        
        return cls(det1, det2)
    
    def get_enu_origin(self) -> Tuple[float, float, float]:
        """Calculate midpoint between sensors in LLA"""
        lat = (self.detection1.sensor_lat + self.detection2.sensor_lat) / 2
        lon = (self.detection1.sensor_lon + self.detection2.sensor_lon) / 2
        alt = 0  # Sea level for origin
        return lat, lon, alt


def load_detections(json_file: str) -> DetectionPair:
    """Load and validate input"""
    with open(json_file, 'r') as f:
        json_string = f.read()
    
    pair = DetectionPair.from_json(json_string)
    
    if not pair.detection1.validate():
        raise ValueError("Detection 1 validation failed")
    if not pair.detection2.validate():
        raise ValueError("Detection 2 validation failed")
    
    return pair