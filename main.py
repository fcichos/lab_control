"""
Lab Control Software - Main Entry Point
Modular camera control, processing, and real-time feedback system
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.app import LabControlApplication
from core.config_manager import ConfigManager
from gui.main_window import MainWindow


def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('lab_control.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Lab Control Software")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Lab Control Software")
    app.setOrganizationName("Research Lab")

    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load()

        # Initialize application controller
        lab_app = LabControlApplication(config)

        # Create and show main window
        main_window = MainWindow(lab_app)
        main_window.show()

        logger.info("Application started successfully")
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
