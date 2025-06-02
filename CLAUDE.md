- We are making a telemetry solver for a bistatic passive radar aggregation server. It has two modules, an initial guess module and a Levenberg–Marquardt Least Squares solver module.
- Each sensor with a fixed, known, location is paired with a illuminator of opportunity (IoO) with a fixed, known, location. The sensors have a reference and survellience antenna on coherent channels on an SDR with a TCXO, so the TDOA and FDOA can be caluclated locally and then sent to the server. The bistatic range reported is the total path IoO→Target→Sensor. The FDOA is the frequency difference of IoO→Sensor compared to IoO→Target→Sensor with negative sign meaning reduction in frequency from sensors POV. Sensors may share IoO, or have different IoO.
- The program will be provided two simultaneous detections via JSON, each with the following information: Sensor position (lat, long), IoO position (lat, long), Transmission frequency in MHz, Timestamp in Unix time milliseconds, Bistatic range in km, Doppler shift in Hz.
- Start as simply as possible. Make and test the smallest possible additions as you go. Make everything as modular as possible. Use existing libraries when possible, though be mindful of excessively increasing dependencies.
- Use Geometery.py to convert between coordinate systems. Input and output of the entire system should be LLA, but use ENU interally for calculations.
- Solve for 2D position (x,y) and velocity (vx,vy) only. Altitude (z) assumed to be 5km, and vertical velocity (vz) assumed to be 0. 
- Do not add features not explicitly asked for unless strictly necessary for function. Do not get sidetracked, follow the todo list closely. After each addition, test its functionality before moving on.
-Report "No Solution" error if the solver does not converge. We will add sanity-checking for solutions later.
-Output should be a JSON with Timestamp, LLA of solution, velocity in ENU (convariance reporting functionality will be added later).

