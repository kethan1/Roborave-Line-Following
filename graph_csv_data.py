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

start = True
with open(filename, 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
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
            lines_of_csv.append(index)
        else:
            start = False

plt.plot(lines_of_csv, Equation, label='Equation')
plt.plot(lines_of_csv, I_Accumulator, label='I Accumulator')
# plt.plot(lines_of_csv, Prev_Error, label='Previous Error')
plt.plot(lines_of_csv, P_With_Error, label='P With Error')
plt.plot(lines_of_csv, I_With_I_Accumulator, label='I With I Accumulator')
plt.plot(lines_of_csv, D_With_Prev_Error, label='D With Prev Error')
plt.plot(lines_of_csv, setpoint, label='Setpoint')
plt.plot(lines_of_csv, Error, label='Error')
plt.xlabel('Lines of CSV')
plt.ylabel('Values')
plt.title('Robot PID')
plt.legend()
plt.show()
