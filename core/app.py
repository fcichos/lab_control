"""
Main Application Controller
Coordinates all subsystems
"""

import logging
import time
from typing import Any, Dict, Optional

import numpy as np

from control.feedback_loop import ControlSetpoint, FeedbackLoop
from control.pid_controller import PIDController
from hardware.adwin_board import AdWinGoldIII
from hardware.andor_camera import AndorSDK2Camera
from hardware.mock_devices import MockAdWin, MockCamera
from processing.pipeline import (
    ProcessingPipeline,
    background_subtraction,
    find_centroids,
    gaussian_filter,
)


class LabControlApplication:
    """Main application controller"""

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.config = config

        # Hardware instances
        self.camera: Optional[AndorSDK2Camera] = None
        self.adwin: Optional[AdWinGoldIII] = None

        # Processing and control
        self.pipeline: Optional[ProcessingPipeline] = None
        self.feedback_loop: Optional[FeedbackLoop] = None
        self.pid_controller: Optional[PIDController] = None

        # State
        self.latest_image: Optional[np.ndarray] = None
        self.latest_features: Dict[str, float] = {}

        self._initialize()

    def _initialize(self):
        """Initialize subsystems"""
        self.logger.info("Initializing application subsystems")

        # Initialize processing pipeline
        use_gpu = self.config.get("processing", {}).get("use_gpu", True)
        self.pipeline = ProcessingPipeline(use_gpu=use_gpu)

        # Add processors based on config
        pipeline_steps = self.config.get("processing", {}).get("pipeline", [])
        if "background_subtraction" in pipeline_steps:
            self.pipeline.add_processor(background_subtraction)
        if "gaussian_filter" in pipeline_steps:
            self.pipeline.add_processor(gaussian_filter)
        if "centroid_detection" in pipeline_steps:
            self.pipeline.add_processor(find_centroids)

    # Camera methods

    def connect_camera(self) -> bool:
        """Connect to camera"""
        try:
            cam_config = self.config.get("camera", {})
            camera_index = cam_config.get("index", 0)

            self.camera = AndorSDK2Camera(camera_index=camera_index)
            success = self.camera.connect()

            if success:
                # Apply default settings
                exposure = cam_config.get("default_exposure", 100)
                gain = cam_config.get("default_gain", 1)
                temp = cam_config.get("target_temperature", -70)

                self.camera.set_exposure(exposure)
                self.camera.set_gain(gain)
                self.camera.set_temperature(temp)

                self.logger.info("Camera connected and configured")

            return success
        except Exception as e:
            self.logger.error(f"Failed to connect camera: {e}")
            return False

    def disconnect_camera(self):
        """Disconnect camera"""
        if self.camera:
            self.camera.disconnect()
            self.camera = None

    def start_acquisition(self) -> bool:
        """Start camera acquisition"""
        if self.camera:
            return self.camera.start_acquisition()
        return False

    def stop_acquisition(self):
        """Stop camera acquisition"""
        if self.camera:
            self.camera.stop_acquisition()

    def set_exposure(self, exposure_ms: float):
        """Set camera exposure"""
        if self.camera:
            self.camera.set_exposure(exposure_ms)

    def set_gain(self, gain: int):
        """Set camera gain"""
        if self.camera:
            self.camera.set_gain(gain)

    def set_temperature(self, temp_celsius: int):
        """Set camera temperature"""
        if self.camera:
            self.camera.set_temperature(temp_celsius)

    def get_camera_temperature(self) -> float:
        """Get current camera temperature"""
        if self.camera:
            return self.camera.get_temperature()
        return -999.0

    def get_latest_image(self) -> Optional[np.ndarray]:
        """Get latest acquired image"""
        if self.camera:
            image = self.camera.acquire_image()
            if image is not None:
                self.latest_image = image
                # Process image
                if self.pipeline:
                    result = self.pipeline.process(image)
                    self.latest_features = result.features
            return self.latest_image
        return None

    # AdWin methods

    def connect_adwin(self) -> bool:
        """Connect to AdWin board"""
        try:
            adwin_config = self.config.get("adwin", {})
            device_number = adwin_config.get("device_number", 1)

            self.adwin = AdWinGoldIII(device_number=device_number)
            success = self.adwin.connect()

            if success:
                # Load process if specified
                process_file = adwin_config.get("process_file")
                print(process_file)
                if process_file:
                    ret = self.adwin.load_process(process_file)
                    self.adwin.start_process(9)  # Process 9 for 1-channel analog

                self.logger.info("AdWin connected")

            return success
        except Exception as e:
            self.logger.error(f"Failed to connect AdWin: {e}")
            return False

    def disconnect_adwin(self):
        """Disconnect AdWin"""
        if self.adwin:
            self.adwin.disconnect()
            self.adwin = None

    def read_adwin_buffer(self) -> Optional[np.ndarray]:
        """
        Read 16-channel packed data buffer from AdWin

        Returns:
            NumPy array of shape (n_steps, 16) or None if no data available
        """
        if not self.adwin:
            self.logger.error("AdWin not connected")
            return None

        try:
            # Get buffer size from DATA_181[3]
            buffer_size = self.adwin.get_long(180, 3)

            # Check write pointer DATA_180[1]
            wp = self.adwin.get_long(180, 1)
            # if wp > 0:
            #     # Read packed buffer
            #     data = self.adwin.read_packed_buffer(buffer_size)
            #     self.logger.debug(f"Got data: {data.shape}")
            #     return data

            return None

        except Exception as e:
            self.logger.error(f"Failed to read AdWin buffer: {e}")
            return None

    def set_laser_power(self, power_percent: float):
        """Set laser power"""
        if self.adwin:
            self.adwin.set_laser_power(power_percent)

    # Feedback control methods

    def start_feedback_loop(self, kp: float, ki: float, kd: float, setpoint: float):
        """Start feedback control loop"""
        if not self.camera or not self.adwin or not self.pipeline:
            self.logger.error("Cannot start feedback: hardware not connected")
            return False

        try:
            # Create PID controller
            control_config = self.config.get("control", {})
            output_limits = tuple(control_config.get("output_limits", [0, 100]))

            self.pid_controller = PIDController(kp, ki, kd, output_limits=output_limits)

            # Create feedback loop
            loop_rate = control_config.get("loop_rate_hz", 10.0)
            self.feedback_loop = FeedbackLoop(
                self.camera,
                self.pipeline,
                self.pid_controller,
                self.adwin,
                loop_rate_hz=loop_rate,
            )

            # Set setpoint (assuming we're controlling centroid_x)
            control_setpoint = ControlSetpoint(
                target_value=setpoint, tolerance=5.0, parameter_name="centroid_x"
            )
            self.feedback_loop.set_setpoint(control_setpoint)

            # Start loop
            self.feedback_loop.start()
            self.logger.info("Feedback loop started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start feedback loop: {e}")
            return False

    def stop_feedback_loop(self):
        """Stop feedback control loop"""
        if self.feedback_loop:
            self.feedback_loop.stop()
            self.feedback_loop = None

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback loop statistics"""
        if self.feedback_loop:
            return self.feedback_loop.get_statistics()
        return {}

    def shutdown(self):
        """Shutdown application"""
        self.logger.info("Shutting down application")

        if self.feedback_loop:
            self.stop_feedback_loop()

        if self.camera:
            self.disconnect_camera()

        if self.adwin:
            self.disconnect_adwin()
