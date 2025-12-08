# python_serial_recorder

This is the README of the python_serial_recorder-program to capture data from a com-port.
Included is an Arduino script for a esp32 to send data from a number of ports, to be specified in a list in the file `ADC_ttgo-t-display.ino`.

# Prereq

The code is build in vs code, and the guide to running the program is written here below

## Package-manager installation guides for windows and macos
Use the following guides to install a package manager if you do not already have one installed.

- for Windows : https://chocolatey.org/install
- for MacOS : https://brew.sh/

## git
- Install Git on your system. This is a smart way to download other peoples projects, and keep control of what your system does.
   - MacOS: `brew install git`
   - Windows: `choco install git`

- Git gui: https://desktop.github.com/download/



## Python 

This program works with Python 3.13.?. 
- I cannot garantee compatability with other python versions.

1. **Option 1**: Use package manager, to create virutal environments. Pick the package manager you have installed on your system. If you dont have it, you can install one from their respective websites.  
   - MacOS: `brew install uv`
   - Windows:   `choco install uv`
   

   **Alternative 2**: *Install python directly 1*... download and use the installer from http://www.python.org

   **Alternative 3**: *Install python directly 2*... (Right now I am focussing on 3.13.x versions. At some point I will upgrade to using 3.14+)
   - MacOS: `brew install python@3.13`
   - Windows:   `choco install python313`

    **Alternative 4**: *Install python directly 3*... Install using App Store (both MacOS and Windows)

## Installation

For MacOS and Windows.

1. Download git repository. You CANNOT install inside Onedrive as of August 2025.
   ```bash
   cd ~
   git clone https://github.com/Anvendt-Programmering/python_serial_recorder.git
   cd python_serial_recorder
   uv sync
   ```
      
2. **Option 1**:Install new python environment (will avoid problems in the future), write the following in the terminal: 
    ```bash   
     uv sync
    ```
   **Alternative 2-4**: Install in global environment (This is a horrible idea, but you do you):
    ```bash   
     pip install -r requirements.txt
    ```

- Note: there is a requirements file, that you may use. If you do not wish to use UV!

## Updating The Repository

In case of changes, the newest version of the repository can be updated using the following terminal text, from within the `python_serial_recorder` folder. 
- **Option 1**: If you are using uv (Personally I find this the fastest and easiest!)
```bash
      git pull
      uv sync
   ```
that's it. 
- **Alternative 2-4**: Look it up online for your particular system and choise.


# Run
* The Python script is running the following code in the terminal, while inside the main python_serial_recorder folder: `uv run main.py`

* While the the python environment you wish to use is active (There are a ton of guides online for this): `python main.py`



