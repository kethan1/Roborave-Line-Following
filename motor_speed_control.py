from typing import List
import math


class MotorSpeedControl:
    """Enables easy passing of motor speed."""
    def __init__(self, base_speed: int, max_speed: int = 1.4):
        self.speed_separate = []
        self.base_speed = base_speed
        self.target_speed = 0
        self.max_speed = max_speed

    def get_speed(self) -> List[int, int]:
        """Returns the speed"""
        if not self.speed_separate:
            return [self.base_speed + self.target_speed, self.base_speed - self.target_speed]
        return self.speed_separate

    def set_target_speed(self, target_speed) -> None:
        """Sets the target speed"""
        self.target_speed = target_speed if abs(target_speed) <= self.max_speed \
            else math.copysign(self.max_speed, target_speed)
