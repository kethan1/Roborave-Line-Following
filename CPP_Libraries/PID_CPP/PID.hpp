#ifndef PID_HPP
#define PID_HPP
#include <stdint.h>
#include <iostream>
#include <fstream>

class PID {
    std::ofstream file_obj;

    public:
        double P_Value, I_Value, D_Value, iAccumulator, prevError;
        bool debug, first;
        
        time_t sTime;

        PID(double P, double I = 0, double D = 0, bool debug_value = true, std::string file = "PIDvars.csv");
        double update(double target, double current);
        void reset();
        void close();
};

#endif
