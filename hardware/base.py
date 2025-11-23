"""
Abstract Hardware Interfaces
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Dict, Any


class CameraInterface(ABC):
    """Abstract interface for cameras"""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to camera"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from camera"""
        pass

    @abstractmethod
    def start_acquisition(self) -> bool:
        """Start continuous acquisition"""
        pass

    @abstractmethod
    def stop_acquisition(self):
        """Stop acquisition"""
        pass

    @abstractmethod
    def acquire_image(self) -> Optional[np.ndarray]:
        """Acquire single image"""
        pass

    @abstractmethod
    def set_exposure(self, exposure_ms: float):
        """Set exposure time in milliseconds"""
        pass

    @abstractmethod
    def set_gain(self, gain: int):
        """Set camera gain"""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get camera information"""
        pass


class ControlBoardInterface(ABC):
    """Abstract interface for control boards"""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to control board"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from board"""
        pass

    @abstractmethod
    def set_parameter(self, param_no: int, value: float):
        """Set parameter value"""
        pass

    @abstractmethod
    def get_parameter(self, param_no: int) -> float:
        """Get parameter value"""
        pass

    @abstractmethod
    def upload_array(self, array_no: int, data: np.ndarray):
        """Upload data array"""
        pass

    @abstractmethod
    def download_array(self, array_no: int, length: int) -> np.ndarray:
        """Download data array"""
        pass
