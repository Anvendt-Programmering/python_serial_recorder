import logging
import re
import pandas as pd
from pathlib import Path
from PySide6 import QtWidgets

 # Create a custom logging handler
class TextHandler(logging.Handler):
    def __init__(self, widget: QtWidgets.QTextEdit):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        if not self.widget.isVisible():
            return
        log_entry = self.format(record)
        self.widget.append(log_entry)
        self.widget.verticalScrollBar().setValue(
            self.widget.verticalScrollBar().maximum()
        )

    # Destructor, remember to remove self from the logger
    def __del__(self):
        logging.getLogger().removeHandler(self)

def process_serial_data(ascii_data: str) -> tuple[str, list[list[int]]]:
    """Process the ASCII data read from the serial connection."""
    row_asci_data = ascii_data.split("\r\n")
    if len(row_asci_data) < 3:
        # Requires at least 3 ready samples, to process. otherwise return all samples as rest
        return ascii_data, []

    rest = row_asci_data[-1]  # Last row is rest
    data = row_asci_data[:-2]
    data_filtered = filter(__str_contains_only_numbers, data)
    data_integers = list(map(__str_to_intarray, data_filtered))
    return rest, data_integers



def calculate_2D_matrix(data: list[list[int]]) -> tuple[int, int]:
    """Calculate the number of rows and columns in a 2D matrix."""
    num_rows = len(data)
    num_cols = len(data[0]) if num_rows else 0
    return num_rows, num_cols


def save_timeseries(path:Path, df: pd.DataFrame, selected_filter: str):
    
    # Extract extension from selected filter, e.g. "*.xlsx" -> ".xlsx"
    if selected_filter:
        ext = selected_filter.split("(")[1].split(")")[0].replace("*", "").strip()
    else:
        ext = path.suffix

    # Ensure the file has an extension
    if not path.suffix and ext:
        path = path.with_suffix(ext)

    ext = path.suffix.lower()

    # Map extensions to writers
    writers = {
        ".csv": lambda p: df.to_csv(p, index=True, index_label="index"),
        ".xlsx": lambda p: df.to_excel(p, index=True, index_label="index"),
        ".json": lambda p: df.reset_index()
        .rename(columns={"index": "index"})
        .to_json(p, orient="records", lines=True),
    }

    writer = writers.get(ext)
    if not writer:
        logging.error(f"Unsupported file extension: {ext}")
        return

    writer(path)
    logging.info(f"Data saved to {path}")

    


def __str_contains_only_numbers(row: str) -> bool:
    """Check if a string contains only numbers and spaces."""
    if not row:
        return False
    return bool(re.fullmatch(r"\s*\d+( \d+)*\s*", row))


def __str_to_intarray(data: str) -> list[int]:
    """Convert a string of numbers separated by spaces to a list of integers."""
    return list(map(int, data.split()))