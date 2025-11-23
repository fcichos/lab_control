"""
Real-Time Feedback Control System
Connects image analysis to laser control
"""
import numpy as np
import logging
import time
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from threading import Thread, Event

from control.pid_controller import PIDController


@dataclass
class ControlSetpoint:
    """Target setpoint for control"""
    target_value: float
    tolerance: float
    parameter_name: str


class FeedbackLoop:
    """
    Real-time feedback loop connecting camera, processing, and control
    """

    def __init__(self, camera, processor, controller, control_board,
                 loop_rate_hz: float = 10.0):
        """
        Initialize feedback loop

        Args:
            camera: Camera interface instance
            processor: Processing pipeline instance
            controller: PID or other controller instance
            control_board: AdWin board interface
            loop_rate_hz: Control loop frequency in Hz
        """
        self.logger = logging.getLogger(__name__)
        self.camera = camera
        self.processor = processor
        self.controller = controller
        self.control_board = control_board

        self.loop_rate_hz = loop_rate_hz
        self.loop_period = 1.0 / loop_rate_hz

        self._running = False
        self._thread: Optional[Thread] = None
        self._stop_event = Event()

        self.setpoint: Optional[ControlSetpoint] = None
        self.last_error: float = 0.0
        self.last_control_output: float = 0.0

        # Statistics
        self.loop_count = 0
        self.error_history: List[float] = []
        self.output_history: List[float] = []

    def set_setpoint(self, setpoint: ControlSetpoint):
        """Set control target"""
        self.setpoint = setpoint
        self.logger.info(f"Setpoint: {setpoint.parameter_name} = "
                        f"{setpoint.target_value} ± {setpoint.tolerance}")

    def start(self):
        """Start feedback loop in background thread"""
        if self._running:
            self.logger.warning("Feedback loop already running")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = Thread(target=self._control_loop, daemon=True)
        self._thread.start()
        self.logger.info("Started feedback loop")

    def stop(self):
        """Stop feedback loop"""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.logger.info("Stopped feedback loop")

    def _control_loop(self):
        """Main control loop (runs in background thread)"""
        self.logger.info(f"Control loop running at {self.loop_rate_hz} Hz")

        while self._running and not self._stop_event.is_set():
            loop_start = time.time()

            try:
                # Step 1: Acquire image from camera
                image = self.camera.acquire_image()
                if image is None:
                    self.logger.warning("Failed to acquire image")
                    continue

                # Step 2: Process image and extract features
                result = self.processor.process(image)

                # Step 3: Calculate error from setpoint
                if self.setpoint is None:
                    self.logger.warning("No setpoint defined")
                    continue

                measured_value = result.features.get(
                    self.setpoint.parameter_name, 0.0
                )
                error = self.setpoint.target_value - measured_value
                self.last_error = error

                # Step 4: Calculate control output
                control_output = self.controller.update(error)
                self.last_control_output = control_output

                # Step 5: Apply control via AdWin board
                self.control_board.set_laser_power(control_output)

                # Update statistics
                self.loop_count += 1
                self.error_history.append(error)
                self.output_history.append(control_output)

                # Keep only last 1000 samples
                if len(self.error_history) > 1000:
                    self.error_history.pop(0)
                    self.output_history.pop(0)

                # Log every 10 loops
                if self.loop_count % 10 == 0:
                    self.logger.debug(
                        f"Loop {self.loop_count}: "
                        f"measured={measured_value:.3f}, "
                        f"error={error:.3f}, "
                        f"output={control_output:.3f}"
                    )

            except Exception as e:
                self.logger.error(f"Control loop error: {e}", exc_info=True)

            # Maintain loop rate
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.loop_period - elapsed)
            if sleep_time > 0:
                self._stop_event.wait(timeout=sleep_time)

    def get_statistics(self) -> Dict[str, Any]:
        """Get control loop statistics"""
        return {
            "loop_count": self.loop_count,
            "last_error": self.last_error,
            "last_output": self.last_control_output,
            "rms_error": np.sqrt(np.mean(np.array(self.error_history)**2)) 
                         if self.error_history else 0.0,
            "mean_output": np.mean(self.output_history) 
                          if self.output_history else 0.0
        }
