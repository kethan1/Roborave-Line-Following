import csv

class PID:
    def __init__(self, P, I, D, debug=True):
        self.P = P
        self.I = I
        self.D = D
        self.debug = debug
        self.iAccumulator = 0
        self.prevError = 0
        self.fileOutput = open("PIDvars.csv", "w")
        self.writePointer = csv.writer(
            self.fileOutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        self.writePointer.writerow(["Equation", "I Accumulator", "Error", "Prev Error", "P", "I", "D", "P With Error", "I with I Accumulator", "D with Prev Error"])
        self.first = True

    def update(self, target, current):
        error = current-target
        self.iAccumulator += error
        if self.first:
            self.iAccumulator = 0
            self.prevError = error
            self.first = False
        output = (self.P*error)+(self.iAccumulator*self.I) + \
            ((error-self.prevError)*self.D)
        if self.debug:
            self.writePointer.writerow([
                output,
                self.iAccumulator,
                error,
                self.prevError,
                self.P,
                self.I,
                self.D,
                self.P * error,
                self.I*self.iAccumulator,
                self.D * (error-self.prevError)
            ])
        self.prevError = error

        return output

    def reset(self):
        self.first = True

    def close(self):
        self.fileOutput.close()
