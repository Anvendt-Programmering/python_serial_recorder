# python_serial_recorder

This file explains how to use the python_serial_recorder-program to capture data from a com-port.
Included is an Arduino script for a esp32 to send data from a number of ports, to be specified in a list in the file `ADC_ttgo-t-display.ino`.

# Prereq

The code is build in vs code, and the guide to running the program is written here below

## Package-manager installation guides for windows and macos
Use the following guides to install a package manager if you do not already have one installed.

- for Windows : https://chocolatey.org/install
- for MacOS : https://brew.sh/

## git
- Install Git on your system. This is a way to download other peoples projects.
   - MacOS: `brew install git`
   - Windows: `choco install git`

- Git gui: https://desktop.github.com/download/



## Python 

This program works with Python 3.13.2. 
- I cannot garantee compatability with other python versions.

1. Option 1: download and use the installer from www.python.org
2. Option 3: Use package manager. Pick the package manager you have installed on your system. If you dont have it, you can install one from their respective websites.  
   - MacOS: `brew install uv`
   - Windows:   `choco install uv`

## how to install python packages via pip

If you do not know how to install new python packages using pip, I suggest reading the following page: https://packaging.python.org/en/latest/tutorials/installing-packages/




## Installation

For MacOS and Windows.

1. download git repository
   ```bash
   git clone https://github.com/Anvendt-Programmering/python_serial_recorder.git
   cd python_serial_recorder
   ```
      
2. Install new python environment (will avoid problems in the future), write the following in the terminal: 
   
   ```bash   
   uv sync
   ```
    
4. activate python environment
   - Depending on if it is not already activated when you open a terminal in VS Code, you can do the following.
     - MacOS

     ```bash
        source .venv/bin/activate  
     ```
     - Windows

     ```bash
        source .venv/Scripts/activate  
     ```

- Note: there is also a requirements file, that you might use. if you do not wish to use UV!

## Updating The Repository

- In case of changes, the newest version of the repository can be updated using the following terminal text, from within the `python_serial_recorder` folder
```bash
      git pull
      uv sync
   ```
that's it.


# Run
The Python script is running the following code in the terminal, while inside the main python_serial_recorder folder.

```bash
uv run main.py
```

or

```bash
python main.py
```



