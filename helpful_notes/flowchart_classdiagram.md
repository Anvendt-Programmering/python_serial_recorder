## Connection and Update Flow

```mermaid
flowchart
    start((Start App))
    setup[Create Model, View, Controller]
    wait_loop[Controller.waiting_for_port_selection]
    scan_ports[Model.get_available_ports]
    detect_esp32{Any ESP32 ports found?}
    update_dropdown[View.update_ports with ESP32 ports]
    keep_waiting[Wait configured period before next port scan]

    connect_btn{Connect button pressed?}
    port_selected{Dropdown has selected ESP32 port?}
    open_conn[Controller.open_connection]
    model_open[Model.open_connection]
    conn_ok{Model is_connected?}
    lock_ui[View.update_ui_elements]
    start_graph_loop[Controller.update_graph]
    read_snapshot[Model.get_snapshot]
    render_view[View.display_data]
    stop([STOP])

    start --> setup --> wait_loop --> scan_ports --> detect_esp32
    detect_esp32 -->|Yes| update_dropdown --> keep_waiting --> wait_loop
    detect_esp32 -->|No| keep_waiting

    update_dropdown --> connect_btn
    connect_btn -->|No| wait_loop
    connect_btn -->|Yes| port_selected
    port_selected -->|No| wait_loop
    port_selected -->|Yes| open_conn --> model_open --> conn_ok

    conn_ok -->|No| wait_loop
    conn_ok -->|Yes| lock_ui --> start_graph_loop
    start_graph_loop --> read_snapshot --> render_view --> start_graph_loop
    lock_ui -. close app .-> stop
```

## MVC Class Diagram

```mermaid
classDiagram
    class Controller {
        -model: Model
        -view: View
        -is_frozen: bool
        +waiting_for_port_selection(dt_ms)
        +update_available_ports(dt_ms)
        +open_connection(port, baudrate, samples_per_channel)
        +update_graph(dt_ms)
        +snapshot_show()
        +save_snapshot()
        +is_running: bool
    }

    class View {
        -master: QMainWindow
        -port: QComboBox
        -baudrate: QComboBox
        -samples_per_channel: QSpinBox
        -connect_button: QPushButton
        +set_controller(controller)
        +setup_ui()
        +on_connect()
        +update_ports(available_ports)
        +update_ui_elements()
        +display_data(data)
    }

    class Model {
        -serial_connection: Serial
        -read_thread: Thread
        -SAMPLES_PER_CHANNEL: int
        -__buffer: DataFrame
        -__snapshot: DataFrame
        +open_connection(port, baudrate, samples_per_channel)
        +start_continuous_read_from_serial(updaterate_sec, failure_duration)
        +get_available_ports() list~str~
        +get_snapshot(is_frozen) DataFrame
        +update_snapshot()
        +is_connected: bool
        +is_disconnected: bool
        +close_connection()
    }

    class Serial
    class DataFrame

    Controller --> Model : manages
    Controller --> View : updates
    View --> Controller : user actions
    Model --> Serial : owns connection
    Model --> DataFrame : stores buffer/snapshot
```

