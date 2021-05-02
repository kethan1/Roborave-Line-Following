import matplotlib.pyplot as plt
import csv

Equation = []
I_Accumulator = []
Error = []
Prev_Error = []
P = []
I = []
D = []
P_With_Error = []
I_With_I_Accumulator = []
D_With_Prev_Error = []
y = []
start = True
with open('PIDvars.csv', 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for index, row in enumerate(plots):
        if not start:
            Equation.append(float(row[0]))
            I_Accumulator.append(float(row[1]))
            Error.append(float(row[2]))
            Prev_Error.append(float(row[3]))
            P.append(float(row[4]))
            I.append(float(row[5]))
            D.append(float(row[6]))
            P_With_Error.append(float(row[7]))
            I_With_I_Accumulator.append(float(row[8]))
            D_With_Prev_Error.append(float(row[9]))
            y.append(index)
        else:
            start = False

plt.plot(Equation, y, label='Equation')
plt.plot(I_Accumulator, y, label='I Accumulator')
plt.plot(Error, y, label='Error')
plt.plot(Prev_Error, y, label='Previous Error')
plt.plot(P, y, label='P')
plt.plot(I, y, label='I')
plt.plot(D, y, label='D')
plt.plot(P_With_Error, y, label='P With Error')
plt.plot(I_With_I_Accumulator, y, label='I With I Accumulator')
plt.plot(D_With_Prev_Error, y, label='D With Prev Error')
plt.xlabel('Values')
plt.ylabel('Lines of CSV')
plt.title('Robot PID')
plt.legend()
plt.show()
