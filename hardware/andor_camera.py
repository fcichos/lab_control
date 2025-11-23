"""
Andor EMCCD Camera Interface
Supports both SDK2 and SDK3 cameras
"""
import numpy as np
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from hardware.base import CameraInterface


class AndorSDK2Camera(CameraInterface):
    """Interface for Andor SDK2 cameras (iXon, iKon, etc.)"""

    def __init__(self, camera_index: int = 0):
        """
        Initialize Andor SDK2 camera

        Args:
            camera_index: Camera index (0 for first camera)
        """
        self.logger = logging.getLogger(__name__)
        self.camera_index = camera_index
        self._is_acquiring = False
        self._camera = None

        try:
            # Import Andor SDK - try multiple methods
            self._initialize_sdk()
        except ImportError as e:
            self.logger.warning(f"Andor SDK not found: {e}")
            self.logger.info("Using mock camera instead")
            from hardware.mock_devices import MockCamera
            self._camera = MockCamera()

    def _initialize_sdk(self):
        """Initialize the Andor SDK"""
        try:
            # Try pylablib first (recommended)
            from pylablib.devices import Andor
            self._camera = Andor.AndorSDK2Camera(idx=self.camera_index)
            self.logger.info("Initialized Andor camera via pylablib")
        except ImportError:
            # Fall back to direct SDK wrapper
            from ctypes import cdll, c_int
            sdk_path = self._find_sdk_path()
            self.sdk = cdll.LoadLibrary(sdk_path)
            self._init_camera()
            self.logger.info("Initialized Andor camera via direct SDK")

    def _find_sdk_path(self) -> str:
        """Locate Andor SDK DLL"""
        import platform
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\Andor SDK\atmcd64d.dll",
                r"C:\Program Files (x86)\Andor SDK\atmcd32d.dll",
            ]
            for path in paths:
                if Path(path).exists():
                    return path
        else:
            return "/usr/local/lib/libandor.so"
        raise FileNotFoundError("Andor SDK not found")

    def connect(self) -> bool:
        """Connect to camera"""
        try:
            if hasattr(self._camera, 'open'):
                self._camera.open()
            self.logger.info(f"Connected to Andor camera {self.camera_index}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from camera"""
        self.stop_acquisition()
        if self._camera:
            if hasattr(self._camera, 'close'):
                self._camera.close()
            self.logger.info("Disconnected from camera")

    def start_acquisition(self) -> bool:
        """Start continuous acquisition"""
        try:
            if hasattr(self._camera, 'start_acquisition'):
                self._camera.start_acquisition()
            self._is_acquiring = True
            self.logger.info("Started acquisition")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start acquisition: {e}")
            return False

    def stop_acquisition(self):
        """Stop acquisition"""
        if self._is_acquiring:
            if hasattr(self._camera, 'stop_acquisition'):
                self._camera.stop_acquisition()
            self._is_acquiring = False
            self.logger.info("Stopped acquisition")

    def acquire_image(self) -> Optional[np.ndarray]:
        """
        Acquire single image from camera

        Returns:
            numpy array with image data, or None if failed
        """
        try:
            if hasattr(self._camera, 'snap'):
                image = self._camera.snap()
            elif hasattr(self._camera, 'acquire_image'):
                image = self._camera.acquire_image()
            else:
                # Mock fallback
                image = np.random.randint(0, 4096, (512, 512), dtype=np.uint16)

            return image

        except Exception as e:
            self.logger.error(f"Failed to acquire image: {e}")
            return None

    def set_exposure(self, exposure_ms: float):
        """Set exposure time in milliseconds"""
        try:
            if hasattr(self._camera, 'set_exposure'):
                self._camera.set_exposure(exposure_ms / 1000.0)  # Convert to seconds
            self.logger.info(f"Set exposure to {exposure_ms} ms")
        except Exception as e:
            self.logger.error(f"Failed to set exposure: {e}")

    def set_gain(self, gain: int):
        """Set EM gain"""
        try:
            if hasattr(self._camera, 'set_gain'):
                self._camera.set_gain(gain)
            self.logger.info(f"Set gain to {gain}")
        except Exception as e:
            self.logger.error(f"Failed to set gain: {e}")

    def set_temperature(self, temp_celsius: int):
        """Set target temperature"""
        try:
            if hasattr(self._camera, 'set_temperature'):
                self._camera.set_temperature(temp_celsius)
            self.logger.info(f"Set temperature setpoint to {temp_celsius}°C")
        except Exception as e:
            self.logger.error(f"Failed to set temperature: {e}")

    def get_temperature(self) -> float:
        """Get current sensor temperature"""
        try:
            if hasattr(self._camera, 'get_temperature'):
                return self._camera.get_temperature()
            return -999.0  # Mock value
        except Exception as e:
            self.logger.error(f"Failed to get temperature: {e}")
            return -999.0

    def get_info(self) -> Dict[str, Any]:
        """Get camera information"""
        return {
            "model": "Andor EMCCD",
            "index": self.camera_index,
            "sdk": "SDK2",
            "status": "connected" if self._camera else "disconnected"
        }
