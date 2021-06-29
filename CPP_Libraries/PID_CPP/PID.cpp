#include "PID.hpp"
#include <iostream>
#include <fstream>
#include <time.h>


PID::PID (double P, double I, double D, bool debug_value, std::string file) {
    P_Value = P;
    I_Value = I;
    D_Value = D;
    debug = debug_value;
    first = true;
    iAccumulator = 0;
    prevError = 0;
    file_obj.open(file);
    file_obj << "Equation,I Accumulator,Error,Prev Error,P With Error,I with I Accumulator,D with Prev Error,Setpoint,Time\n";
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
    double output = (P_Value * error) + (iAccumulator * I_Value) + ((error - prevError) * D_Value);

    if (debug) {
        file_obj << output << "," << iAccumulator << "," << error << "," << prevError << "," << P_Value * error << "," << I_Value * iAccumulator << "," << D_Value * (error - prevError) << "," << target << "," << time(0) - sTime << "\n";
    }

    return output;
}

void PID::reset() {
    first = true;
}

void PID::close() {
    file_obj.close();
}
