from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any

from MainWindow import MainWindow


class ScrollableFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_configure(self, _event: tk.Event[tk.Misc]) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event[tk.Misc]) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)


class TkMainWindow:
    def __init__(self, settings_path: str | Path | None = None) -> None:
        self.root = tk.Tk()
        self.root.title("PrintGlow")
        self.root.geometry("1360x900")
        self.root.minsize(1100, 760)

        self._configure_styles()

        self._message_queue: queue.Queue[str] = queue.Queue()
        self.controller = MainWindow(settings_path=settings_path, message_handler=self._post_message)

        self.value_vars: dict[str, tk.StringVar] = {}
        self.command_vars: dict[str, tk.StringVar] = {}
        self.value_entries: dict[str, ttk.Entry] = {}
        self.command_entries: dict[str, ttk.Entry] = {}

        self.sent_log_index = 0
        self.received_log_index = 0

        self.port_var = tk.StringVar()
        self.connection_var = tk.StringVar()
        self.ack_var = tk.StringVar()
        self.op_run_var = tk.StringVar()
        self.read_fdia_var = tk.StringVar()
        self.rpm_var = tk.StringVar()
        self.tuning_status_var = tk.StringVar()

        self.curr_t_var = tk.StringVar()
        self.is_log_var = tk.BooleanVar()

        self.temp_set_vars = {tag: tk.StringVar() for tag in ("1", "2", "3", "4")}
        self.temp_current_vars = {tag: tk.StringVar() for tag in ("1", "2", "3", "4")}
        self.temp_button_text = {tag: tk.StringVar() for tag in ("1", "2", "3", "4")}
        self.temp_entries: dict[str, ttk.Entry] = {}

        self.fan_vars = {fan: tk.StringVar() for fan in (1, 2, 3)}
        self.fan_entries: dict[int, ttk.Entry] = {}
        self.custom_command_var = tk.StringVar()

        self.settings_path_var = tk.StringVar(value=str(self.controller.settings_path))
        self.firmware_var = tk.StringVar()
        self.tuning_temp_var = tk.StringVar()
        self.tuning_cycles_var = tk.StringVar()
        self.tuning_p_var = tk.StringVar()
        self.tuning_i_var = tk.StringVar()
        self.tuning_d_var = tk.StringVar()

        self.puller_auto_var = tk.BooleanVar()
        self.winder_auto_var = tk.BooleanVar()
        self.spooler_auto_var = tk.BooleanVar()
        self._syncing_ui = False

        self.notebook = ttk.Notebook(self.root)
        self.controls_tab = ttk.Frame(self.notebook, padding=12)
        self.pid_tab = ttk.Frame(self.notebook, padding=12)
        self.settings_tab = ttk.Frame(self.notebook, padding=12)
        self.commands_tab = ttk.Frame(self.notebook, padding=12)
        self.logs_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.controls_tab, text="Controls")
        self.notebook.add(self.pid_tab, text="PID Tuning")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.commands_tab, text="Commands")
        self.notebook.add(self.logs_tab, text="Logs")
        self.notebook.pack(fill="both", expand=True)

        self._build_controls_tab()
        self._build_pid_tab()
        self._build_settings_tab()
        self._build_commands_tab()
        self._build_logs_tab()
        self._bind_ui_variables()

        self._load_model_into_vars(force=True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._schedule_poll()

    def run(self) -> None:
        self.root.mainloop()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.configure(bg="#17191c")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background="#17191c")
        style.configure("TLabelframe", background="#17191c", foreground="#f1e2c6")
        style.configure("TLabelframe.Label", background="#17191c", foreground="#f1e2c6", font=("Segoe UI Semibold", 10))
        style.configure("TLabel", background="#17191c", foreground="#e7e3db")
        style.configure("Header.TLabel", background="#17191c", foreground="#ffbf69", font=("Segoe UI Semibold", 16))
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", padding=7)
        style.configure("Status.TLabel", background="#17191c", foreground="#ffbf69", font=("Consolas", 10))
        style.configure("TCheckbutton", background="#17191c", foreground="#e7e3db")
        style.configure("TRadiobutton", background="#17191c", foreground="#e7e3db")
        style.configure("TNotebook", background="#17191c")
        style.configure("TNotebook.Tab", padding=(12, 8))

    def _build_controls_tab(self) -> None:
        self.controls_tab.columnconfigure(0, weight=1)
        self.controls_tab.columnconfigure(1, weight=1)

        header = ttk.Label(self.controls_tab, text="PrintGlow Controller", style="Header.TLabel")
        header.grid(row=0, column=0, sticky="w")

        subheader = ttk.Label(self.controls_tab, textvariable=self.settings_path_var, style="Status.TLabel")
        subheader.grid(row=0, column=1, sticky="e")

        connection = ttk.LabelFrame(self.controls_tab, text="Connection", padding=12)
        connection.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(12, 8))
        connection.columnconfigure(1, weight=1)

        ttk.Label(connection, text="COM Port").grid(row=0, column=0, sticky="w")
        self.port_combo = ttk.Combobox(connection, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky="ew", padx=(8, 8))

        ttk.Button(connection, text="Refresh Ports", command=self._refresh_ports).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(connection, text="Connect", style="Accent.TButton", command=self._connect).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(connection, text="Disconnect", command=self._disconnect).grid(row=0, column=4)

        ttk.Label(connection, text="Connected").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Label(connection, textvariable=self.connection_var, style="Status.TLabel").grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Label(connection, text="Ack").grid(row=1, column=2, sticky="e", pady=(10, 0))
        ttk.Label(connection, textvariable=self.ack_var, style="Status.TLabel").grid(row=1, column=3, sticky="w", pady=(10, 0))
        ttk.Label(connection, text="Operation").grid(row=1, column=4, sticky="e", pady=(10, 0))
        ttk.Label(connection, textvariable=self.op_run_var, style="Status.TLabel").grid(row=1, column=5, sticky="w", pady=(10, 0))

        temperature = ttk.LabelFrame(self.controls_tab, text="Temperature", padding=12)
        temperature.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=8)
        temperature.columnconfigure(1, weight=1)

        ttk.Label(temperature, text="Zone").grid(row=0, column=0, sticky="w")
        ttk.Label(temperature, text="Set Temp").grid(row=0, column=1, sticky="w", padx=(8, 8))
        ttk.Label(temperature, text="Current").grid(row=0, column=2, sticky="w", padx=(8, 8))
        ttk.Label(temperature, text="State").grid(row=0, column=3, sticky="w", padx=(8, 8))

        for row, tag in enumerate(("1", "2", "3", "4"), start=1):
            ttk.Label(temperature, text=f"T{tag}").grid(row=row, column=0, sticky="w", pady=4)
            entry = ttk.Entry(temperature, textvariable=self.temp_set_vars[tag], width=12)
            entry.grid(row=row, column=1, sticky="w", padx=(8, 8), pady=4)
            self.temp_entries[tag] = entry
            ttk.Label(temperature, textvariable=self.temp_current_vars[tag], style="Status.TLabel").grid(row=row, column=2, sticky="w", padx=(8, 8), pady=4)
            ttk.Button(temperature, textvariable=self.temp_button_text[tag], command=lambda current_tag=tag: self._toggle_temp(current_tag)).grid(row=row, column=3, sticky="w", padx=(8, 8), pady=4)

        motors = ttk.LabelFrame(self.controls_tab, text="Motion", padding=12)
        motors.grid(row=1, column=1, sticky="nsew", pady=(12, 8))
        motors.columnconfigure(1, weight=1)

        self.motor_entries: dict[str, list[ttk.Entry]] = {}
        motor_rows = [
            ("Auger", "Auger", "Set auger speed"),
            ("Puller", "", "Set puller speed"),
            ("Spooler", "Spooler", "Auto spooler from puller"),
            ("Manual Spool", "Spool", "Manual spool speed"),
            ("Winder", "Winder", "Set winder speed"),
        ]

        self.motor_vars = {
            "Auger": tk.StringVar(),
            "Puller": tk.StringVar(),
            "Spooler": tk.StringVar(),
            "Winder": tk.StringVar(),
        }

        for row, (label_text, command, button_text) in enumerate(motor_rows):
            ttk.Label(motors, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
            key = "Spooler" if label_text == "Manual Spool" else label_text
            entry = ttk.Entry(motors, textvariable=self.motor_vars[key], width=14)
            entry.grid(row=row, column=1, sticky="ew", padx=(8, 8), pady=4)
            self.motor_entries.setdefault(key, []).append(entry)
            ttk.Button(motors, text=button_text, command=lambda current_command=command: self._motor_control(current_command)).grid(row=row, column=2, sticky="ew", pady=4)

        fans = ttk.LabelFrame(self.controls_tab, text="Fans", padding=12)
        fans.grid(row=3, column=0, sticky="nsew", padx=(0, 8), pady=8)

        for row, fan in enumerate((1, 2, 3)):
            ttk.Label(fans, text=f"Fan {fan}").grid(row=row, column=0, sticky="w", pady=4)
            entry = ttk.Entry(fans, textvariable=self.fan_vars[fan], width=10)
            entry.grid(row=row, column=1, sticky="w", padx=(8, 8), pady=4)
            self.fan_entries[fan] = entry
            ttk.Button(fans, text="Apply", command=lambda current_fan=fan: self._fan_apply(current_fan)).grid(row=row, column=2, padx=(0, 8), pady=4)
            ttk.Button(fans, text="Off", command=lambda current_fan=fan: self._fan_off(current_fan)).grid(row=row, column=3, pady=4)

        operation = ttk.LabelFrame(self.controls_tab, text="Operation", padding=12)
        operation.grid(row=3, column=1, sticky="nsew", pady=8)
        operation.columnconfigure(0, weight=1)
        operation.columnconfigure(1, weight=1)
        operation.columnconfigure(2, weight=1)
        operation.columnconfigure(3, weight=1)

        ttk.Checkbutton(operation, text="Puller Auto", variable=self.puller_auto_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(operation, text="Winder Auto", variable=self.winder_auto_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(operation, text="Spooler Auto", variable=self.spooler_auto_var).grid(row=0, column=2, sticky="w")

        ttk.Button(operation, text="Start Operation", style="Accent.TButton", command=self._start_operation).grid(row=1, column=0, sticky="ew", pady=(12, 0), padx=(0, 8))
        ttk.Button(operation, text="Start Spooling", command=self._start_spooling).grid(row=1, column=1, sticky="ew", pady=(12, 0), padx=8)
        ttk.Button(operation, text="Stop Operation", command=self._stop_operation).grid(row=1, column=2, sticky="ew", pady=(12, 0), padx=8)
        ttk.Button(operation, text="Emergency Stop", command=self._emergency_stop).grid(row=1, column=3, sticky="ew", pady=(12, 0), padx=(8, 0))

        ttk.Label(operation, text="Read Dia").grid(row=2, column=0, sticky="w", pady=(12, 0))
        ttk.Label(operation, textvariable=self.read_fdia_var, style="Status.TLabel").grid(row=2, column=1, sticky="w", pady=(12, 0))
        ttk.Label(operation, text="RPM").grid(row=2, column=2, sticky="w", pady=(12, 0))
        ttk.Label(operation, textvariable=self.rpm_var, style="Status.TLabel").grid(row=3, column=0, columnspan=4, sticky="w")

        custom = ttk.LabelFrame(self.controls_tab, text="Custom Command", padding=12)
        custom.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=8)
        custom.columnconfigure(0, weight=1)

        self.custom_entry = ttk.Entry(custom, textvariable=self.custom_command_var)
        self.custom_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.custom_entry.bind("<Return>", self._on_custom_return)
        self.custom_entry.bind("<Up>", self._on_custom_up)
        self.custom_entry.bind("<Down>", self._on_custom_down)
        ttk.Button(custom, text="Send Command", command=self._custom_send).grid(row=0, column=1)

    def _build_pid_tab(self) -> None:
        self.pid_tab.columnconfigure(0, weight=1)

        tuning = ttk.LabelFrame(self.pid_tab, text="PID Tuning", padding=12)
        tuning.grid(row=0, column=0, sticky="nsew")
        tuning.columnconfigure(4, weight=1)

        ttk.Label(tuning, text="Target").grid(row=0, column=0, sticky="w")
        for column, tag in enumerate(("1", "2", "3", "4"), start=1):
            ttk.Radiobutton(tuning, text=f"T{tag}", value=tag, variable=self.curr_t_var).grid(row=0, column=column, sticky="w")

        ttk.Label(tuning, text="Tuning Temp").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.tuning_temp_entry = ttk.Entry(tuning, textvariable=self.tuning_temp_var, width=10)
        self.tuning_temp_entry.grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Label(tuning, text="Cycles").grid(row=1, column=2, sticky="w", pady=(10, 0))
        self.tuning_cycles_entry = ttk.Entry(tuning, textvariable=self.tuning_cycles_var, width=10)
        self.tuning_cycles_entry.grid(row=1, column=3, sticky="w", pady=(10, 0))

        ttk.Label(tuning, text="P").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.tuning_p_entry = ttk.Entry(tuning, textvariable=self.tuning_p_var, width=12)
        self.tuning_p_entry.grid(row=2, column=1, sticky="w", pady=(10, 0))
        ttk.Label(tuning, text="I").grid(row=2, column=2, sticky="w", pady=(10, 0))
        self.tuning_i_entry = ttk.Entry(tuning, textvariable=self.tuning_i_var, width=12)
        self.tuning_i_entry.grid(row=2, column=3, sticky="w", pady=(10, 0))
        ttk.Label(tuning, text="D").grid(row=2, column=4, sticky="w", pady=(10, 0))
        self.tuning_d_entry = ttk.Entry(tuning, textvariable=self.tuning_d_var, width=12)
        self.tuning_d_entry.grid(row=2, column=5, sticky="w", pady=(10, 0))

        ttk.Button(tuning, text="Start Tuning", command=self._start_tuning).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(tuning, text="Set PID", command=self._set_pid).grid(row=3, column=2, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Checkbutton(tuning, text="Enable Log File", variable=self.is_log_var, command=self._apply_logging_flag).grid(row=3, column=4, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Label(tuning, textvariable=self.tuning_status_var, style="Status.TLabel").grid(row=4, column=0, columnspan=6, sticky="w", pady=(10, 0))

    def _build_settings_tab(self) -> None:
        self.settings_tab.columnconfigure(0, weight=1)

        toolbar = ttk.Frame(self.settings_tab)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        toolbar.columnconfigure(4, weight=1)

        ttk.Label(toolbar, text="Firmware Version").grid(row=0, column=0, sticky="w")
        ttk.Entry(toolbar, textvariable=self.firmware_var, width=18).grid(row=0, column=1, padx=(8, 16), sticky="w")
        ttk.Button(toolbar, text="Read Settings", command=self._read_settings).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(toolbar, text="Write Settings", command=self._write_settings).grid(row=0, column=3)

        self.settings_scroll = ScrollableFrame(self.settings_tab)
        self.settings_scroll.grid(row=1, column=0, sticky="nsew")
        self.settings_tab.rowconfigure(1, weight=1)

        for row, field_name in enumerate(self.controller.sett.values.to_dict().keys()):
            ttk.Label(self.settings_scroll.inner, text=field_name).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
            variable = tk.StringVar()
            entry = ttk.Entry(self.settings_scroll.inner, textvariable=variable)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.settings_scroll.inner.columnconfigure(1, weight=1)
            self.value_vars[field_name] = variable
            self.value_entries[field_name] = entry

    def _build_commands_tab(self) -> None:
        self.commands_tab.columnconfigure(0, weight=1)

        note = ttk.Label(
            self.commands_tab,
            text="Command templates are kept separate from UI logic and can be edited here.",
            style="Status.TLabel",
        )
        note.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.commands_scroll = ScrollableFrame(self.commands_tab)
        self.commands_scroll.grid(row=1, column=0, sticky="nsew")
        self.commands_tab.rowconfigure(1, weight=1)

        for row, field_name in enumerate(self.controller.sett.commands.to_dict().keys()):
            ttk.Label(self.commands_scroll.inner, text=field_name).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
            variable = tk.StringVar()
            entry = ttk.Entry(self.commands_scroll.inner, textvariable=variable)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.commands_scroll.inner.columnconfigure(1, weight=1)
            self.command_vars[field_name] = variable
            self.command_entries[field_name] = entry

    def _build_logs_tab(self) -> None:
        self.logs_tab.columnconfigure(0, weight=1)
        self.logs_tab.columnconfigure(1, weight=1)
        self.logs_tab.rowconfigure(0, weight=1)

        sent_frame = ttk.LabelFrame(self.logs_tab, text="Sent", padding=8)
        sent_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sent_frame.rowconfigure(0, weight=1)
        sent_frame.columnconfigure(0, weight=1)

        received_frame = ttk.LabelFrame(self.logs_tab, text="Received", padding=8)
        received_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        received_frame.rowconfigure(0, weight=1)
        received_frame.columnconfigure(0, weight=1)

        self.sent_text = ScrolledText(sent_frame, wrap="word", bg="#101214", fg="#dfe7ee", insertbackground="#dfe7ee")
        self.sent_text.grid(row=0, column=0, sticky="nsew")
        self.sent_text.configure(state="disabled")

        self.received_text = ScrolledText(received_frame, wrap="word", bg="#101214", fg="#dfe7ee", insertbackground="#dfe7ee")
        self.received_text.grid(row=0, column=0, sticky="nsew")
        self.received_text.configure(state="disabled")

    def _format_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "True" if value else "False"
        if isinstance(value, float):
            return format(value, ".15g")
        return str(value)

    def _bind_ui_variables(self) -> None:
        self.port_var.trace_add("write", lambda *_: self._sync_port_var())
        self.curr_t_var.trace_add("write", lambda *_: self._sync_curr_t_var())
        self.is_log_var.trace_add("write", lambda *_: self._sync_is_log_var())
        self.firmware_var.trace_add("write", lambda *_: self._sync_firmware_var())
        self.puller_auto_var.trace_add("write", lambda *_: self._sync_operation_toggle("PullerToggle", self.puller_auto_var))
        self.winder_auto_var.trace_add("write", lambda *_: self._sync_operation_toggle("WinderToggle", self.winder_auto_var))
        self.spooler_auto_var.trace_add("write", lambda *_: self._sync_operation_toggle("SpoolerToggle", self.spooler_auto_var))

        for tag, variable in self.temp_set_vars.items():
            variable.trace_add("write", lambda *_args, current_tag=tag: self._sync_float_attr(self.controller.comViewModel.comModel, f"SetTemp{current_tag}", self.temp_set_vars[current_tag]))

        for key, variable in self.motor_vars.items():
            variable.trace_add("write", lambda *_args, current_key=key: self._sync_float_attr(self.controller.sett.values, current_key, self.motor_vars[current_key]))

        for fan, variable in self.fan_vars.items():
            variable.trace_add("write", lambda *_args, current_fan=fan: self._sync_int_attr(self.controller.sett.values, f"Fan{current_fan}", self.fan_vars[current_fan]))

        tuning_fields = {
            "TuningTemp": (self.tuning_temp_var, int),
            "TuningCycles": (self.tuning_cycles_var, int),
            "TuningP": (self.tuning_p_var, float),
            "TuningI": (self.tuning_i_var, float),
            "TuningD": (self.tuning_d_var, float),
        }
        for attr_name, (variable, caster) in tuning_fields.items():
            variable.trace_add("write", lambda *_args, current_attr=attr_name, current_var=variable, current_caster=caster: self._sync_typed_attr(self.controller.sett.values, current_attr, current_var, current_caster))

        for field_name, variable in self.value_vars.items():
            variable.trace_add("write", lambda *_args, current_field=field_name: self._sync_setting_value_field(current_field))

        for field_name, variable in self.command_vars.items():
            variable.trace_add("write", lambda *_args, current_field=field_name: self._sync_command_field(current_field))

    def _sync_port_var(self) -> None:
        if self._syncing_ui:
            return
        self.controller.comViewModel.comModel.selectedPort = self.port_var.get() or None

    def _sync_curr_t_var(self) -> None:
        if self._syncing_ui:
            return
        self.controller.comViewModel.comModel.CurrT = self.curr_t_var.get() or "1"

    def _sync_is_log_var(self) -> None:
        if self._syncing_ui:
            return
        self.controller.comViewModel.comModel.isLog = self.is_log_var.get()

    def _sync_firmware_var(self) -> None:
        if self._syncing_ui:
            return
        self.controller.sett.FirmwareVersion = self.firmware_var.get()

    def _sync_operation_toggle(self, attr_name: str, variable: tk.BooleanVar) -> None:
        if self._syncing_ui:
            return
        setattr(self.controller, attr_name, variable.get())

    def _sync_float_attr(self, target: Any, attr_name: str, variable: tk.StringVar) -> None:
        self._sync_typed_attr(target, attr_name, variable, float)

    def _sync_int_attr(self, target: Any, attr_name: str, variable: tk.StringVar) -> None:
        self._sync_typed_attr(target, attr_name, variable, lambda value: int(float(value)))

    def _sync_typed_attr(self, target: Any, attr_name: str, variable: tk.StringVar, caster: Any) -> None:
        if self._syncing_ui:
            return
        text = variable.get().strip()
        if text == "":
            return
        try:
            setattr(target, attr_name, caster(text))
        except ValueError:
            return

    def _sync_setting_value_field(self, field_name: str) -> None:
        if self._syncing_ui:
            return
        variable = self.value_vars[field_name]
        current_value = getattr(self.controller.sett.values, field_name)
        text = variable.get()
        if text.strip() == "":
            return
        try:
            setattr(self.controller.sett.values, field_name, self._parse_value(text, current_value, field_name))
        except ValueError:
            return

    def _sync_command_field(self, field_name: str) -> None:
        if self._syncing_ui:
            return
        setattr(self.controller.sett.commands, field_name, self.command_vars[field_name].get())

    def _safe_focus_get(self) -> tk.Misc | None:
        try:
            return self.root.focus_get()
        except (tk.TclError, KeyError):
            return None

    def _load_model_into_vars(self, force: bool = False) -> None:
        com_model = self.controller.comViewModel.comModel
        setting = self.controller.sett
        focus_widget = None if force else self._safe_focus_get()
        self._syncing_ui = True
        try:
            self.port_combo.configure(values=com_model.Ports)
            if force or focus_widget is not self.port_combo:
                self.port_var.set(com_model.selectedPort or "")

            self.curr_t_var.set(com_model.CurrT)
            self.is_log_var.set(com_model.isLog)
            self.firmware_var.set(setting.FirmwareVersion or "")

            temp_entries = {
                "1": com_model.SetTemp1,
                "2": com_model.SetTemp2,
                "3": com_model.SetTemp3,
                "4": com_model.SetTemp4,
            }

            for tag, value in temp_entries.items():
                if force or focus_widget is not self.temp_entries[tag]:
                    self.temp_set_vars[tag].set(self._format_value(value))

            motor_values = {
                "Auger": setting.values.Auger,
                "Puller": setting.values.Puller,
                "Spooler": setting.values.Spooler,
                "Winder": setting.values.Winder,
            }
            for key, value in motor_values.items():
                if force or all(focus_widget is not entry for entry in self.motor_entries.get(key, [])):
                    self.motor_vars[key].set(self._format_value(value))

            for fan in (1, 2, 3):
                if force or focus_widget is not self.fan_entries[fan]:
                    self.fan_vars[fan].set(self._format_value(getattr(setting.values, f"Fan{fan}")))

            self.puller_auto_var.set(self.controller.PullerToggle)
            self.winder_auto_var.set(self.controller.WinderToggle)
            self.spooler_auto_var.set(self.controller.SpoolerToggle)

            if force or focus_widget is not self.tuning_temp_entry:
                self.tuning_temp_var.set(self._format_value(setting.values.TuningTemp))
            if force or focus_widget is not self.tuning_cycles_entry:
                self.tuning_cycles_var.set(self._format_value(setting.values.TuningCycles))
            if force or focus_widget is not self.tuning_p_entry:
                self.tuning_p_var.set(self._format_value(setting.values.TuningP))
            if force or focus_widget is not self.tuning_i_entry:
                self.tuning_i_var.set(self._format_value(setting.values.TuningI))
            if force or focus_widget is not self.tuning_d_entry:
                self.tuning_d_var.set(self._format_value(setting.values.TuningD))

            for field_name, variable in self.value_vars.items():
                entry = self.value_entries[field_name]
                if force or focus_widget is not entry:
                    variable.set(self._format_value(getattr(setting.values, field_name)))

            for field_name, variable in self.command_vars.items():
                entry = self.command_entries[field_name]
                if force or focus_widget is not entry:
                    variable.set(getattr(setting.commands, field_name) or "")
        finally:
            self._syncing_ui = False

        self._sync_runtime_status()

    def _sync_runtime_status(self) -> None:
        com_model = self.controller.comViewModel.comModel
        setting = self.controller.sett
        view_model = self.controller.comViewModel

        self.connection_var.set("Connected" if com_model.printerConnected else "Disconnected")
        self.ack_var.set(str(com_model.Ack))
        self.op_run_var.set("Running" if com_model.OpRun else "Idle")
        self.read_fdia_var.set(self._format_value(setting.values.ReadFDia))
        self.rpm_var.set(
            f"Auger {self._format_value(view_model.AugerRPM)} | "
            f"Puller {self._format_value(view_model.PullerRPM)} | "
            f"Spooler {self._format_value(view_model.SpoolerRPM)} | "
            f"Winder {self._format_value(view_model.WinderRPM)}"
        )
        self.tuning_status_var.set("Tuning active" if com_model.isTuning else "Tuning idle")

        temp_values = {
            "1": com_model.Temp1,
            "2": com_model.Temp2,
            "3": com_model.Temp3,
            "4": com_model.Temp4,
        }
        temp_states = {
            "1": com_model.Temp1On,
            "2": com_model.Temp2On,
            "3": com_model.Temp3On,
            "4": com_model.Temp4On,
        }
        for tag in ("1", "2", "3", "4"):
            self.temp_current_vars[tag].set(self._format_value(temp_values[tag]))
            self.temp_button_text[tag].set("Turn Off" if temp_states[tag] else "Turn On")

    def _parse_value(self, text: str, current_value: Any, field_name: str) -> Any:
        if isinstance(current_value, int) and not isinstance(current_value, bool):
            return int(float(text))
        if isinstance(current_value, float):
            return float(text)
        return text

    def _apply_ui_to_model(self) -> bool:
        try:
            com_model = self.controller.comViewModel.comModel
            setting = self.controller.sett

            com_model.selectedPort = self.port_var.get() or None
            com_model.CurrT = self.curr_t_var.get() or "1"
            com_model.isLog = self.is_log_var.get()

            com_model.SetTemp1 = float(self.temp_set_vars["1"].get())
            com_model.SetTemp2 = float(self.temp_set_vars["2"].get())
            com_model.SetTemp3 = float(self.temp_set_vars["3"].get())
            com_model.SetTemp4 = float(self.temp_set_vars["4"].get())

            setting.FirmwareVersion = self.firmware_var.get()
            setting.values.TuningTemp = int(float(self.tuning_temp_var.get()))
            setting.values.TuningCycles = int(float(self.tuning_cycles_var.get()))
            setting.values.TuningP = float(self.tuning_p_var.get())
            setting.values.TuningI = float(self.tuning_i_var.get())
            setting.values.TuningD = float(self.tuning_d_var.get())
            self.value_vars["TuningTemp"].set(self.tuning_temp_var.get())
            self.value_vars["TuningCycles"].set(self.tuning_cycles_var.get())
            self.value_vars["TuningP"].set(self.tuning_p_var.get())
            self.value_vars["TuningI"].set(self.tuning_i_var.get())
            self.value_vars["TuningD"].set(self.tuning_d_var.get())

            for field_name, variable in self.value_vars.items():
                current_value = getattr(setting.values, field_name)
                setattr(setting.values, field_name, self._parse_value(variable.get(), current_value, field_name))

            for field_name, variable in self.command_vars.items():
                setattr(setting.commands, field_name, variable.get())

            setting.values.Auger = float(self.motor_vars["Auger"].get())
            setting.values.Puller = float(self.motor_vars["Puller"].get())
            setting.values.Spooler = float(self.motor_vars["Spooler"].get())
            setting.values.Winder = float(self.motor_vars["Winder"].get())

            setting.values.Fan1 = int(float(self.fan_vars[1].get()))
            setting.values.Fan2 = int(float(self.fan_vars[2].get()))
            setting.values.Fan3 = int(float(self.fan_vars[3].get()))

            self.controller.PullerToggle = self.puller_auto_var.get()
            self.controller.WinderToggle = self.winder_auto_var.get()
            self.controller.SpoolerToggle = self.spooler_auto_var.get()
            return True
        except ValueError as ex:
            messagebox.showerror("Invalid Value", f"Could not parse a numeric field.\n{ex}")
            return False

    def _refresh_ports(self) -> None:
        self.controller.CheckCom()
        self.port_combo.configure(values=self.controller.comViewModel.comModel.Ports)
        if self.controller.comViewModel.comModel.selectedPort:
            self.port_var.set(self.controller.comViewModel.comModel.selectedPort)

    def _run_background(self, target: Any) -> None:
        threading.Thread(target=target, daemon=True).start()

    def _connect(self) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(lambda: self.controller.ConnectCom())

    def _disconnect(self) -> None:
        self._run_background(lambda: self.controller.DisconnectCom())

    def _toggle_temp(self, tag: str) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(lambda current_tag=tag: self.controller.TempClick(current_tag))

    def _start_tuning(self) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(self.controller.StartTuningClick)

    def _set_pid(self) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(self.controller.SetPIDClick)

    def _apply_logging_flag(self) -> None:
        self.controller.comViewModel.comModel.isLog = self.is_log_var.get()

    def _motor_control(self, motor: str) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(lambda current_motor=motor: self.controller.MotorClick(current_motor))

    def _fan_apply(self, fan: int) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(lambda current_fan=fan: self.controller.comViewModel.FanControl(False, current_fan))

    def _fan_off(self, fan: int) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(lambda current_fan=fan: self.controller.comViewModel.FanControl(True, current_fan))

    def _start_operation(self) -> None:
        if not self._apply_ui_to_model():
            return
        self._run_background(
            lambda: self.controller.StartOpClick(
                PullerToggle=self.puller_auto_var.get(),
                WinderToggle=self.winder_auto_var.get(),
                SpoolerToggle=self.spooler_auto_var.get(),
            )
        )

    def _start_spooling(self) -> None:
        self._run_background(self.controller.StartSpoolingClick)

    def _stop_operation(self) -> None:
        self._run_background(self.controller.StopOpClick)

    def _emergency_stop(self) -> None:
        self._run_background(self.controller.EmergencyClick)

    def _custom_send(self) -> None:
        if not self._apply_ui_to_model():
            return
        new_text = self.controller.CustomClick(self.custom_command_var.get())
        self.custom_command_var.set(new_text)

    def _on_custom_return(self, _event: tk.Event[tk.Misc]) -> str:
        if not self._apply_ui_to_model():
            return "break"
        new_text = self.controller.CustomCommandEnter("Enter", self.custom_command_var.get())
        self.custom_command_var.set(new_text)
        return "break"

    def _on_custom_up(self, _event: tk.Event[tk.Misc]) -> str:
        new_text = self.controller.CustomCommandEnter("Up", self.custom_command_var.get())
        self.custom_command_var.set(new_text)
        self.custom_entry.icursor("end")
        return "break"

    def _on_custom_down(self, _event: tk.Event[tk.Misc]) -> str:
        new_text = self.controller.CustomCommandEnter("Down", self.custom_command_var.get())
        self.custom_command_var.set(new_text)
        self.custom_entry.icursor("end")
        return "break"

    def _read_settings(self) -> None:
        self.controller.ReadSettClick()
        self._load_model_into_vars(force=True)

    def _write_settings(self) -> None:
        if not self._apply_ui_to_model():
            return
        self.controller.sett.WriteSettings(self.controller.sett)
        self._post_message("Settings saved.")

    def _append_log(self, widget: ScrolledText, lines: list[str]) -> None:
        if not lines:
            return
        widget.configure(state="normal")
        for line in lines:
            widget.insert("end", line + "\n")
        widget.see("end")
        widget.configure(state="disabled")

    def _drain_runtime_messages(self) -> None:
        while True:
            try:
                message = self._message_queue.get_nowait()
            except queue.Empty:
                break
            messagebox.showinfo("PrintGlow", message)

    def _post_message(self, message: str) -> None:
        self._message_queue.put(message)

    def _schedule_poll(self) -> None:
        self._poll()
        self.root.after(150, self._schedule_poll)

    def _poll(self) -> None:
        self._load_model_into_vars()

        sent_lines = self.controller.serialDataSent[self.sent_log_index :]
        self.sent_log_index = len(self.controller.serialDataSent)
        self._append_log(self.sent_text, sent_lines)

        received_lines = self.controller.serialDataReceived[self.received_log_index :]
        self.received_log_index = len(self.controller.serialDataReceived)
        self._append_log(self.received_text, received_lines)

        self._drain_runtime_messages()

    def _on_close(self) -> None:
        try:
            if self._apply_ui_to_model():
                self.controller.AppClose(exit_process=False)
        finally:
            self.root.destroy()
