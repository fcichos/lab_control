"""
AdWin Gold III Real-Time Board Interface
Microsecond-precision laser control
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from hardware.base import ControlBoardInterface


class AdWinGoldIII(ControlBoardInterface):
    """Interface for AdWin Gold III real-time system"""

    def __init__(self, device_number: int = 1):
        """
        Initialize AdWin board

        Args:
            device_number: AdWin device number (usually 1)
        """
        self.logger = logging.getLogger(__name__)
        self.device_number = device_number
        self._adwin = None
        self._process_running = False

        try:
            import ADwin

            self._adwin = ADwin.ADwin(DeviceNo=device_number)
            self._adwin.Boot("/opt/adwin/share/btl/adwin12.btl")
            self.logger.info("AdWin module imported successfully")
        except ImportError:
            self.logger.warning("AdWin module not found, using mock device")
            from hardware.mock_devices import MockAdWin

            self._adwin = MockAdWin()

    def connect(self) -> bool:
        """Connect to AdWin device"""
        try:
            # Test connection by reading processor type
            proc_type = self._adwin.Processor_Type()
            self.logger.info(f"Connected to AdWin (Processor: {proc_type})")

            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to AdWin: {e}")
            return False

    def debug_adwin_methods(self):
        """Print all available methods on ADwin object for debugging"""
        if self._adwin:
            methods = [m for m in dir(self._adwin) if not m.startswith("_")]
            self.logger.info(f"Available ADwin methods: {methods}")
            print("Available ADwin methods:")
            for m in methods:
                print(f"  - {m}")
        else:
            self.logger.warning("ADwin object not initialized")

    def disconnect(self):
        """Disconnect from AdWin"""
        self.stop_process()
        self.logger.info("Disconnected from AdWin")

    def load_process(self, process_file: str) -> bool:
        """
        Load ADbasic or ADwinC compiled process

        Args:
            process_file: Path to .TB1 (ADbasic) or .TBC (ADwinC) file
        """
        try:
            if not Path(process_file).exists():
                raise FileNotFoundError(f"Process file not found: {process_file}")

            self._adwin.Load_Process(process_file)
            self._adwin.Set_Processdelay(9, 200000)
            self.logger.info(f"Loaded process: {process_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load process: {e}")
            return False

    def start_process(self, process_no: int = 9) -> bool:
        """Start real-time process on AdWin"""
        try:
            self._adwin.Start_Process(process_no)
            self._process_running = True
            self.logger.info(f"Started process {process_no}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start process: {e}")
            return False

    def stop_process(self, process_no: int = 1):
        """Stop real-time process"""
        try:
            if self._process_running:
                self._adwin.Stop_Process(process_no)
                self._process_running = False
                self.logger.info(f"Stopped process {process_no}")
        except Exception as e:
            self.logger.error(f"Failed to stop process: {e}")

    def set_parameter(self, param_no: int, value: float):
        """
        Set floating-point parameter

        Args:
            param_no: Parameter number (1-80)
            value: Parameter value
        """
        try:
            self._adwin.Set_FPar(param_no, value)
            self.logger.debug(f"Set FPar[{param_no}] = {value}")
        except Exception as e:
            self.logger.error(f"Failed to set parameter: {e}")

    def get_parameter(self, param_no: int) -> float:
        """Get floating-point parameter"""
        try:
            return self._adwin.Get_FPar(param_no)
        except Exception as e:
            self.logger.error(f"Failed to get parameter: {e}")
            return 0.0

    def set_laser_power(self, power_percent: float):
        """
        Set laser power via DAC output

        Args:
            power_percent: Laser power (0-100%)
        """
        # Assuming DAC range 0-10V for 0-100% power
        voltage = (power_percent / 100.0) * 10.0

        # Set via parameter (process reads this and sets DAC)
        self.set_parameter(1, voltage)
        self.logger.info(f"Set laser power to {power_percent}%")

    def set_control_signal(self, channel: int, value: float):
        """
        Set arbitrary control signal on specific channel

        Args:
            channel: Output channel (1-8 for Gold III)
            value: Voltage value (-10 to +10V typical)
        """
        try:
            # Use data array for multi-channel control
            data_array = np.array([value], dtype=np.float32)
            self._adwin.SetData_Float(channel, data_array, 1, 1)
            self.logger.debug(f"Set channel {channel} to {value}V")
        except Exception as e:
            self.logger.error(f"Failed to set control signal: {e}")

    def read_input(self, channel: int) -> float:
        """Read analog input channel"""
        try:
            # Read from data array populated by real-time process
            value = self._adwin.Get_FPar(10 + channel)
            return value
        except Exception as e:
            self.logger.error(f"Failed to read input: {e}")
            return 0.0

    def upload_array(self, array_no: int, data: np.ndarray):
        """
        Upload data array to AdWin

        Args:
            array_no: Data array number (1-200)
            data: NumPy array to upload
        """
        try:
            if data.dtype == np.float32 or data.dtype == np.float64:
                self._adwin.SetData_Float(
                    array_no, data.astype(np.float32), 1, len(data)
                )
            else:
                self._adwin.SetData_Long(array_no, data.astype(np.int32), 1, len(data))
            self.logger.info(f"Uploaded {len(data)} values to array {array_no}")
        except Exception as e:
            self.logger.error(f"Failed to upload array: {e}")

    def download_array(self, array_no: int, length: int) -> np.ndarray:
        """Download data array from AdWin"""
        try:
            data = np.zeros(length, dtype=np.float32)
            self._adwin.GetData_Float(array_no, data, 1, length)
            return data
        except Exception as e:
            self.logger.error(f"Failed to download array: {e}")
            return np.zeros(length)

    def get_status(self) -> Dict[str, Any]:
        """Get AdWin status information"""
        try:
            return {
                "processor": self._adwin.Processor_Type(),
                "process_running": self._process_running,
                "workload": self._adwin.Workload() if self._process_running else 0,
            }
        except:
            return {"processor": "Unknown", "process_running": False, "workload": 0}

    def get_long(self, data_no: int, index: int) -> int:
        """
        Get a LONG value from AdWin data array or parameter

        Args:
            data_no: Data array number (e.g., 181 for DATA_181)
            index: Array index (1-based)

        Returns:
            Long integer value
        """
        try:
            # Try Data_Get_Long method name (common ADwin Python API naming)
            # print(self._adwin.Data_Length(180))
            # print(self._adwin.Data_Length(181))
            # return 0
            result = self._adwin.GetData_Long(181, 1, 100)
            print(result[0])
            return 0
            # return result[0] if isinstance(result, (list, tuple)) else result
        except Exception as e:
            self.logger.error(f"Failed to get long DATA_{data_no}[{index}]: {e}")
            return 0
