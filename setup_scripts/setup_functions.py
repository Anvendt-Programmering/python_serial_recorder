def initialize_logging():
    """Setup logging, so it will both save to a file"""
    import logging
    import time
    from pathlib import Path
    # Setup Logging
    filename = Path("logs")/ f"log-{time.strftime("%Y-%m-%d", time.localtime())}.log"
    Path(f"logs").mkdir(exist_ok=True)
    logging_format = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    logging.basicConfig(level=logging.INFO,
        format=logging_format,
        filename=Path("logs")/ f"log-{time.strftime("%Y-%m-%d", time.localtime())}.log"    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            logging_format
        )
    )
    logging.getLogger().addHandler(console_handler)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    return filename

def verify_python_version():
    """Verify that the python version is correct, otherwise warn user"""
    import logging
    import sys
    # Ensure suggested python version
    try:
        with open(".python-version", "r") as f:
            version_str = f.read().strip()
            SUGGESTED_PY_VERSION = tuple(map(int, version_str.split(".")))
    except FileNotFoundError as e:
        logging.error(f"Could not find .python-version file. Using default version (3.14.2). Error: {e}")
        SUGGESTED_PY_VERSION = (3, 14, 2)
    if (sys.version_info.major, sys.version_info.minor, sys.version_info.micro) != SUGGESTED_PY_VERSION:
        logging.warning(
            f"This script is designed for Python {SUGGESTED_PY_VERSION[0]}.{SUGGESTED_PY_VERSION[1]}.{SUGGESTED_PY_VERSION[2]}"
            f" (current: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}) might cause unexpected behavior or errors."
            f" If errors occur, run 'uv sync', or update to the suggested python version."
        )

def setup_theme():
    """Set theme of UI to either dark or light"""
    import darkdetect
    import matplotlib.pyplot as plt
    if darkdetect.isDark():
        plt.style.use(
            "https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle"
        )
    else:
        plt.style.use("ggplot")

if __name__ == "__main__":
    import logging
    import os
    filename = initialize_logging()
    setup_theme()
    verify_python_version()
    logging.info("Does this work?")
