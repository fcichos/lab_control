# Lab Control Software

Modular Python/PyQt6 software for controlling Andor EMCCD cameras, processing images with PyTorch, and real-time laser control via AdWin Gold III.

## Quick Start

### Installation with uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt

# Install Andor SDK separately from Oxford Instruments
# Install ADwin Python module from ADwin installation directory
```

### Installation with pip (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Software

```bash
python main.py
```

## Project Structure

```
lab_control/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config.yaml            # Configuration file
├── core/                  # Application core
│   ├── app.py            # Main controller
│   └── config_manager.py # Configuration management
├── hardware/              # Hardware interfaces
│   ├── base.py           # Abstract interfaces
│   ├── andor_camera.py   # Andor camera support
│   ├── adwin_board.py    # AdWin board interface
│   └── mock_devices.py   # Mock devices for testing
├── processing/            # Image processing
│   └── pipeline.py       # Processing pipeline with PyTorch
├── control/               # Feedback control
│   ├── pid_controller.py # PID controller
│   └── feedback_loop.py  # Real-time feedback system
└── gui/                   # PyQt6 GUI
    └── main_window.py    # Main window
```

## Features

- 🎥 **Andor Camera Control** - Full SDK2/SDK3 support
- ⚡ **GPU Acceleration** - PyTorch models for image processing
- 🎛️ **AdWin Integration** - Microsecond-precision control
- 🔄 **Closed-Loop Control** - PID-based feedback system
- 🧩 **Modular Design** - Easy to extend and customize
- 🧪 **Mock Devices** - Test without hardware

## Configuration

Edit `config.yaml` to configure:
- Camera settings (exposure, gain, temperature)
- AdWin parameters (device number, process file)
- Processing pipeline (GPU usage, algorithms)
- Control parameters (loop rate, PID gains)

## Development

The software uses mock devices when hardware is not available, allowing development and testing without physical equipment.

## Documentation

See the interactive canvas documentation for complete API reference and examples.

## Requirements

- Python 3.8+
- PyQt6
- PyTorch (with CUDA for GPU acceleration)
- NumPy, SciPy
- Andor SDK (from Oxford Instruments)
- ADwin Python module (from Jäger Messtechnik)

## License

This software is provided as-is for research and educational purposes.
