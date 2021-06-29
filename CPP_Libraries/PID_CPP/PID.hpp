#ifndef PID_HPP
#define PID_HPP
#include <stdint.h>
#include <iostream>
#include <fstream>

class PID {
    std::ofstream file;

    public:
        double P, I, D, iAccumulator, prevError;
        bool debug, first;
        
        time_t sTime;

        PID(double P_value, double I_value = 0, double D_value = 0, bool debug_value = true, std::string file_path = "PIDvars.csv");
        double update(double target, double current);
        void reset();
        void close();
};

#endif
