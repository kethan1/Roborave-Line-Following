#ifndef PID_HPP
#define PID_HPP
#include <stdint.h>
#include <iostream>
#include <fstream>

class PID {
    public:
        double P, I, D, iAccumulator, prevError;
        bool debug, first;
        std::ofstream file;
        
        time_t sTime;

        PID(double P_value, double I_value, double D_value, bool debug_value = true, std::string file_path = "PIDvars.csv");
        double update(double target, double current);
        void reset();
        void close();
};

#endif
