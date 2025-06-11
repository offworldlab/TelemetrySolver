"""
Main program for 3-detection telemetry solver
"""
import sys
import json
import argparse
from typing import Dict

from detection_triple import load_detections
from initial_guess_3det import get_initial_guess
from lm_solver_3det import solve_position_velocity_3d


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='3-Detection telemetry solver for bistatic passive radar')
    parser.add_argument('input_file', help='JSON file containing 3 detection data')
    args = parser.parse_args()
    
    try:
        # Load detections
        detection_triple = load_detections(args.input_file)
        
        # Get initial guess (6D)
        initial_guess = get_initial_guess(detection_triple)
        
        # Solve for position and velocity
        solution = solve_position_velocity_3d(detection_triple, initial_guess)
        
        if solution is None:
            # No convergence
            output = {"error": "No Solution"}
        else:
            # Format output
            output = {
                "timestamp": detection_triple.detection1.timestamp,
                "latitude": solution['lat'],
                "longitude": solution['lon'],
                "altitude": solution['alt'],
                "velocity_east": solution['velocity_east'],
                "velocity_north": solution['velocity_north'],
                "velocity_up": solution['velocity_up'],
                "convergence_metric": solution['convergence_metric'],
                "residuals": solution['residuals']
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