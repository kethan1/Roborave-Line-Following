import csv
import time


class PID:
    def __init__(self, P=1, I=0, D=0, debug=True, file="PIDvars.csv"):
        self.P = P
        self.I = I
        self.D = D
        self.debug = debug
        self.iAccumulator = 0
        self.prevError = 0
        if self.debug:
            self.fileOutput = open(file, "w")
            self.writePointer = csv.writer(self.fileOutput)
            self.writePointer.writerow([
                "Equation", "I Accumulator", "Error", "Prev Error",
                "P With Error", "I with I Accumulator", "D with Prev Error",
                "Setpoint", "PIDInput", "Time"
            ])
        self.first = True

    def update(self, target, current):
        error = target - current
        self.iAccumulator += error
        if self.first:
            self.iAccumulator = 0
            self.prevError = error
            self.first = False
            self.sTime = time.time()
        output = (self.P * error) + (self.iAccumulator * self.I) + ((error - self.prevError) * self.D)
        if self.debug:
            self.writePointer.writerow([
                output,
                self.iAccumulator,
                error,
                self.prevError,
                self.P * error,
                self.I * self.iAccumulator,
                self.D * (error-self.prevError),
                target,
                current,
                time.time() - self.sTime
            ])
        self.prevError = error

        return output

    def reset(self):
        self.first = True

    def close(self):
        if self.debug:
            self.fileOutput.close()
