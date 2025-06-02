"""
Main program for telemetry solver
"""
import sys
import json
import argparse
from typing import Dict

from detection import load_detections
from initial_guess import get_initial_guess
from lm_solver import solve_position_velocity


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Telemetry solver for bistatic passive radar')
    parser.add_argument('input_file', help='JSON file containing detection data')
    args = parser.parse_args()
    
    try:
        # Load detections
        detection_pair = load_detections(args.input_file)
        
        # Get initial guess
        initial_guess = get_initial_guess(detection_pair)
        
        # Solve for position and velocity
        solution = solve_position_velocity(detection_pair, initial_guess)
        
        if solution is None:
            # No convergence
            output = {"error": "No Solution"}
        else:
            # Format output
            output = {
                "timestamp": detection_pair.detection1.timestamp,
                "latitude": solution['lat'],
                "longitude": solution['lon'],
                "altitude": solution['alt'],
                "velocity_east": solution['velocity_east'],
                "velocity_north": solution['velocity_north'],
                "velocity_up": solution['velocity_up']
            }
        
        # Print JSON output
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        # Handle errors
        error_output = {"error": str(e)}
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()