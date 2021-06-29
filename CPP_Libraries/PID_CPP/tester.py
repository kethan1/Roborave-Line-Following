import PID

test_pid = PID(P=1)

print(test_pid.update(9, 1))
