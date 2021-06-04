import matplotlib.pyplot as plt
import csv

Equation = []
I_Accumulator = []
Error = []
Prev_Error = []
P_With_Error = []
I_With_I_Accumulator = []
D_With_Prev_Error = []
x = []
start = True
with open('PIDvars.csv', 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for index, row in enumerate(plots):
        if not start:
            Equation.append(float(row[0]))
            I_Accumulator.append(float(row[1]))
            Error.append(float(row[2]))
            Prev_Error.append(float(row[3]))
            P_With_Error.append(float(row[7]))
            I_With_I_Accumulator.append(float(row[8]))
            D_With_Prev_Error.append(float(row[9]))
            x.append(index)
        else:
            start = False

plt.plot(x, Equation, label='Equation')
plt.plot(x, I_Accumulator, label='I Accumulator')
plt.plot(x, Error, label='Error')
plt.plot(x, Prev_Error, label='Previous Error')
plt.plot(x, P_With_Error, label='P With Error')
plt.plot(x, I_With_I_Accumulator, label='I With I Accumulator')
plt.plot(x, D_With_Prev_Error, label='D With Prev Error')
plt.xlabel('Lines of CSV')
plt.ylabel('Values')
plt.title('Robot PID')
plt.legend()
plt.show()
