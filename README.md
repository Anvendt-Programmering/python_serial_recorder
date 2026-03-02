# python_serial_recorder

This is the README of the python_serial_recorder-program to capture data from a com-port.
Included is an Arduino script for a esp32 to send data from a number of ports, to be specified in a list in the file `ADC_ttgo-t-display.ino`.


# Installation
1. Download git repository

   ```bash
   cd ~
   git clone https://github.com/Anvendt-Programmering/python_serial_recorder.git
   cd python_serial_recorder
   ```


2. Install Required Packages

If UV is installed on your system:
   ```bash
   uv run main.py`
   ```
If you have Conda on your ystem:
   ```bash
   conda create -n python-serial-recorder python=3.14.2 -y
   conda activate python-serial-recorder
   pip install -r requirements.txt
   ```

# Run program

If UV is installed on your system:
   - `uv run main.py`


Otherwise: Ensure that your installed python interpreter is selected, could be `conda activate python-serial-recorder`. then:
```bash
python main.py
```

# Guides

Install the following elements:
- Package manager
- Git
- Python

## Package-manager installation guides for windows and macos

Use the following guides to install a package manager if you do not already have one installed.

- for Windows : winget (Er indbygget i Windows11)
- for MacOS : https://brew.sh/

## Install Git

While not strictly necessary, it is greatly advised to use git. Also besides classes.
   - MacOS: `brew install git`
   - Windows: `winget install --id Git.Git -e --source winget`

## Install Python version > 3.14
Install Python using the following guide: https://github.com/AAU-Python-Guides/install_python_guide


