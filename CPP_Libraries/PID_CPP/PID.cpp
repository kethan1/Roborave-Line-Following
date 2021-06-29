#include "PID.hpp"
#include <iostream>
#include <fstream>
#include <time.h>


PID::PID (double P_value, double I_value, double D_value, bool debug_value, std::string file_path) {
    P = P_value;
    I = I_value;
    D = D_value;
    debug = debug_value;
    first = true;
    iAccumulator = 0;
    prevError = 0;
    file.open(file_path);
    file << "Equation,I Accumulator,Error,Prev Error,P With Error,I with I Accumulator,D with Prev Error,Setpoint,Time\n";
}

double PID::update(double target, double current) {
    double error = current - target;
    iAccumulator += error;
    if (first) {
        iAccumulator = 0;
        prevError = error;
        first = false;
        sTime = time(0);
    }
    double output = (P * error) + (iAccumulator * I) + ((error - prevError) * D);

    if (debug) {
        file << output << "," << iAccumulator << "," << error << "," << prevError << "," << P * error << "," << I * iAccumulator << "," << D * (error - prevError) << "," << target << "," << time(0) - sTime;
    }

    return output;
}

void PID::reset() {
    first = true;
}

void PID::close() {
    file.close();
}
