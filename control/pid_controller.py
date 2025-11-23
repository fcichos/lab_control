"""
PID Controller Implementation
"""
import time
import numpy as np
import logging


class PIDController:
    """PID controller with anti-windup"""

    def __init__(self, kp: float, ki: float, kd: float,
                 output_limits: tuple = (0, 100)):
        """
        Initialize PID controller

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            output_limits: (min, max) output limits
        """
        self.logger = logging.getLogger(__name__)
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min, self.output_max = output_limits

        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

        self.logger.info(f"PID Controller initialized: Kp={kp}, Ki={ki}, Kd={kd}")

    def update(self, error: float) -> float:
        """
        Calculate PID control output

        Args:
            error: Current error (setpoint - measured)

        Returns:
            Control output
        """
        current_time = time.time()
        dt = current_time - self.last_time

        if dt <= 0:
            dt = 0.001  # Prevent division by zero

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * dt
        i_term = self.ki * self.integral

        # Derivative term
        derivative = (error - self.last_error) / dt
        d_term = self.kd * derivative

        # Calculate output
        output = p_term + i_term + d_term

        # Apply limits
        output = np.clip(output, self.output_min, self.output_max)

        # Anti-windup: prevent integral windup
        if output != (p_term + i_term + d_term):
            self.integral -= error * dt  # Reverse integration

        # Update state
        self.last_error = error
        self.last_time = current_time

        return output

    def reset(self):
        """Reset controller state"""
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
        self.logger.info("PID controller reset")

    def set_gains(self, kp: float, ki: float, kd: float):
        """Update PID gains"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.logger.info(f"PID gains updated: Kp={kp}, Ki={ki}, Kd={kd}")
