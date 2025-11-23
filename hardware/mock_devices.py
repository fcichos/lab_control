"""
Mock Hardware Devices for Testing
"""
import numpy as np
import logging
from typing import Dict, Any

from hardware.base import CameraInterface, ControlBoardInterface


class MockCamera(CameraInterface):
    """Mock camera for testing without hardware"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.acquiring = False
        self.exposure = 100.0
        self.gain = 1
        self.temperature = -70.0
        self.frame_count = 0

    def connect(self) -> bool:
        self.connected = True
        self.logger.info("Mock camera connected")
        return True

    def disconnect(self):
        self.connected = False
        self.acquiring = False
        self.logger.info("Mock camera disconnected")

    def start_acquisition(self) -> bool:
        if not self.connected:
            return False
        self.acquiring = True
        self.logger.info("Mock camera acquisition started")
        return True

    def stop_acquisition(self):
        self.acquiring = False
        self.logger.info("Mock camera acquisition stopped")

    def acquire_image(self) -> np.ndarray:
        """Generate synthetic image with Gaussian spots"""
        self.frame_count += 1

        # Create image with noise
        image = np.random.poisson(100, (512, 512)).astype(np.uint16)

        # Add Gaussian spot that moves slightly
        y, x = np.ogrid[:512, :512]
        center_x = 256 + 50 * np.sin(self.frame_count * 0.1)
        center_y = 256 + 30 * np.cos(self.frame_count * 0.1)

        spot = np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * 20**2))
        image = image + (spot * 3000 * self.gain).astype(np.uint16)

        return np.clip(image, 0, 65535)

    def set_exposure(self, exposure_ms: float):
        self.exposure = exposure_ms
        self.logger.debug(f"Mock camera exposure set to {exposure_ms} ms")

    def set_gain(self, gain: int):
        self.gain = gain
        self.logger.debug(f"Mock camera gain set to {gain}")

    def set_temperature(self, temp_celsius: int):
        self.temperature = temp_celsius
        self.logger.debug(f"Mock camera temperature setpoint: {temp_celsius}°C")

    def get_temperature(self) -> float:
        # Simulate slow cooling
        return self.temperature + 5.0

    def get_info(self) -> Dict[str, Any]:
        return {
            "model": "Mock Camera",
            "index": 0,
            "status": "connected" if self.connected else "disconnected"
        }


class MockAdWin(ControlBoardInterface):
    """Mock AdWin board for testing"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.parameters = {}
        self.arrays = {}

    def connect(self) -> bool:
        self.connected = True
        self.logger.info("Mock AdWin connected")
        return True

    def disconnect(self):
        self.connected = False
        self.logger.info("Mock AdWin disconnected")

    def Processor_Type(self):
        return "T12 (Mock)"

    def Workload(self):
        return 15  # Mock 15% workload

    def Load_Process(self, filename: str):
        self.logger.info(f"Mock: Loaded process {filename}")

    def Start_Process(self, process_no: int):
        self.logger.info(f"Mock: Started process {process_no}")

    def Stop_Process(self, process_no: int):
        self.logger.info(f"Mock: Stopped process {process_no}")

    def set_parameter(self, param_no: int, value: float):
        self.parameters[param_no] = value
        self.logger.debug(f"Mock AdWin: FPar[{param_no}] = {value}")

    def get_parameter(self, param_no: int) -> float:
        return self.parameters.get(param_no, 0.0)

    def Set_FPar(self, param_no: int, value: float):
        self.set_parameter(param_no, value)

    def Get_FPar(self, param_no: int) -> float:
        return self.get_parameter(param_no)

    def upload_array(self, array_no: int, data: np.ndarray):
        self.arrays[array_no] = data.copy()
        self.logger.debug(f"Mock AdWin: Uploaded {len(data)} values to array {array_no}")

    def download_array(self, array_no: int, length: int) -> np.ndarray:
        if array_no in self.arrays:
            return self.arrays[array_no][:length]
        return np.zeros(length)

    def SetData_Float(self, array_no: int, data: np.ndarray, start: int, count: int):
        self.upload_array(array_no, data)

    def GetData_Float(self, array_no: int, data: np.ndarray, start: int, count: int):
        if array_no in self.arrays:
            data[:] = self.arrays[array_no][:count]

    def SetData_Long(self, array_no: int, data: np.ndarray, start: int, count: int):
        self.upload_array(array_no, data)
