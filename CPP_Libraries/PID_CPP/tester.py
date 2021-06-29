from PID import PID

test_pid = PID(1)

assert test_pid.update(1, 9) == 8.0
assert test_pid.update(1, 1) == 0.0
assert test_pid.update(5, 1) == -4.0
