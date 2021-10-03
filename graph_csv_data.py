#!/usr/bin/env python3

import matplotlib.pyplot as plt
import csv
import sys

filename = "rev_per_second.csv"
if sys.argv[1:]:
    filename = sys.argv[1]

Equation = []
I_Accumulator = []
Error = []
Prev_Error = []
P_With_Error = []
I_With_I_Accumulator = []
D_With_Prev_Error = []
lines_of_csv = []
setpoint = []
theTime = []
PIDInput = []

start = True
with open(filename, "r") as csvfile:
    plots = csv.reader(csvfile, delimiter=",")
    for index, row in enumerate(plots):
        if not start:
            Equation.append(float(row[0]))
            I_Accumulator.append(float(row[1]))
            Error.append(float(row[2]))
            Prev_Error.append(float(row[3]))
            P_With_Error.append(float(row[4]))
            I_With_I_Accumulator.append(float(row[5]))
            D_With_Prev_Error.append(float(row[6]))
            setpoint.append(float(row[7]))
            PIDInput.append(float(row[8]))
            theTime.append(float(row[9]))
            lines_of_csv.append(index)
        else:
            start = False

plt.plot(theTime, Equation, label="Equation")
plt.plot(theTime, I_Accumulator, label="I Accumulator")
# plt.plot(theTime, Prev_Error, label='Previous Error')
plt.plot(theTime, P_With_Error, label="P With Error")
plt.plot(theTime, I_With_I_Accumulator, label="I With I Accumulator")
plt.plot(theTime, D_With_Prev_Error, label="D With Prev Error")
plt.plot(theTime, setpoint, label="Setpoint")
plt.plot(theTime, Error, label="Error")
plt.plot(theTime, PIDInput, "-o", label="Input")
plt.xlabel("Time in Seconds")
plt.ylabel("Values")
plt.title("Robot PID")
plt.legend()
plt.show()
