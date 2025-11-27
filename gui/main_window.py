"""
Main GUI Window - PyQt6 Interface
Simplified version - see canvas for full implementation
"""

import logging

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("Lab Control Software")
        self.setGeometry(100, 100, 1400, 900)

        self._setup_ui()
        self._setup_connections()
        self._setup_timers()

        self.logger.info("Main window initialized")

    def _setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel: Camera view
        left_panel = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("background-color: black;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.image_label)

        # Camera controls
        cam_ctrl = self._create_camera_controls()
        left_panel.addWidget(cam_ctrl)
        main_layout.addLayout(left_panel, stretch=2)

        # Right panel: Control
        right_panel = self._create_control_panel()
        main_layout.addWidget(right_panel, stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _create_camera_controls(self) -> QGroupBox:
        """Create camera control panel"""
        group = QGroupBox("Camera Controls")
        layout = QVBoxLayout()

        # Connection buttons
        conn_layout = QHBoxLayout()
        self.btn_connect_camera = QPushButton("Connect Camera")
        self.btn_start_acq = QPushButton("Start Acquisition")
        conn_layout.addWidget(self.btn_connect_camera)
        conn_layout.addWidget(self.btn_start_acq)
        layout.addLayout(conn_layout)

        # Exposure control
        exp_layout = QHBoxLayout()
        exp_layout.addWidget(QLabel("Exposure (ms):"))
        self.spin_exposure = QDoubleSpinBox()
        self.spin_exposure.setRange(0.1, 10000)
        self.spin_exposure.setValue(100)
        exp_layout.addWidget(self.spin_exposure)
        layout.addLayout(exp_layout)

        # Gain control
        gain_layout = QHBoxLayout()
        gain_layout.addWidget(QLabel("EM Gain:"))
        self.spin_gain = QSpinBox()
        self.spin_gain.setRange(0, 300)
        self.spin_gain.setValue(1)
        gain_layout.addWidget(self.spin_gain)
        layout.addLayout(gain_layout)

        group.setLayout(layout)
        return group

    def _create_control_panel(self) -> QWidget:
        """Create control panel"""
        widget = QGroupBox("Laser Control")
        layout = QVBoxLayout(widget)

        # AdWin connection
        self.btn_connect_adwin = QPushButton("Connect AdWin")
        layout.addWidget(self.btn_connect_adwin)

        # Laser power
        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Laser Power (%):"))
        self.spin_laser_power = QDoubleSpinBox()
        self.spin_laser_power.setRange(0, 100)
        self.spin_laser_power.setValue(0)
        power_layout.addWidget(self.spin_laser_power)
        self.btn_set_power = QPushButton("Set")
        power_layout.addWidget(self.btn_set_power)
        layout.addLayout(power_layout)

        # Read buffer button
        self.btn_read_buffer = QPushButton("Read Buffer")
        layout.addWidget(self.btn_read_buffer)

        # Feedback controls
        feedback_group = QGroupBox("Feedback Control")
        feedback_layout = QVBoxLayout()

        # PID gains
        pid_layout = QHBoxLayout()
        pid_layout.addWidget(QLabel("Kp:"))
        self.spin_kp = QDoubleSpinBox()
        self.spin_kp.setValue(1.0)
        pid_layout.addWidget(self.spin_kp)
        feedback_layout.addLayout(pid_layout)

        # Setpoint
        setpoint_layout = QHBoxLayout()
        setpoint_layout.addWidget(QLabel("Setpoint:"))
        self.spin_setpoint = QDoubleSpinBox()
        self.spin_setpoint.setRange(-1000, 1000)
        self.spin_setpoint.setValue(256)
        setpoint_layout.addWidget(self.spin_setpoint)
        feedback_layout.addLayout(setpoint_layout)

        # Start/Stop buttons
        ctrl_btn_layout = QHBoxLayout()
        self.btn_start_feedback = QPushButton("Start Feedback")
        self.btn_stop_feedback = QPushButton("Stop Feedback")
        ctrl_btn_layout.addWidget(self.btn_start_feedback)
        ctrl_btn_layout.addWidget(self.btn_stop_feedback)
        feedback_layout.addLayout(ctrl_btn_layout)

        feedback_group.setLayout(feedback_layout)
        layout.addWidget(feedback_group)
        layout.addStretch()

        return widget

    def _setup_connections(self):
        """Connect signals and slots"""
        self.btn_connect_camera.clicked.connect(self.on_connect_camera)
        self.btn_start_acq.clicked.connect(self.on_start_acquisition)
        self.spin_exposure.valueChanged.connect(self.on_exposure_changed)
        self.spin_gain.valueChanged.connect(self.on_gain_changed)

        self.btn_connect_adwin.clicked.connect(self.on_connect_adwin)
        self.btn_set_power.clicked.connect(self.on_set_laser_power)
        self.btn_read_buffer.clicked.connect(self.on_read_buffer)

        self.btn_start_feedback.clicked.connect(self.on_start_feedback)
        self.btn_stop_feedback.clicked.connect(self.on_stop_feedback)

    def _setup_timers(self):
        """Setup update timers"""
        self.image_timer = QTimer()
        self.image_timer.timeout.connect(self.update_image)

    def on_connect_camera(self):
        """Connect to camera"""
        if self.app.connect_camera():
            self.status_bar.showMessage("Camera connected", 3000)
        else:
            self.status_bar.showMessage("Failed to connect camera", 3000)

    def on_start_acquisition(self):
        """Start camera acquisition"""
        if self.app.start_acquisition():
            self.image_timer.start(100)  # 10 Hz
            self.status_bar.showMessage("Acquisition started", 3000)

    def on_exposure_changed(self, value):
        """Update camera exposure"""
        self.app.set_exposure(value)

    def on_gain_changed(self, value):
        """Update camera gain"""
        self.app.set_gain(value)

    def on_connect_adwin(self):
        """Connect to AdWin"""
        if self.app.connect_adwin():
            self.status_bar.showMessage("AdWin connected", 3000)

    def on_set_laser_power(self):
        """Set laser power"""
        power = self.spin_laser_power.value()
        self.app.set_laser_power(power)
        self.status_bar.showMessage(f"Laser power set to {power}%", 3000)

    def on_read_buffer(self):
        """Read AdWin 16-channel buffer"""
        data = self.app.read_adwin_buffer()
        if data is not None:
            self.status_bar.showMessage(f"Got buffer data: {data.shape}", 3000)
            self.logger.info(
                f"Buffer data shape: {data.shape}, min: {data.min()}, max: {data.max()}"
            )
        else:
            self.status_bar.showMessage("No buffer data available", 3000)

    def on_start_feedback(self):
        """Start feedback control"""
        kp = self.spin_kp.value()
        setpoint = self.spin_setpoint.value()
        self.app.start_feedback_loop(kp, 0.1, 0.01, setpoint)
        self.status_bar.showMessage("Feedback loop started", 3000)

    def on_stop_feedback(self):
        """Stop feedback control"""
        self.app.stop_feedback_loop()
        self.status_bar.showMessage("Feedback loop stopped", 3000)

    def update_image(self):
        """Update displayed image"""
        image = self.app.get_latest_image()
        if image is not None:
            self.display_image(image)

    def display_image(self, image: np.ndarray):
        """Display numpy array as image"""
        # Normalize to 8-bit
        img_normalized = (
            (image - image.min()) / (image.max() - image.min()) * 255
        ).astype(np.uint8)

        height, width = img_normalized.shape
        q_image = QImage(
            img_normalized.data, width, height, width, QImage.Format.Format_Grayscale8
        )

        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """Handle window close"""
        self.app.shutdown()
        event.accept()
