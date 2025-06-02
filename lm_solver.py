"""
Levenberg-Marquardt solver module for telemetry solver
"""
import numpy as np
from scipy.optimize import least_squares
from typing import List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detection import DetectionPair
from Geometry import Geometry


def distance_3d(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
    """Calculate Euclidean distance between two 3D points"""
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)


def bistatic_range_residual(state: List[float], ioo_enu: Tuple[float, float, float],
                           sensor_enu: Tuple[float, float, float], 
                           measured_range_m: float) -> float:
    """Calculate range residual"""
    # Extract position from state (z=5000m fixed)
    target_pos = (state[0], state[1], 5000.0)
    
    # Calculate bistatic range
    range_ioo_target = distance_3d(ioo_enu, target_pos)
    range_target_sensor = distance_3d(target_pos, sensor_enu)
    calculated_range = range_ioo_target + range_target_sensor
    
    return calculated_range - measured_range_m


def doppler_residual(state: List[float], ioo_enu: Tuple[float, float, float],
                    sensor_enu: Tuple[float, float, float],
                    freq_hz: float, measured_doppler_hz: float) -> float:
    """Calculate Doppler residual"""
    # Extract position and velocity from state
    target_pos = np.array([state[0], state[1], 5000.0])
    target_vel = np.array([state[2], state[3], 0.0])
    
    # Speed of light
    c = 299792458.0  # m/s
    
    # Calculate unit vectors
    # IoO to target
    ioo_to_target = target_pos - np.array(ioo_enu)
    dist_ioo_target = np.linalg.norm(ioo_to_target)
    unit_ioo_target = ioo_to_target / dist_ioo_target
    
    # Target to sensor
    target_to_sensor = np.array(sensor_enu) - target_pos
    dist_target_sensor = np.linalg.norm(target_to_sensor)
    unit_target_sensor = target_to_sensor / dist_target_sensor
    
    # Radial velocities
    v_radial_ioo = np.dot(target_vel, unit_ioo_target)
    v_radial_sensor = np.dot(target_vel, unit_target_sensor)
    
    # Bistatic Doppler
    # Negative sign because FDOA is frequency difference (direct - reflected)
    doppler_ratio = -(v_radial_ioo + v_radial_sensor) / c
    calculated_doppler = freq_hz * doppler_ratio
    
    return calculated_doppler - measured_doppler_hz


def residual_function(state: List[float], detection_pair: DetectionPair, 
                     enu_origin: Tuple[float, float, float]) -> np.ndarray:
    """Calculate all residuals for the system"""
    origin_lat, origin_lon, origin_alt = enu_origin
    
    # Convert all positions to ENU
    # Detection 1
    sensor1_ecef = Geometry.lla2ecef(detection_pair.detection1.sensor_lat,
                                     detection_pair.detection1.sensor_lon, 0)
    ioo1_ecef = Geometry.lla2ecef(detection_pair.detection1.ioo_lat,
                                  detection_pair.detection1.ioo_lon, 0)
    
    sensor1_enu = Geometry.ecef2enu(sensor1_ecef[0], sensor1_ecef[1], sensor1_ecef[2],
                                   origin_lat, origin_lon, origin_alt)
    ioo1_enu = Geometry.ecef2enu(ioo1_ecef[0], ioo1_ecef[1], ioo1_ecef[2],
                                 origin_lat, origin_lon, origin_alt)
    
    # Detection 2
    sensor2_ecef = Geometry.lla2ecef(detection_pair.detection2.sensor_lat,
                                     detection_pair.detection2.sensor_lon, 0)
    ioo2_ecef = Geometry.lla2ecef(detection_pair.detection2.ioo_lat,
                                  detection_pair.detection2.ioo_lon, 0)
    
    sensor2_enu = Geometry.ecef2enu(sensor2_ecef[0], sensor2_ecef[1], sensor2_ecef[2],
                                   origin_lat, origin_lon, origin_alt)
    ioo2_enu = Geometry.ecef2enu(ioo2_ecef[0], ioo2_ecef[1], ioo2_ecef[2],
                                 origin_lat, origin_lon, origin_alt)
    
    # Convert measurements
    range1_m = detection_pair.detection1.bistatic_range_km * 1000
    range2_m = detection_pair.detection2.bistatic_range_km * 1000
    freq1_hz = detection_pair.detection1.freq_mhz * 1e6
    freq2_hz = detection_pair.detection2.freq_mhz * 1e6
    
    # Calculate residuals
    residuals = np.array([
        bistatic_range_residual(state, ioo1_enu, sensor1_enu, range1_m),
        doppler_residual(state, ioo1_enu, sensor1_enu, freq1_hz, 
                        detection_pair.detection1.doppler_hz),
        bistatic_range_residual(state, ioo2_enu, sensor2_enu, range2_m),
        doppler_residual(state, ioo2_enu, sensor2_enu, freq2_hz,
                        detection_pair.detection2.doppler_hz)
    ])
    
    return residuals


def solve_position_velocity(detection_pair: DetectionPair, 
                           initial_guess: List[float]) -> Optional[dict]:
    """
    Solve for position and velocity using Levenberg-Marquardt
    Returns solution dict or None if failed
    """
    enu_origin = detection_pair.get_enu_origin()
    
    # Run optimization
    result = least_squares(
        residual_function,
        initial_guess,
        args=(detection_pair, enu_origin),
        method='lm',
        ftol=1e-6  # For 10m convergence
    )
    
    if not result.success:
        return None
    
    # Extract solution
    x_enu, y_enu, vx_enu, vy_enu = result.x
    
    # Convert position from ENU to ECEF then to LLA
    origin_lat, origin_lon, origin_alt = enu_origin
    target_ecef = Geometry.enu2ecef(x_enu, y_enu, 5000.0,
                                    origin_lat, origin_lon, origin_alt)
    target_lla = Geometry.ecef2lla(target_ecef[0], target_ecef[1], target_ecef[2])
    
    # Check convergence (position error < 10m)
    final_residuals = residual_function(result.x, detection_pair, enu_origin)
    range_residuals = [abs(final_residuals[0]), abs(final_residuals[2])]
    if max(range_residuals) > 10.0:
        return None
    
    return {
        'lat': target_lla[0],
        'lon': target_lla[1],
        'alt': 5000.0,
        'velocity_east': vx_enu,
        'velocity_north': vy_enu,
        'velocity_up': 0.0
    }