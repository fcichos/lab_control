"""
Configuration Management
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            self.logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self._get_defaults()

        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {self.config_file}")
            return self.config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_defaults()

    def save(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            self.logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'camera': {
                'type': 'andor_sdk2',
                'index': 0,
                'default_exposure': 100,
                'default_gain': 1,
                'target_temperature': -70
            },
            'adwin': {
                'device_number': 1,
                'process_file': 'laser_control.TB1'
            },
            'processing': {
                'use_gpu': True,
                'pipeline': ['background_subtraction', 'gaussian_filter', 'centroid_detection']
            },
            'control': {
                'loop_rate_hz': 10,
                'pid': {'kp': 1.0, 'ki': 0.1, 'kd': 0.01},
                'output_limits': [0, 100]
            }
        }
