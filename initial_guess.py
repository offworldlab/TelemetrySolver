"""
Initial guess module for telemetry solver
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Tuple
from detection import DetectionPair
from Geometry import Geometry


def calculate_ellipse_center_enu(ioo_enu: Tuple[float, float, float], 
                                sensor_enu: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Return midpoint between ellipse foci in ENU"""
    center_x = (ioo_enu[0] + sensor_enu[0]) / 2
    center_y = (ioo_enu[1] + sensor_enu[1]) / 2
    center_z = (ioo_enu[2] + sensor_enu[2]) / 2
    return center_x, center_y, center_z


def get_initial_guess(detection_pair: DetectionPair) -> List[float]:
    """
    Calculate initial position estimate
    Returns: [x, y, vx, vy] in ENU with zero velocity
    """
    # Get ENU origin (sensor midpoint)
    origin_lat, origin_lon, origin_alt = detection_pair.get_enu_origin()
    
    # Convert detection 1 positions to ENU
    sensor1_ecef = Geometry.lla2ecef(detection_pair.detection1.sensor_lat, 
                                     detection_pair.detection1.sensor_lon, 0)
    ioo1_ecef = Geometry.lla2ecef(detection_pair.detection1.ioo_lat,
                                  detection_pair.detection1.ioo_lon, 0)
    
    sensor1_enu = Geometry.ecef2enu(sensor1_ecef[0], sensor1_ecef[1], sensor1_ecef[2],
                                   origin_lat, origin_lon, origin_alt)
    ioo1_enu = Geometry.ecef2enu(ioo1_ecef[0], ioo1_ecef[1], ioo1_ecef[2],
                                 origin_lat, origin_lon, origin_alt)
    
    # Convert detection 2 positions to ENU
    sensor2_ecef = Geometry.lla2ecef(detection_pair.detection2.sensor_lat,
                                     detection_pair.detection2.sensor_lon, 0)
    ioo2_ecef = Geometry.lla2ecef(detection_pair.detection2.ioo_lat,
                                  detection_pair.detection2.ioo_lon, 0)
    
    sensor2_enu = Geometry.ecef2enu(sensor2_ecef[0], sensor2_ecef[1], sensor2_ecef[2],
                                   origin_lat, origin_lon, origin_alt)
    ioo2_enu = Geometry.ecef2enu(ioo2_ecef[0], ioo2_ecef[1], ioo2_ecef[2],
                                 origin_lat, origin_lon, origin_alt)
    
    # Calculate ellipse centers
    center1 = calculate_ellipse_center_enu(ioo1_enu, sensor1_enu)
    center2 = calculate_ellipse_center_enu(ioo2_enu, sensor2_enu)
    
    # Average the centers for initial position
    initial_x = (center1[0] + center2[0]) / 2
    initial_y = (center1[1] + center2[1]) / 2
    
    # Return with zero velocity
    return [initial_x, initial_y, 0.0, 0.0]