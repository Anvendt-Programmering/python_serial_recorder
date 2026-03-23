#!.venv/bin/python

# Et godt spørgsmål
"""
Python Serial Recorder

This program is a graphical user interface (GUI) application that allows users to view and record data from a serial port in real-time.
It follows the Model-View-Controller (MVC) design pattern to separate concerns and improve maintainability.

- Model: Handles the data and serial communication using pyserial.
- View: Manages the graphical user interface using pyside6 and Matplotlib.
- Controller: Coordinates between the Model and View, handling user interactions and updating the view with new data.

Features:
- Automatically detects available COM ports.
- Allows users to select a COM port, baud rate, and number of samples per channel.
- Displays real-time data from the serial port in a graph.
- Allows users to freeze/unfreeze the data display.
- Provides options to save the data as CSV, Excel, or JSON files.

Author: Martin Siemienski Andersen, Aalborg University, Aalborg, Denmark
Copyright (c) 2024 A Curious Clincal Programmer
"""
import logging
from pathlib import Path
from PySide6 import QtWidgets
from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtGui import QKeyEvent, QKeySequence, QShortcut
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import serial
import threading
import time
import pandas as pd
import serial.tools.list_ports as list_ports

from setup_scripts import setup_functions as my_setup
from setup_scripts.helper_functions import TextHandler, save_timeseries, calculate_2D_matrix, process_serial_data

my_setup.verify_python_version()
my_setup.initialize_logging()
my_setup.setup_theme()

def main() -> None:
    """Main function to set up the GUI and start the application."""
    app = QtWidgets.QApplication([])
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Serial Data Viewer")
    main_window.resize(1000, 800)
    model = Model()
    view = View(master=main_window)
    controller = Controller(model, view, update_rate_ms=100)
    view.set_controller(controller=controller)
    main_window.setCentralWidget(view)
    main_window.setFocusPolicy(
        Qt.FocusPolicy.StrongFocus
    )  # Ensures widget captures all key events
    main_window.setFocus()  # Forces focus onto the widget
    main_window.show()
    app.exec()


class Controller:
    """Controller class to manage interactions between the Model and View."""

    def __init__(self, model: "Model", view: "View", update_rate_ms: int = 100) -> None:
        self.model, self.view, self.is_frozen = model, view, False
        self.waiting_for_port_selection(dt_ms=update_rate_ms)

    def waiting_for_port_selection(self, dt_ms=100) -> None:
        """Update available ports until a connection is made."""
        if self.model.is_connected:
            QTimer.singleShot(dt_ms, self.update_graph)
            return
        self.update_available_ports()
        QTimer.singleShot(dt_ms, self.waiting_for_port_selection)

    def update_available_ports(self, dt_ms=100):
        """Get the list of available COM ports and update the view."""
        available_ports = self.model.get_available_ports()
        QTimer.singleShot(
            dt_ms,
            lambda available_ports=available_ports: self.view.update_ports(
                available_ports
            ),
        )

    def open_connection(
        self, port: str, baudrate: int, samples_per_channel: int
    ) -> None:
        """Open a serial connection and update the UI elements."""
        self.model.open_connection(port, baudrate, samples_per_channel)
        self.SAMPLES_PER_CHANNEL = samples_per_channel
        self.view.update_ui_elements()

    def update_graph(self, dt_ms=1000 * 1 / 50) -> None:
        """Create a thread to periodically update data if new data is available."""
        dt_ms = int(dt_ms)

        def graph_updating_thread():
            if self.model.is_disconnected:
                return

            if self.view.isVisible():
                df = self.model.get_snapshot(is_frozen=self.is_frozen)
                if df is not None and not df.empty:
                    self.view.display_data(df)

            QTimer.singleShot(dt_ms, graph_updating_thread)

        QTimer.singleShot(dt_ms, graph_updating_thread)

    def snapshot_show(self):
        """Toggle freezing and unfreezing of the data display."""
        self.is_frozen = not self.is_frozen

        if self.is_frozen:
            self.model.update_snapshot()

    def save_snapshot(self):
        """Save the current snapshot to a file."""
        def save_fcn(df):
            filters = (
                    "Excel files (*.xlsx);;"
                    "CSV files (*.csv);;"
                    "JSON files (*.json);;"
                    "All files (*.*)"
                )
            file_path, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
                    None,
                    "Save Timeseries",
                    "",
                    filters,
                )
            if not file_path:
                return  # User cancelled
            path = Path(file_path)
            save_timeseries(path, df, selected_filter)

            

        if self.is_running:
            self.snapshot_show()
            QTimer.singleShot(0, self.save_snapshot)
            return

        df = self.model.get_snapshot(is_frozen=self.is_frozen)
        if df.empty:
            self.snapshot_show()
            logging.error("Nothing to save, unfreezing.")
            logging.warning("Attempted to save an empty snapshot.")
            return
        QTimer.singleShot(1, lambda: save_fcn(df))

    @property
    def is_running(self):
        """Check if the data display is running."""
        return not self.is_frozen


class View(QtWidgets.QWidget):
    """View class to manage the graphical user interface."""

    lines: list[Line2D] = []

    def __init__(self, master: QtWidgets.QMainWindow) -> None:
        super().__init__(master)
        self.master = master
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setup_ui()

    def on_key_press(self, event: QKeyEvent):
        """Handle key press events."""

        match event.key():
            case Qt.Key.Key_Space:
                # pause / resume
                self.controller.snapshot_show()

            case Qt.Key.Key_S:
                # Save current snapshot (or freeze then save)
                self.controller.save_snapshot()

    def set_controller(self, controller: "Controller"):
        """Set the controller for the view."""
        self.controller = controller

    def setup_ui(self):
        """Set up the UI elements."""

        control_layout = QtWidgets.QHBoxLayout()
        main_layout = self.layout()
        assert isinstance(main_layout, QtWidgets.QVBoxLayout)
        main_layout.addLayout(control_layout)

        selection_layout = QtWidgets.QVBoxLayout()
        control_layout.addLayout(selection_layout)

        keybindings_layout = QtWidgets.QVBoxLayout()
        control_layout.addLayout(keybindings_layout)

        keybindings_layout.addWidget(
            QtWidgets.QLabel(
                "Key Bindings:\n\t[Space]: Freeze / Unfreeze\n\t[S]: Save data to file"
            )
        )

        lbl = QtWidgets.QLabel("Select COM Port:")
        selection_layout.addWidget(lbl)

        self.port = QtWidgets.QComboBox()
        selection_layout.addWidget(self.port)

        lbl = QtWidgets.QLabel("Select Baudrate:")
        selection_layout.addWidget(lbl)

        BAUDRATE_OPTIONS = [9600, 115200, 256000, 512000, 921600]
        self.baudrate = QtWidgets.QComboBox()
        self.baudrate.addItems(list(map(str, BAUDRATE_OPTIONS)))
        self.baudrate.setCurrentText(str(BAUDRATE_OPTIONS[-1]))
        selection_layout.addWidget(self.baudrate)

        lbl = QtWidgets.QLabel("Select Number of samples (per channel):")
        selection_layout.addWidget(lbl)

        self.samples_per_channel = QtWidgets.QSpinBox(
            minimum=10, maximum=100000, singleStep=100, value=2000
        )
        selection_layout.addWidget(self.samples_per_channel)

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.on_connect)
        selection_layout.addWidget(self.connect_button)

        # Set Matplotlib theme based on the OS theme
        #

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Real-time ADC Data")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("ADC Output")
        self.ax.grid(True)
        self.canvas = FigureCanvas(self.fig)

        main_layout.addWidget(self.canvas)

        # logging area
        self.setup_logger()

    def display_data(self, data: pd.DataFrame):
        """Update the graph with new data."""
        COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        if len(self.lines) != len(data.columns):
            for line in self.lines:
                line.remove()
            self.lines.clear()
            for idx, channel in enumerate(data.columns):
                line = Line2D(
                    xdata=data.index,
                    ydata=data[channel],
                    label=channel,
                    color=COLORS[idx % len(COLORS)],
                )
                self.lines.append(line)
                self.ax.add_line(line)

            self.ax.legend(loc="upper left")
        else:
            for channel, line in zip(data.columns, self.lines):
                line.set_data(data.index, data[channel])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def on_connect(self):
        """Connect to the selected COM port and baudrate."""
        try:
            port = self.port.currentText()
            baudrate = int(self.baudrate.currentText())
            samples_per_channel = int(self.samples_per_channel.value())
            if not port:
                raise ValueError("Please select a COM port.")
            if baudrate <= 0:
                raise ValueError("Please select a valid baudrate.")
            self.controller.open_connection(
                port=port, baudrate=baudrate, samples_per_channel=samples_per_channel
            )
            logging.info(
                f"Connected to port {port} with baudrate {baudrate} and {samples_per_channel} samples per channel."
            )
        except Exception as e:
            logging.error(str(e))

    def update_ports(self, available_ports):
        """Update the available ports dropdown."""
        if set(available_ports) == set(
            self.port.itemText(i) for i in range(self.port.count())
        ):
            return
        selected_port = self.port.currentText()
        self.port.clear()
        self.port.addItems(available_ports)
        if selected_port in available_ports:
            self.port.setCurrentText(selected_port)
        elif available_ports:
            self.port.setCurrentText(available_ports[-1])
        else:
            self.port.setCurrentText("")

    def update_ui_elements(self):
        """Disable buttons and dropdowns, and activate keybindings."""

        # Create a QShortcut for the spacebar key press
        evt = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Space,
            Qt.KeyboardModifier.NoModifier,
        )
        space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self.master)
        space_shortcut.activated.connect(lambda evt=evt: self.on_key_press(evt))

        evt = QKeyEvent(
            QEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.NoModifier
        )
        s_shortcut = QShortcut(QKeySequence(Qt.Key.Key_S), self.master)
        s_shortcut.activated.connect(lambda evt=evt: self.on_key_press(evt))

        self.keyPressEvent = self.on_key_press
        self.port.setEnabled(False)
        self.baudrate.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.samples_per_channel.setEnabled(False)

    def setup_logger(self):
        """Set up the logging system to write to the QtWidgets.QTextEdit widget."""

        main_layout = self.layout()
        assert isinstance(main_layout, QtWidgets.QVBoxLayout)
        self.log_area = QtWidgets.QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        text_handler = text_handler = TextHandler(self.log_area)
        text_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

        logging.getLogger().addHandler(text_handler)

class Model:
    """Model class to handle data and serial communication."""

    __snapshot = pd.DataFrame()
    __buffer = pd.DataFrame()
    __df_update_lock = threading.Lock()
    serial_connection: serial.Serial | None = None
    read_thread: threading.Thread | None = None
    SAMPLES_PER_CHANNEL: int = 0

    def open_connection(
        self, port: str, baudrate: int, samples_per_channel: int
    ) -> None:
        """Open a serial connection and start reading in a separate thread."""
        if self.is_connected:
            raise serial.SerialException("Already connected to a serial port.")
        try:
            self.serial_connection = serial.Serial(port, baudrate)
            self.SAMPLES_PER_CHANNEL = samples_per_channel
            self.read_thread = threading.Thread(
                target=self.start_continuous_read_from_serial,
                name="SerialReader",
                daemon=True,
            )
            self.read_thread.start()
        except serial.SerialException as _:
            raise serial.SerialException("Could not open serial connection")

    def start_continuous_read_from_serial(
        self, updaterate_sec: float = 1.0 / 50.0, failure_duration: float = 3.0
    ):
        """Continuously read data from the serial port in a background thread."""
        rest, counter = "", 0
        if self.serial_connection and self.is_connected:
            self.serial_connection.flush()
            self.serial_connection.read()

        t0 = time.time()
        ok = True
        while self.is_connected:
            try:
                available_bytes = self.get_available_bytes()

            except serial.SerialException as _:
                self.close_connection()
                logging.error(
                    "ESP32 disconnected! Restart the program, if you wish to continue!"
                )
                return

            if not available_bytes:  # If there are no available bytes to read
                if ok:
                    t0 = time.time()

                if time.time() - t0 > failure_duration:
                    self.close_connection()
                    return

                ok = False
                time.sleep(updaterate_sec)
                continue
            ok = True
            ascii_data = self.read_serial_data(available_bytes, rest)
            if ascii_data is None:
                rest = ""
            else:
                rest, data_integers = process_serial_data(ascii_data)
                if data_integers:
                    self.update_dataframe(data_integers, counter)
                    counter += len(data_integers)
            time.sleep(updaterate_sec)

    def get_available_bytes(self) -> int:
        """Get the number of available bytes in the serial connection."""
        if self.serial_connection:
            return self.serial_connection.in_waiting
        else:
            return 0

    def read_serial_data(self, available_bytes: int, rest: str) -> str | None:
        """Read data from the serial connection and decode it."""
        try:
            if self.serial_connection is None:
                return None
            bytes = self.serial_connection.read(available_bytes)
            return rest + bytes.decode()
        except UnicodeDecodeError:
            logging.warning("Read unknown non-character bytes.")
            return None

    def update_dataframe(self, data_integers: list[list[int]], counter: int) -> None:
        """Update the DataFrame with new data."""
        num_rows, num_channels = calculate_2D_matrix(data_integers)
        if num_rows == 0 or num_channels == 0:
            return
        column_names = [f"Ch{i}" for i in range(num_channels)]
        dfnew = pd.DataFrame(
            data_integers,
            index=range(counter, counter + num_rows),
            columns=column_names,
        )
        self.update_df(data=dfnew)

    def update_df(self, data: pd.DataFrame) -> None:
        """Update the buffer with new data."""
        with self.__df_update_lock:
            if self.__buffer.shape[1] != data.shape[1]:
                self.__buffer = pd.DataFrame(
                    [[0] * data.shape[1]] * self.SAMPLES_PER_CHANNEL,
                    columns=data.columns,
                    index=range(-self.SAMPLES_PER_CHANNEL, 0),
                    dtype=int,
                )
            self.__buffer = pd.concat([self.__buffer, data], ignore_index=False)
            if len(self.__buffer) > self.SAMPLES_PER_CHANNEL:
                self.__buffer = self.__buffer.iloc[-self.SAMPLES_PER_CHANNEL :]

    def close_connection(self) -> None:
        """Close the serial connection."""
        if self.is_connected and self.serial_connection:
            self.serial_connection.close()

    def get_available_ports(self) -> list[str]:
        """Get the list of available COM ports."""
        return sorted([port.device for port in list_ports.comports()])

    def update_snapshot(self) -> None:
        """Copy the current buffer into a snapshot."""
        with self.__df_update_lock:
            self.__snapshot = self.__buffer.copy()

    def get_snapshot(self, is_frozen: bool) -> pd.DataFrame:
        """Return a snapshot of the data or the buffer."""
        if self.is_disconnected:
            return self.__snapshot.copy()
        with self.__df_update_lock:
            return self.__snapshot.copy() if is_frozen else self.__buffer.copy()

    @property
    def is_connected(self) -> bool:
        """Check if the serial connection is established."""
        if self.serial_connection is None:
            return False
        if self.read_thread is None:
            return False

        b = self.serial_connection.is_open and self.read_thread.is_alive()
        return b

    @property
    def is_disconnected(self) -> bool:
        """Check if the serial connection is not established."""
        return not self.is_connected

    def __del__(self) -> None:
        """Destructor to close the serial connection."""
        self.close_connection()

if __name__ == "__main__":
    logging.info("Starting Serial Recorder...")
    main()
    logging.info("Exiting...")
