"""Cross-platform Native Desktop GUI (`tkinter.ttk`) for Linux, macOS, and Windows.

Drives `purpleair-data-logger` strictly through `CliSubprocessBridge` (CLI + JSON)
with zero duplicated engine or PurpleAir API logic.
"""

from __future__ import annotations

import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from .cli_bridge import CliSubprocessBridge
from .locale_manager import LocaleManager

STATIC_DIR = Path(__file__).resolve().parent / "static"
if not STATIC_DIR.is_dir() and getattr(sys, "_MEIPASS", None):  # pragma: no cover
    _cand = Path(sys._MEIPASS) / "purpleair_data_logger" / "gui" / "static"
    if _cand.is_dir():
        STATIC_DIR = _cand

PALETTES: dict[str, dict[str, str]] = {
    "dark": {
        "bg": "#0f172a",
        "panel": "#1e293b",
        "card": "#0b1220",
        "fg": "#f1f5f9",
        "muted": "#94a3b8",
        "accent": "#a855f7",
        "success": "#10b981",
        "danger": "#ef4444",
        "border": "#334155",
    },
    "light": {
        "bg": "#f8fafc",
        "panel": "#ffffff",
        "card": "#e2e8f0",
        "fg": "#0f172a",
        "muted": "#475569",
        "accent": "#7c3aed",
        "success": "#059669",
        "danger": "#dc2626",
        "border": "#cbd5e1",
    },
}

SERIES_COLORS = [
    "#a855f7",
    "#06b6d4",
    "#10b981",
    "#f59e0b",
    "#f43f5e",
    "#3b82f6",
]


class DesktopLoggerStudio:
    """Cross-platform tkinter.ttk GUI interacting exclusively with the CLI + JSON."""

    def __init__(
        self,
        bridge: CliSubprocessBridge,
        schedule_refresh: bool = True,
        locale_mgr: LocaleManager | None = None,
    ) -> None:
        self.bridge = bridge
        self.config_doc: dict[str, Any] = self.bridge.load_config_dict()
        gui_cfg = (
            self.config_doc.get("gui", {})
            if isinstance(self.config_doc.get("gui"), dict)
            else {}
        )
        self.locale = locale_mgr or LocaleManager(
            locale=str(gui_cfg.get("locale") or gui_cfg.get("language") or "en"),
            locale_file=str(gui_cfg.get("locale_file") or "") or None,
        )

        self.theme_name = "light" if gui_cfg.get("theme") == "light" else "dark"
        self.refresh_ms = max(250, int(gui_cfg.get("refresh_interval_ms", 1000)))
        win_w = max(800, int(gui_cfg.get("window_width", 1280)))
        win_h = max(600, int(gui_cfg.get("window_height", 820)))

        self.root = tk.Tk()
        self.root.title(
            self.locale.t(
                "app.window_title",
                default=f"PurpleAir Data Logger Studio — {self.bridge.config_path.name}",
                filename=self.bridge.config_path.name,
            )
        )
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.minsize(920, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._selected_dut_index = 0
        self._after_id: str | None = None
        self._icon_image: tk.PhotoImage | None = None
        self._header_icon_img: tk.PhotoImage | None = None

        self._apply_icon()
        self._apply_style()
        self._build_layout()
        self.reload_from_disk()
        self.refresh_live_state(reschedule=schedule_refresh)

    def _apply_icon(self) -> None:
        """Apply custom branded icon to window titlebar, taskbar, and macOS Dock."""
        static_dir = STATIC_DIR
        png_path = static_dir / "app_icon.png"
        ico_path = static_dir / "app_icon.ico"
        icns_path = static_dir / "app_icon.icns"

        if png_path.is_file():
            try:
                self._icon_image = tk.PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self._icon_image)
            except Exception:
                pass

        if sys.platform == "win32" and ico_path.is_file():
            try:
                self.root.iconbitmap(default=str(ico_path))
            except Exception:
                pass

        if sys.platform == "darwin":
            self._set_macos_dock_icon(png_path if png_path.is_file() else icns_path)

    @staticmethod
    def _set_macos_dock_icon(icon_path: Path) -> bool:
        """Set the macOS Dock application icon via standard AppKit/ctypes."""
        if not icon_path.is_file():
            return False
        try:
            import ctypes
            import ctypes.util

            objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
            ctypes.cdll.LoadLibrary(
                "/System/Library/Frameworks/AppKit.framework/AppKit"
            )

            objc.objc_getClass.restype = ctypes.c_void_p
            objc.objc_getClass.argtypes = [ctypes.c_char_p]
            objc.sel_registerName.restype = ctypes.c_void_p
            objc.sel_registerName.argtypes = [ctypes.c_char_p]

            def call_msg(
                target: Any,
                sel_name: str,
                *args: Any,
                restype: Any = ctypes.c_void_p,
                argtypes: list[Any] | None = None,
            ) -> Any:
                fn = ctypes.cast(
                    objc.objc_msgSend,
                    ctypes.CFUNCTYPE(
                        restype, ctypes.c_void_p, ctypes.c_void_p, *(argtypes or [])
                    ),
                )
                return fn(
                    target, objc.sel_registerName(sel_name.encode("utf-8")), *args
                )

            cls_ns_app = objc.objc_getClass(b"NSApplication")
            cls_ns_image = objc.objc_getClass(b"NSImage")
            cls_ns_string = objc.objc_getClass(b"NSString")

            ns_app = call_msg(cls_ns_app, "sharedApplication")
            ns_path_str = call_msg(
                cls_ns_string,
                "stringWithUTF8String:",
                str(icon_path).encode("utf-8"),
                argtypes=[ctypes.c_char_p],
            )
            img_alloc = call_msg(cls_ns_image, "alloc")
            ns_img = call_msg(
                img_alloc,
                "initWithContentsOfFile:",
                ns_path_str,
                argtypes=[ctypes.c_void_p],
            )
            if ns_img:
                call_msg(
                    ns_app,
                    "setApplicationIconImage:",
                    ns_img,
                    argtypes=[ctypes.c_void_p],
                )
                return True
        except Exception:
            pass
        return False

    def _apply_style(self) -> None:
        pal = PALETTES[self.theme_name]
        self.root.configure(bg=pal["bg"])
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            ".", background=pal["bg"], foreground=pal["fg"], font=("TkDefaultFont", 10)
        )
        style.configure("TFrame", background=pal["bg"])
        style.configure("Panel.TFrame", background=pal["panel"])
        style.configure("Panel.TLabel", background=pal["panel"], foreground=pal["fg"])
        style.configure("Card.TFrame", background=pal["card"], relief="flat")
        style.configure("TLabel", background=pal["bg"], foreground=pal["fg"])
        style.configure(
            "CardTitle.TLabel",
            background=pal["card"],
            foreground=pal["muted"],
            font=("TkDefaultFont", 9),
        )
        style.configure(
            "CardValue.TLabel",
            background=pal["card"],
            foreground=pal["fg"],
            font=("TkDefaultFont", 15, "bold"),
        )
        style.configure(
            "Header.TLabel",
            background=pal["panel"],
            foreground=pal["fg"],
            font=("TkDefaultFont", 13, "bold"),
        )
        style.configure(
            "Subtle.TLabel",
            background=pal["panel"],
            foreground=pal["muted"],
            font=("TkDefaultFont", 9),
        )
        style.configure(
            "TButton", background=pal["panel"], foreground=pal["fg"], padding=(10, 5)
        )
        style.map("TButton", background=[("active", pal["border"])])
        style.configure(
            "Accent.TButton",
            background=pal["accent"],
            foreground="#ffffff",
            padding=(12, 6),
        )
        style.configure(
            "Danger.TButton",
            background=pal["danger"],
            foreground="#ffffff",
            padding=(12, 6),
        )
        style.configure("TNotebook", background=pal["bg"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=pal["panel"],
            foreground=pal["fg"],
            padding=(12, 6),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", pal["accent"])],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Treeview",
            background=pal["card"],
            fieldbackground=pal["card"],
            foreground=pal["fg"],
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading", background=pal["panel"], foreground=pal["fg"]
        )
        style.configure("TEntry", fieldbackground=pal["card"], foreground=pal["fg"])
        style.configure("TCombobox", fieldbackground=pal["card"], foreground=pal["fg"])
        style.configure("TCheckbutton", background=pal["bg"], foreground=pal["fg"])

    def _build_layout(self) -> None:
        pal = PALETTES[self.theme_name]

        header = ttk.Frame(self.root, style="Panel.TFrame", padding=(14, 10))
        header.pack(fill=tk.X)

        icon_thumb = STATIC_DIR / "app_icon_32.png"
        if icon_thumb.is_file():
            try:
                self._header_icon_img = tk.PhotoImage(file=str(icon_thumb))
                icon_lbl = ttk.Label(
                    header, image=self._header_icon_img, style="Panel.TLabel"
                )
                icon_lbl.pack(side=tk.LEFT, padx=(0, 10))
            except Exception:
                pass

        title_box = ttk.Frame(header, style="Panel.TFrame")
        title_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(
            title_box,
            text=self.locale.t(
                "app.header_title",
                default="PurpleAir Data Logger — Cross-Platform CLI Studio",
            ),
            style="Header.TLabel",
        ).pack(anchor=tk.W)
        self.cfg_path_var = tk.StringVar(
            value=self.locale.t(
                "labels.json_config",
                default=f"JSON Config: {self.bridge.config_path}",
                path=self.bridge.config_path,
            )
        )
        ttk.Label(
            title_box, textvariable=self.cfg_path_var, style="Subtle.TLabel"
        ).pack(anchor=tk.W)

        btn_bar = ttk.Frame(header, style="Panel.TFrame")
        btn_bar.pack(side=tk.RIGHT)
        ttk.Button(
            btn_bar,
            text=self.locale.t("buttons.open_json", default="Open JSON..."),
            command=self.action_open_config,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            btn_bar,
            text=self.locale.t("buttons.save_json", default="Save JSON"),
            command=self.action_save_all,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            btn_bar,
            text=self.locale.t("buttons.start_logger", default="Start CLI Logger"),
            style="Accent.TButton",
            command=self.action_start_run,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            btn_bar,
            text=self.locale.t("buttons.stop_logger", default="Stop CLI Logger"),
            style="Danger.TButton",
            command=self.action_stop_run,
        ).pack(side=tk.LEFT, padx=3)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 4))

        self._build_dashboard_tab()
        self._build_duts_tab()
        self._build_ezsnmp_studio_tab()
        self._build_sinks_and_gui_tab()
        self._build_explorer_tab()
        self._build_json_tab()

        footer = ttk.Frame(self.root, style="Panel.TFrame", padding=(12, 6))
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.audit_status_var = tk.StringVar(
            value=self.locale.t("status_bar.audit_ready", default="CLI Audit: Ready")
        )
        ttk.Label(
            footer, textvariable=self.audit_status_var, style="Subtle.TLabel"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.cli_bin_label = ttk.Label(
            footer,
            text=self.locale.t(
                "status_bar.backend_cli",
                default=f"Backend CLI: {' '.join(self.bridge.cli_base_command())}",
                cli_command=" ".join(self.bridge.cli_base_command()),
            ),
            style="Subtle.TLabel",
        )
        self.cli_bin_label.pack(side=tk.RIGHT)
        _ = pal

    def _build_dashboard_tab(self) -> None:
        pal = PALETTES[self.theme_name]
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(
            tab,
            text=self.locale.t("tabs.live_dashboard", default="1. Live Dashboard"),
        )

        kpi_row = ttk.Frame(tab)
        kpi_row.pack(fill=tk.X, pady=(0, 8))
        self.kpi_vars: dict[str, tk.StringVar] = {}
        kpi_specs = [
            ("state", self.locale.t("cards.cli_engine", default="CLI Engine")),
            ("cycles", self.locale.t("cards.cycles", default="Cycles")),
            ("batches", self.locale.t("cards.batches", default="Batches")),
            ("samples", self.locale.t("cards.samples", default="Samples")),
            ("queue", self.locale.t("cards.queue_depth", default="Queue Depth")),
            (
                "errors",
                self.locale.t("cards.poll_sink_errors", default="Poll / Sink Errors"),
            ),
        ]
        for key, label in kpi_specs:
            card = ttk.Frame(kpi_row, style="Card.TFrame", padding=(12, 8))
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor=tk.W)
            var = tk.StringVar(value="0")
            self.kpi_vars[key] = var
            ttk.Label(card, textvariable=var, style="CardValue.TLabel").pack(
                anchor=tk.W
            )

        act_row = ttk.Frame(tab)
        act_row.pack(fill=tk.X, pady=4)
        ttk.Button(
            act_row,
            text=self.locale.t(
                "buttons.run_single_cycle", default="Run Single Cycle (CLI --once)"
            ),
            command=self.action_run_once,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            act_row,
            text=self.locale.t(
                "buttons.probe_all_duts", default="Probe All Sensors (CLI probe)"
            ),
            command=self.action_probe_all,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            act_row,
            text=self.locale.t(
                "buttons.validate_config", default="Validate Config (CLI validate)"
            ),
            command=self.action_validate_saved,
        ).pack(side=tk.LEFT, padx=3)

        chart_ctrl_frame = ttk.Frame(tab, style="Panel.TFrame")
        chart_ctrl_frame.pack(fill=tk.X, pady=(6, 2))

        ttk.Label(
            chart_ctrl_frame,
            text=self.locale.t(
                "sections.realtime_series",
                default="Real-Time PurpleAir Numeric Series (streamed from `purpleair-data-logger run --json`):",
            ),
            style="Panel.TLabel",
        ).pack(side=tk.LEFT, anchor=tk.W)

        chart_act_box = ttk.Frame(chart_ctrl_frame, style="Panel.TFrame")
        chart_act_box.pack(side=tk.RIGHT)

        ttk.Label(
            chart_act_box,
            text=self.locale.t("labels.visible_series", default="Visible Series:"),
            style="Panel.TLabel",
        ).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Button(
            chart_act_box,
            text=self.locale.t("buttons.select_all", default="Select All"),
            command=self.action_select_all_series,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            chart_act_box,
            text=self.locale.t("buttons.clear_all", default="Clear All"),
            command=self.action_clear_all_series,
        ).pack(side=tk.LEFT, padx=2)

        self.series_selector_frame = ttk.Frame(
            tab, style="Panel.TFrame", padding=(2, 2)
        )
        self.series_selector_frame.pack(fill=tk.X, pady=(0, 4))
        self._series_vars: dict[str, tk.BooleanVar] = {}
        self._series_cbs: dict[str, ttk.Checkbutton] = {}
        self._last_series_map: dict[str, list[dict[str, Any]]] = {}
        self._user_modified_series: bool = False
        self._legend_hitboxes: list[tuple[float, float, float, float, str]] = []

        self.chart_canvas = tk.Canvas(
            tab,
            height=220,
            bg=pal["card"],
            highlightthickness=1,
            highlightbackground=pal["border"],
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.chart_canvas.bind("<Button-1>", self._on_canvas_click)

        bottom_split = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        bottom_split.pack(fill=tk.BOTH, expand=True)

        log_frame = ttk.Frame(bottom_split)
        ttk.Label(
            log_frame,
            text=self.locale.t(
                "sections.live_event_stream", default="Live CLI JSON Event Stream:"
            ),
        ).pack(anchor=tk.W)
        self.cli_log_text = tk.Text(
            log_frame,
            height=9,
            bg=pal["card"],
            fg=pal["fg"],
            insertbackground=pal["fg"],
            font=("Courier", 10),
        )
        self.cli_log_text.pack(fill=tk.BOTH, expand=True)
        bottom_split.add(log_frame, weight=3)

        audit_frame = ttk.Frame(bottom_split)
        ttk.Label(
            audit_frame,
            text=self.locale.t(
                "sections.command_audit", default="Behind-the-Scenes CLI Command Audit:"
            ),
        ).pack(anchor=tk.W)
        self.audit_tree = ttk.Treeview(
            audit_frame,
            columns=("time", "rc", "ms", "cmd"),
            show="headings",
            height=8,
        )
        self.audit_tree.heading(
            "time", text=self.locale.t("table_headers.utc_time", default="UTC Time")
        )
        self.audit_tree.heading(
            "rc", text=self.locale.t("table_headers.exit", default="Exit")
        )
        self.audit_tree.heading(
            "ms", text=self.locale.t("table_headers.ms", default="ms")
        )
        self.audit_tree.heading(
            "cmd",
            text=self.locale.t("table_headers.command", default="Executed CLI Command"),
        )
        self.audit_tree.column("time", width=90, stretch=False)
        self.audit_tree.column("rc", width=45, stretch=False)
        self.audit_tree.column("ms", width=65, stretch=False)
        self.audit_tree.column("cmd", width=360, stretch=True)
        self.audit_tree.pack(fill=tk.BOTH, expand=True)
        bottom_split.add(audit_frame, weight=2)

    def _build_duts_tab(self) -> None:
        pal = PALETTES[self.theme_name]
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(
            tab,
            text=self.locale.t("tabs.duts_and_metrics", default="2. Sensors & Metrics"),
        )

        pane = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(pane, padding=(0, 0, 8, 0))
        ttk.Label(
            left,
            text=self.locale.t(
                "sections.configured_duts", default="Configured Sensors:"
            ),
        ).pack(anchor=tk.W)
        self.dut_listbox = tk.Listbox(
            left,
            bg=pal["card"],
            fg=pal["fg"],
            selectbackground=pal["accent"],
            exportselection=False,
            width=26,
        )
        self.dut_listbox.pack(fill=tk.BOTH, expand=True, pady=4)
        self.dut_listbox.bind("<<ListboxSelect>>", self._on_dut_selected)

        dut_btns = ttk.Frame(left)
        dut_btns.pack(fill=tk.X)
        ttk.Button(
            dut_btns,
            text=self.locale.t("buttons.add_dut", default="+ Add Sensor"),
            command=self.action_add_dut,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            dut_btns,
            text=self.locale.t("buttons.remove_dut", default="- Remove"),
            command=self.action_remove_dut,
        ).pack(side=tk.LEFT, padx=2)
        pane.add(left, weight=1)

        right = ttk.Frame(pane)
        form = ttk.Frame(right)
        form.pack(fill=tk.X)

        self.dut_vars: dict[str, tk.Variable] = {
            "name": tk.StringVar(),
            "dut_ip": tk.StringVar(),
            "enabled": tk.BooleanVar(value=True),
            "poll_interval_ms": tk.StringVar(value="1000"),
            "mode": tk.StringVar(value="stub"),
            "version": tk.StringVar(value="v1"),
            "community": tk.StringVar(value=""),
            "port_number": tk.StringVar(value="131075"),
            "timeout_seconds": tk.StringVar(value="10"),
            "retries": tk.StringVar(value="2"),
            "security_level": tk.StringVar(value="single"),
            "security_username": tk.StringVar(),
            "auth_protocol": tk.StringVar(value="0"),
            "auth_passphrase": tk.StringVar(),
            "privacy_protocol": tk.StringVar(value="0"),
            "privacy_passphrase": tk.StringVar(),
        }

        fields = [
            (
                self.locale.t("labels.dut_name_colon", default="Sensor Name:"),
                "name",
                0,
                0,
            ),
            (
                self.locale.t("labels.host_ip_colon", default="Host / IP:"),
                "dut_ip",
                0,
                2,
            ),
            (
                self.locale.t("labels.poll_ms_colon", default="Poll ms:"),
                "poll_interval_ms",
                0,
                4,
            ),
            (
                self.locale.t("labels.snmp_mode_colon", default="PurpleAir Mode:"),
                "mode",
                1,
                0,
            ),
            (
                self.locale.t("labels.snmp_version_colon", default="API Version:"),
                "version",
                1,
                2,
            ),
            (
                self.locale.t("labels.community_colon", default="API Read Key:"),
                "community",
                1,
                4,
            ),
            (
                self.locale.t("labels.udp_port_colon", default="Sensor Index:"),
                "port_number",
                2,
                0,
            ),
            (
                self.locale.t("labels.timeout_colon", default="Timeout (s):"),
                "timeout_seconds",
                2,
                2,
            ),
            (
                self.locale.t("labels.retries_colon", default="Retries:"),
                "retries",
                2,
                4,
            ),
            (
                self.locale.t("labels.v3_seclevel_colon", default="Endpoint:"),
                "security_level",
                3,
                0,
            ),
            (
                self.locale.t("labels.v3_username_colon", default="Owner Key:"),
                "security_username",
                3,
                2,
            ),
            (
                self.locale.t("labels.v3_authproto_colon", default="Group ID:"),
                "auth_protocol",
                3,
                4,
            ),
            (
                self.locale.t("labels.v3_authpass_colon", default="API Write Key:"),
                "auth_passphrase",
                4,
                0,
            ),
            (
                self.locale.t("labels.v3_privproto_colon", default="Location Type:"),
                "privacy_protocol",
                4,
                2,
            ),
            (
                self.locale.t("labels.v3_privpass_colon", default="Member ID:"),
                "privacy_passphrase",
                4,
                4,
            ),
        ]
        for label_txt, key, r, c in fields:
            ttk.Label(form, text=label_txt).grid(
                row=r, column=c, sticky=tk.W, padx=4, pady=3
            )
            if key == "mode":
                w: tk.Widget = ttk.Combobox(
                    form,
                    textvariable=self.dut_vars[key],
                    values=["stub", "cloud", "local"],
                    width=14,
                    state="readonly",
                )
            elif key == "version":
                w = ttk.Combobox(
                    form,
                    textvariable=self.dut_vars[key],
                    values=["v1"],
                    width=14,
                    state="readonly",
                )
            elif key == "security_level":
                w = ttk.Combobox(
                    form,
                    textvariable=self.dut_vars[key],
                    values=["single", "multiple", "history", "local", "group"],
                    width=14,
                    state="readonly",
                )
            else:
                w = ttk.Entry(form, textvariable=self.dut_vars[key], width=16)
            w.grid(row=r, column=c + 1, sticky=tk.EW, padx=4, pady=3)

        chk_row = ttk.Frame(right)
        chk_row.pack(fill=tk.X, pady=4)
        ttk.Checkbutton(
            chk_row,
            text=self.locale.t("labels.dut_enabled_check", default="Sensor Enabled"),
            variable=self.dut_vars["enabled"],
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            chk_row,
            text=self.locale.t(
                "buttons.apply_dut_changes", default="Apply Sensor Changes to JSON"
            ),
            style="Accent.TButton",
            command=self.action_apply_dut,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(
            chk_row,
            text=self.locale.t(
                "buttons.probe_selected_dut", default="Probe This Sensor via CLI"
            ),
            command=self.action_probe_selected_dut,
        ).pack(side=tk.LEFT, padx=4)

        ttk.Label(
            right,
            text=self.locale.t(
                "sections.dut_polled_metrics",
                default="Sensor Polled Metrics (PurpleAir Fields):",
            ),
        ).pack(anchor=tk.W, pady=(8, 2))
        self.metrics_tree = ttk.Treeview(
            right,
            columns=("name", "oid", "op", "rep"),
            show="headings",
            height=8,
        )
        for col, title, width in [
            (
                "name",
                self.locale.t("table_headers.metric_name", default="Metric Name"),
                160,
            ),
            (
                "oid",
                self.locale.t(
                    "table_headers.oid_symbolic", default="PurpleAir Field Key"
                ),
                260,
            ),
            ("op", self.locale.t("table_headers.operation", default="Operation"), 90),
            (
                "rep",
                self.locale.t("table_headers.max_repeaters", default="Max Repeaters"),
                100,
            ),
        ]:
            self.metrics_tree.heading(col, text=title)
            self.metrics_tree.column(col, width=width)
        self.metrics_tree.pack(fill=tk.BOTH, expand=True)

        m_add = ttk.Frame(right)
        m_add.pack(fill=tk.X, pady=4)
        self.new_metric_name = tk.StringVar(value="pm2.5_atm")
        self.new_metric_oid = tk.StringVar(value="pm2.5_atm")
        self.new_metric_op = tk.StringVar(value="get")
        ttk.Label(
            m_add, text=self.locale.t("labels.metric_name_colon", default="Name:")
        ).pack(side=tk.LEFT)
        ttk.Entry(m_add, textvariable=self.new_metric_name, width=14).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Label(
            m_add, text=self.locale.t("labels.metric_oid_colon", default="Field:")
        ).pack(side=tk.LEFT)
        ttk.Entry(m_add, textvariable=self.new_metric_oid, width=22).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Combobox(
            m_add,
            textvariable=self.new_metric_op,
            values=["get", "single", "multiple", "history", "local"],
            width=10,
            state="readonly",
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            m_add,
            text=self.locale.t("buttons.add_metric", default="+ Add Metric"),
            command=self.action_add_metric,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            m_add,
            text=self.locale.t("buttons.remove_metric", default="- Delete Selected"),
            command=self.action_remove_metric,
        ).pack(side=tk.LEFT, padx=3)

        pane.add(right, weight=3)

    def _build_ezsnmp_studio_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(
            tab,
            text=self.locale.t(
                "tabs.ezsnmp_studio", default="3. PurpleAir Query / SET"
            ),
        )

        ctrl = ttk.Frame(tab)
        ctrl.pack(fill=tk.X, pady=(0, 8))

        self.req_dut_var = tk.StringVar()
        self.req_op_var = tk.StringVar(value="get")
        self.req_oid_var = tk.StringVar(value="pm2.5_atm, humidity, temperature")
        self.req_set_type_var = tk.StringVar(value="s")
        self.req_set_val_var = tk.StringVar(value="")
        self.req_record_var = tk.BooleanVar(value=False)

        ttk.Label(ctrl, text=self.locale.t("labels.dut_colon", default="Sensor:")).grid(
            row=0, column=0, sticky=tk.W, padx=4, pady=3
        )
        self.req_dut_combo = ttk.Combobox(
            ctrl, textvariable=self.req_dut_var, width=18, state="readonly"
        )
        self.req_dut_combo.grid(row=0, column=1, padx=4, pady=3)

        ttk.Label(
            ctrl, text=self.locale.t("labels.operation_colon", default="Operation:")
        ).grid(row=0, column=2, sticky=tk.W, padx=4, pady=3)
        ttk.Combobox(
            ctrl,
            textvariable=self.req_op_var,
            values=["get", "single", "multiple", "history", "local", "set"],
            width=12,
            state="readonly",
        ).grid(row=0, column=3, padx=4, pady=3)

        ttk.Label(
            ctrl,
            text=self.locale.t(
                "labels.oids_comma_sep", default="Field(s) (comma-sep):"
            ),
        ).grid(row=0, column=4, sticky=tk.W, padx=4, pady=3)
        ttk.Entry(ctrl, textvariable=self.req_oid_var, width=28).grid(
            row=0, column=5, padx=4, pady=3
        )

        ttk.Label(
            ctrl, text=self.locale.t("labels.set_type_colon", default="SET Type:")
        ).grid(row=1, column=0, sticky=tk.W, padx=4, pady=3)
        ttk.Combobox(
            ctrl,
            textvariable=self.req_set_type_var,
            values=["s", "i", "d"],
            width=8,
            state="readonly",
        ).grid(row=1, column=1, sticky=tk.W, padx=4, pady=3)

        ttk.Label(
            ctrl, text=self.locale.t("labels.set_value_colon", default="SET Value:")
        ).grid(row=1, column=2, sticky=tk.W, padx=4, pady=3)
        ttk.Entry(ctrl, textvariable=self.req_set_val_var, width=22).grid(
            row=1, column=3, columnspan=2, sticky=tk.EW, padx=4, pady=3
        )

        ttk.Checkbutton(
            ctrl,
            text=self.locale.t(
                "labels.persist_to_sinks_check",
                default="Also persist response to enabled sinks (--record)",
            ),
            variable=self.req_record_var,
        ).grid(row=1, column=5, sticky=tk.W, padx=4)

        ttk.Button(
            ctrl,
            text=self.locale.t("buttons.execute_via_cli", default="Execute via CLI"),
            style="Accent.TButton",
            command=self.action_execute_ezsnmp_request,
        ).grid(row=0, column=6, rowspan=2, padx=8)

        self.req_summary_var = tk.StringVar(
            value=self.locale.t(
                "status_bar.ready_ondemand",
                default="Ready to run on-demand PurpleAir request/set via CLI.",
            )
        )
        ttk.Label(tab, textvariable=self.req_summary_var).pack(anchor=tk.W, pady=(0, 4))

        self.req_tree = ttk.Treeview(
            tab,
            columns=("oid", "index", "snmp_type", "raw", "typed", "status"),
            show="headings",
        )
        for col, title, w in [
            ("oid", self.locale.t("table_headers.oid", default="Field"), 220),
            ("index", self.locale.t("table_headers.index", default="Sensor Index"), 90),
            (
                "snmp_type",
                self.locale.t("table_headers.snmp_type", default="Value Type"),
                110,
            ),
            (
                "raw",
                self.locale.t(
                    "table_headers.raw_value", default="Raw Value (purpleair_api)"
                ),
                240,
            ),
            (
                "typed",
                self.locale.t(
                    "table_headers.normalized_type", default="Normalized Type"
                ),
                110,
            ),
            ("status", self.locale.t("table_headers.status", default="Status"), 70),
        ]:
            self.req_tree.heading(col, text=title)
            self.req_tree.column(col, width=w)
        self.req_tree.pack(fill=tk.BOTH, expand=True)

    def _build_sinks_and_gui_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(
            tab,
            text=self.locale.t(
                "tabs.sinks_and_settings", default="4. Sinks & JSON Settings"
            ),
        )

        self.settings_vars: dict[str, tk.Variable] = {
            "poll_interval_ms": tk.StringVar(value="1000"),
            "queue_depth": tk.StringVar(value="4096"),
            "worker_threads": tk.StringVar(value="4"),
            "max_cycles": tk.StringVar(value="0"),
            "sqlite_enabled": tk.BooleanVar(value=True),
            "sqlite_path": tk.StringVar(value="./data/purpleair_demo.sqlite3"),
            "csv_enabled": tk.BooleanVar(value=False),
            "csv_dir": tk.StringVar(value="./data/csv"),
            "jsonl_enabled": tk.BooleanVar(value=False),
            "jsonl_dir": tk.StringVar(value="./data/jsonl"),
            "prom_enabled": tk.BooleanVar(value=False),
            "prom_port": tk.StringVar(value="9102"),
            "gui_frontend": tk.StringVar(value="auto"),
            "gui_theme": tk.StringVar(value=self.theme_name),
            "gui_locale": tk.StringVar(value=self.locale.locale),
            "gui_refresh_ms": tk.StringVar(value="1000"),
            "gui_port": tk.StringVar(value="8765"),
        }

        grid = ttk.Frame(tab)
        grid.pack(fill=tk.X)

        rows = [
            (
                self.locale.t(
                    "labels.logger_poll_interval",
                    default="Logger Poll Interval (ms):",
                ),
                "poll_interval_ms",
                0,
                0,
            ),
            (
                self.locale.t(
                    "labels.bounded_queue_depth", default="Bounded Queue Depth:"
                ),
                "queue_depth",
                0,
                2,
            ),
            (
                self.locale.t("labels.worker_threads", default="Worker Threads:"),
                "worker_threads",
                1,
                0,
            ),
            (
                self.locale.t(
                    "labels.max_cycles", default="Max Cycles (0=continuous):"
                ),
                "max_cycles",
                1,
                2,
            ),
            (
                self.locale.t("labels.sqlite3_path", default="SQLite3 Path:"),
                "sqlite_path",
                2,
                0,
            ),
            (
                self.locale.t("labels.csv_directory", default="CSV Directory:"),
                "csv_dir",
                3,
                0,
            ),
            (
                self.locale.t("labels.jsonl_directory", default="JSONL Directory:"),
                "jsonl_dir",
                4,
                0,
            ),
            (
                self.locale.t(
                    "labels.prometheus_port", default="Prometheus HTTP Port:"
                ),
                "prom_port",
                5,
                0,
            ),
            (
                self.locale.t(
                    "labels.gui_frontend", default="GUI Frontend (auto|tk|web):"
                ),
                "gui_frontend",
                6,
                0,
            ),
            (
                self.locale.t("labels.gui_theme", default="GUI Theme (dark|light):"),
                "gui_theme",
                6,
                2,
            ),
            (
                self.locale.t(
                    "labels.gui_locale", default="GUI Locale / Language (en|es):"
                ),
                "gui_locale",
                7,
                0,
            ),
            (
                self.locale.t("labels.web_studio_port", default="Web Studio Port:"),
                "gui_port",
                7,
                2,
            ),
            (
                self.locale.t("labels.gui_refresh", default="GUI Refresh (ms):"),
                "gui_refresh_ms",
                8,
                0,
            ),
        ]
        for lbl, key, r, c in rows:
            ttk.Label(grid, text=lbl).grid(row=r, column=c, sticky=tk.W, padx=6, pady=4)
            if key == "gui_frontend":
                w: tk.Widget = ttk.Combobox(
                    grid,
                    textvariable=self.settings_vars[key],
                    values=["auto", "tk", "web"],
                    width=18,
                    state="readonly",
                )
            elif key == "gui_theme":
                w = ttk.Combobox(
                    grid,
                    textvariable=self.settings_vars[key],
                    values=["dark", "light"],
                    width=18,
                    state="readonly",
                )
            elif key == "gui_locale":
                w = ttk.Combobox(
                    grid,
                    textvariable=self.settings_vars[key],
                    values=self.locale.supported_locales(),
                    width=18,
                    state="readonly",
                )
            else:
                w = ttk.Entry(grid, textvariable=self.settings_vars[key], width=24)
            w.grid(row=r, column=c + 1, sticky=tk.W, padx=6, pady=4)

        ttk.Checkbutton(
            grid,
            text=self.locale.t("labels.enable_sqlite3", default="Enable SQLite3 Sink"),
            variable=self.settings_vars["sqlite_enabled"],
        ).grid(row=2, column=2, sticky=tk.W, padx=6)
        ttk.Checkbutton(
            grid,
            text=self.locale.t("labels.enable_csv", default="Enable CSV Sink"),
            variable=self.settings_vars["csv_enabled"],
        ).grid(row=3, column=2, sticky=tk.W, padx=6)
        ttk.Checkbutton(
            grid,
            text=self.locale.t("labels.enable_jsonl", default="Enable JSONL Sink"),
            variable=self.settings_vars["jsonl_enabled"],
        ).grid(row=4, column=2, sticky=tk.W, padx=6)
        ttk.Checkbutton(
            grid,
            text=self.locale.t(
                "labels.enable_prometheus", default="Enable Prometheus Sink"
            ),
            variable=self.settings_vars["prom_enabled"],
        ).grid(row=5, column=2, sticky=tk.W, padx=6)

        ttk.Button(
            tab,
            text=self.locale.t(
                "buttons.save_settings",
                default="Save Runtime, Sink & GUI Settings to JSON",
            ),
            style="Accent.TButton",
            command=self.action_apply_settings_tab,
        ).pack(anchor=tk.W, pady=12)

    def _build_explorer_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(
            tab,
            text=self.locale.t("tabs.data_explorer", default="5. Data Explorer"),
        )

        bar = ttk.Frame(tab)
        bar.pack(fill=tk.X, pady=(0, 8))
        self.exp_dut_var = tk.StringVar()
        self.exp_metric_var = tk.StringVar()
        self.exp_limit_var = tk.StringVar(value="100")

        ttk.Label(
            bar, text=self.locale.t("labels.filter_dut_colon", default="Filter Sensor:")
        ).pack(side=tk.LEFT)
        ttk.Entry(bar, textvariable=self.exp_dut_var, width=16).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Label(
            bar,
            text=self.locale.t("labels.filter_metric_colon", default="Filter Metric:"),
        ).pack(side=tk.LEFT)
        ttk.Entry(bar, textvariable=self.exp_metric_var, width=16).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Label(bar, text=self.locale.t("labels.limit_colon", default="Limit:")).pack(
            side=tk.LEFT
        )
        ttk.Entry(bar, textvariable=self.exp_limit_var, width=8).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(
            bar,
            text=self.locale.t(
                "buttons.query_stored_samples",
                default="Query Stored Samples (CLI inspect)",
            ),
            style="Accent.TButton",
            command=self.action_inspect_sinks,
        ).pack(side=tk.LEFT, padx=8)

        self.inspect_tree = ttk.Treeview(
            tab,
            columns=("ts", "dut", "metric", "oid", "stype", "raw", "sink"),
            show="headings",
        )
        for col, title, w in [
            (
                "ts",
                self.locale.t("table_headers.timestamp_ns", default="Timestamp (ns)"),
                160,
            ),
            ("dut", self.locale.t("table_headers.dut", default="Sensor"), 130),
            ("metric", self.locale.t("table_headers.metric", default="Metric"), 140),
            ("oid", self.locale.t("table_headers.oid", default="Field"), 200),
            (
                "stype",
                self.locale.t("table_headers.snmp_type", default="Value Type"),
                100,
            ),
            ("raw", self.locale.t("table_headers.value", default="Value"), 220),
            ("sink", self.locale.t("table_headers.sink", default="Sink"), 80),
        ]:
            self.inspect_tree.heading(col, text=title)
            self.inspect_tree.column(col, width=w)
        self.inspect_tree.pack(fill=tk.BOTH, expand=True)

    def _build_json_tab(self) -> None:
        pal = PALETTES[self.theme_name]
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(
            tab,
            text=self.locale.t("tabs.raw_json_schema", default="6. Raw JSON & Schema"),
        )

        top = ttk.Frame(tab)
        top.pack(fill=tk.X, pady=(0, 6))
        self.tpl_var = tk.StringVar(value="demo")
        ttk.Label(
            top, text=self.locale.t("labels.template_colon", default="Template:")
        ).pack(side=tk.LEFT)
        ttk.Combobox(
            top,
            textvariable=self.tpl_var,
            values=["minimal", "demo", "enterprise", "local"],
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            top,
            text=self.locale.t("buttons.load_template", default="Load CLI Template"),
            command=self.action_load_template,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            top,
            text=self.locale.t(
                "buttons.validate_editor_json",
                default="Validate Editor JSON via CLI",
            ),
            command=self.action_validate_editor,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            top,
            text=self.locale.t("buttons.save_editor_json", default="Save Editor JSON"),
            style="Accent.TButton",
            command=self.action_save_editor_json,
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            top,
            text=self.locale.t("buttons.show_json_schema", default="Show JSON Schema"),
            command=self.action_show_schema,
        ).pack(side=tk.LEFT, padx=3)

        self.json_status_var = tk.StringVar(
            value=self.locale.t(
                "status_bar.all_config_stored_json",
                default="All configuration is stored in JSON.",
            )
        )
        ttk.Label(tab, textvariable=self.json_status_var).pack(anchor=tk.W, pady=(0, 4))

        self.json_editor = tk.Text(
            tab,
            bg=pal["card"],
            fg=pal["fg"],
            insertbackground=pal["fg"],
            font=("Courier", 11),
            undo=True,
        )
        self.json_editor.pack(fill=tk.BOTH, expand=True)

    # --- Synchronization Helpers ---

    def reload_from_disk(self) -> None:
        raw = self.bridge.load_config_text()
        self.config_doc = json.loads(raw)
        self.cfg_path_var.set(
            self.locale.t(
                "labels.json_config",
                default=f"JSON Config: {self.bridge.config_path}",
                path=self.bridge.config_path,
            )
        )

        self.json_editor.delete("1.0", tk.END)
        self.json_editor.insert("1.0", raw)

        duts = self.config_doc.get("duts", [])
        self.dut_listbox.delete(0, tk.END)
        dut_names: list[str] = []
        for d in duts:
            name = str(d.get("name", "unnamed"))
            dut_names.append(name)
            state_badge = "ON" if d.get("enabled", True) else "OFF"
            self.dut_listbox.insert(
                tk.END, f"[{state_badge}] {name} ({d.get('dut_ip', '')})"
            )

        self.req_dut_combo["values"] = dut_names
        if dut_names and not self.req_dut_var.get():
            self.req_dut_var.set(dut_names[0])

        if duts:
            idx = min(self._selected_dut_index, len(duts) - 1)
            self.dut_listbox.selection_set(idx)
            self._populate_dut_form(idx)

        lg = (
            self.config_doc.get("logger", {})
            if isinstance(self.config_doc.get("logger"), dict)
            else {}
        )
        self.settings_vars["poll_interval_ms"].set(
            str(lg.get("poll_interval_ms", 1000))
        )
        self.settings_vars["queue_depth"].set(
            str(self.config_doc.get("queue_capacity") or lg.get("queue_depth", 4096))
        )
        self.settings_vars["worker_threads"].set(str(lg.get("worker_threads", 4)))
        self.settings_vars["max_cycles"].set(
            str(self.config_doc.get("max_poll_cycles") or lg.get("max_cycles", 0))
        )

        self.settings_vars["sqlite_enabled"].set(False)
        self.settings_vars["csv_enabled"].set(False)
        self.settings_vars["jsonl_enabled"].set(False)
        self.settings_vars["prom_enabled"].set(False)
        raw_sinks = self.config_doc.get("sinks", {})
        if isinstance(raw_sinks, dict):
            sq = raw_sinks.get("sqlite") or raw_sinks.get("sqlite3") or {}
            if isinstance(sq, dict) and sq:
                self.settings_vars["sqlite_enabled"].set(bool(sq.get("enabled", True)))
                self.settings_vars["sqlite_path"].set(
                    str(sq.get("path", "./data/purpleair_demo.sqlite3"))
                )
            cs = raw_sinks.get("csv") or {}
            if isinstance(cs, dict) and cs:
                self.settings_vars["csv_enabled"].set(bool(cs.get("enabled", True)))
                self.settings_vars["csv_dir"].set(
                    str(cs.get("directory") or cs.get("dir", "./data/csv"))
                )
            jl = raw_sinks.get("jsonl") or {}
            if isinstance(jl, dict) and jl:
                self.settings_vars["jsonl_enabled"].set(bool(jl.get("enabled", True)))
                self.settings_vars["jsonl_dir"].set(
                    str(jl.get("directory") or jl.get("dir", "./data/jsonl"))
                )
            pr = raw_sinks.get("prometheus") or {}
            if isinstance(pr, dict) and pr:
                self.settings_vars["prom_enabled"].set(bool(pr.get("enabled", True)))
                self.settings_vars["prom_port"].set(str(pr.get("port", 9102)))

        gui = (
            self.config_doc.get("gui", {})
            if isinstance(self.config_doc.get("gui"), dict)
            else {}
        )
        self.settings_vars["gui_frontend"].set(str(gui.get("frontend", "auto")))
        self.settings_vars["gui_theme"].set(str(gui.get("theme", self.theme_name)))
        self.settings_vars["gui_locale"].set(
            str(gui.get("locale") or gui.get("language") or self.locale.locale)
        )
        self.settings_vars["gui_refresh_ms"].set(
            str(gui.get("refresh_interval_ms", 1000))
        )
        self.settings_vars["gui_port"].set(str(gui.get("port", 8765)))

    def _populate_dut_form(self, idx: int) -> None:
        duts = self.config_doc.get("duts", [])
        if idx < 0 or idx >= len(duts):
            return
        self._selected_dut_index = idx
        d = duts[idx]
        sc = d.get("purpleair") or d.get("snmp") or {}
        self.dut_vars["name"].set(str(d.get("name", "")))
        self.dut_vars["dut_ip"].set(str(d.get("dut_ip", "")))
        self.dut_vars["enabled"].set(bool(d.get("enabled", True)))
        self.dut_vars["poll_interval_ms"].set(str(d.get("poll_interval_ms", 1000)))
        self.dut_vars["mode"].set(str(sc.get("mode", "stub")))
        self.dut_vars["version"].set(str(sc.get("version", "v1")))
        self.dut_vars["community"].set(
            str(sc.get("api_read_key") or sc.get("community", ""))
        )
        self.dut_vars["port_number"].set(
            str(
                sc.get("sensor_index")
                or sc.get("port_number")
                or sc.get("port", 131075)
            )
        )
        self.dut_vars["timeout_seconds"].set(str(sc.get("timeout_seconds", 10)))
        self.dut_vars["retries"].set(str(sc.get("retries", 2)))
        self.dut_vars["security_level"].set(
            str(sc.get("endpoint") or sc.get("security_level", "single"))
        )
        self.dut_vars["security_username"].set(
            str(sc.get("owner_key") or sc.get("security_username", ""))
        )
        self.dut_vars["auth_protocol"].set(
            str(sc.get("group_id") or sc.get("auth_protocol", "0"))
        )
        self.dut_vars["auth_passphrase"].set(
            str(sc.get("api_write_key") or sc.get("auth_passphrase", ""))
        )
        self.dut_vars["privacy_protocol"].set(
            str(sc.get("location_type") or sc.get("privacy_protocol", "0"))
        )
        self.dut_vars["privacy_passphrase"].set(
            str(sc.get("member_id") or sc.get("privacy_passphrase", ""))
        )

        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)
        for m in d.get("metrics", []):
            self.metrics_tree.insert(
                "",
                tk.END,
                values=(
                    m.get("name", ""),
                    m.get("field") or m.get("oid", ""),
                    m.get("operation", "get"),
                    m.get("max_repeaters", 25),
                ),
            )

    def _on_dut_selected(self, _event: Any = None) -> None:
        sel = self.dut_listbox.curselection()
        if sel:
            self._populate_dut_form(int(sel[0]))

    # --- Actions (Every action goes through CliSubprocessBridge!) ---

    def action_open_config(self) -> None:
        chosen = filedialog.askopenfilename(
            title=self.locale.t(
                "dialogs.open_config_title",
                default="Open purpleair_data_logger JSON Config",
            ),
            filetypes=[
                (
                    self.locale.t(
                        "dialogs.filetype_json", default="JSON Configuration"
                    ),
                    "*.json",
                ),
                (self.locale.t("dialogs.filetype_all", default="All Files"), "*.*"),
            ],
        )
        if chosen:
            self.bridge.stop_run()
            self.bridge = CliSubprocessBridge(chosen)
            self.reload_from_disk()

    def action_save_all(self) -> None:
        res = self.bridge.save_config_dict(self.config_doc)
        self.reload_from_disk()
        self._update_audit_banner(res.get("audit"))

    def action_start_run(self) -> None:
        res = self.bridge.start_run()
        self._update_audit_banner(res.get("audit"))
        self.refresh_live_state(reschedule=False)

    def action_stop_run(self) -> None:
        res = self.bridge.stop_run()
        self._update_audit_banner(res.get("audit"))
        self.refresh_live_state(reschedule=False)

    def action_run_once(self) -> None:
        res = self.bridge.run_once()
        self._update_audit_banner(res.get("audit"))
        self.refresh_live_state(reschedule=False)

    def action_probe_all(self) -> None:
        res = self.bridge.probe()
        self._update_audit_banner(res.get("audit"))
        if res.get("data"):
            self.notebook.select(2)
            self._populate_request_results_from_probe(res["data"])

    def action_probe_selected_dut(self) -> None:
        dut_name = str(self.dut_vars["name"].get()).strip()
        res = self.bridge.probe(dut_name=dut_name)
        self._update_audit_banner(res.get("audit"))
        if res.get("data"):
            self.notebook.select(2)
            self._populate_request_results_from_probe(res["data"])

    def _populate_request_results_from_probe(
        self, probe_payload: dict[str, Any]
    ) -> None:
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)
        total_samples = 0
        for r in probe_payload.get("results", []):
            for s in r.get("samples", []):
                total_samples += 1
                self.req_tree.insert(
                    "",
                    tk.END,
                    values=(
                        s.get("oid", ""),
                        s.get("oid_index", ""),
                        s.get("snmp_type", ""),
                        s.get("raw_value", ""),
                        s.get("type_name", ""),
                        s.get("status", 0),
                    ),
                )
        self.req_summary_var.set(
            self.locale.t(
                "status_bar.probe_summary",
                default=f"CLI probe completed across {probe_payload.get('count', 0)} sensor(s) -> {total_samples} sample(s).",
                count=probe_payload.get("count", 0),
                total=total_samples,
            )
        )

    def action_validate_saved(self) -> None:
        res = self.bridge.validate()
        self._update_audit_banner(res.get("audit"))
        rep = res.get("data") or {}
        if rep.get("valid"):
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.validation_passed",
                    default=f"CLI Validation PASSED ({rep.get('enabled_duts', 0)} sensors, {rep.get('enabled_sinks', 0)} sinks).",
                    duts=rep.get("enabled_duts", 0),
                    sinks=rep.get("enabled_sinks", 0),
                )
            )
        else:
            errs = "; ".join(
                rep.get("errors", [res.get("stderr", "Validation failed")])
            )
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.validation_failed",
                    default=f"CLI Validation FAILED: {errs}",
                    errors=errs,
                )
            )

    def action_add_dut(self) -> None:
        duts = self.config_doc.setdefault("duts", [])
        new_name = f"sensor-{len(duts) + 1}"
        duts.append(
            {
                "name": new_name,
                "dut_ip": "127.0.0.1",
                "enabled": True,
                "poll_interval_ms": 1000,
                "purpleair": {
                    "mode": "stub",
                    "version": "v1",
                    "api_read_key": "",
                    "sensor_index": 131075,
                },
                "metrics": [
                    {"name": "pm2.5_atm", "field": "pm2.5_atm", "operation": "get"},
                    {"name": "humidity", "field": "humidity", "operation": "get"},
                ],
            }
        )
        self._selected_dut_index = len(duts) - 1
        self.action_save_all()

    def action_remove_dut(self) -> None:
        duts = self.config_doc.get("duts", [])
        if not duts or self._selected_dut_index >= len(duts):
            return
        duts.pop(self._selected_dut_index)
        self._selected_dut_index = max(0, self._selected_dut_index - 1)
        self.action_save_all()

    def action_apply_dut(self) -> None:
        duts = self.config_doc.setdefault("duts", [])
        if not duts or self._selected_dut_index >= len(duts):
            return
        d = duts[self._selected_dut_index]
        d["name"] = str(self.dut_vars["name"].get()).strip()
        d["dut_ip"] = str(self.dut_vars["dut_ip"].get()).strip()
        d["enabled"] = bool(self.dut_vars["enabled"].get())
        d["poll_interval_ms"] = max(
            1, int(self.dut_vars["poll_interval_ms"].get() or 1000)
        )
        sc_key = "snmp" if "snmp" in d and "purpleair" not in d else "purpleair"
        sc = d.setdefault(sc_key, {})
        sc["mode"] = str(self.dut_vars["mode"].get())
        sc["version"] = str(self.dut_vars["version"].get())
        sc["api_read_key"] = str(self.dut_vars["community"].get())
        sc["sensor_index"] = int(self.dut_vars["port_number"].get() or 131075)
        sc["timeout_seconds"] = int(self.dut_vars["timeout_seconds"].get() or 10)
        sc["retries"] = int(self.dut_vars["retries"].get() or 2)
        sc["endpoint"] = str(self.dut_vars["security_level"].get())
        sc["owner_key"] = str(self.dut_vars["security_username"].get())
        sc["api_write_key"] = str(self.dut_vars["auth_passphrase"].get())
        self.action_save_all()

    def action_add_metric(self) -> None:
        duts = self.config_doc.get("duts", [])
        if not duts or self._selected_dut_index >= len(duts):
            return
        metrics = duts[self._selected_dut_index].setdefault("metrics", [])
        metrics.append(
            {
                "name": self.new_metric_name.get().strip(),
                "field": self.new_metric_oid.get().strip(),
                "oid": self.new_metric_oid.get().strip(),
                "operation": self.new_metric_op.get().strip() or "get",
                "max_repeaters": 25,
            }
        )
        self.action_save_all()

    def action_remove_metric(self) -> None:
        duts = self.config_doc.get("duts", [])
        if not duts or self._selected_dut_index >= len(duts):
            return
        sel = self.metrics_tree.selection()
        if not sel:
            return
        idx = self.metrics_tree.index(sel[0])
        metrics = duts[self._selected_dut_index].get("metrics", [])
        if 0 <= idx < len(metrics):
            metrics.pop(idx)
            self.action_save_all()

    def action_execute_ezsnmp_request(self) -> None:
        dut = self.req_dut_var.get().strip()
        op = self.req_op_var.get().strip()
        raw_oids = [x.strip() for x in self.req_oid_var.get().split(",") if x.strip()]
        record = bool(self.req_record_var.get())

        if not dut or not raw_oids:
            self.req_summary_var.set(
                self.locale.t(
                    "dialogs.select_dut_and_oid",
                    default="Select a Sensor and specify at least one Field.",
                )
            )
            return

        if op == "set":
            res = self.bridge.set_oid(
                dut_name=dut,
                oid=raw_oids[0],
                set_type=self.req_set_type_var.get().strip() or "s",
                value=self.req_set_val_var.get(),
                record=record,
            )
        else:
            res = self.bridge.request(
                dut_name=dut, operation=op, oids=raw_oids, record=record
            )

        self._update_audit_banner(res.get("audit"))
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)

        payload = res.get("data") or {}
        if not res["ok"]:
            err_msg = (
                payload.get("error") or res.get("stderr", "CLI request failed").strip()
            )
            self.req_summary_var.set(
                self.locale.t(
                    "status_bar.ezsnmp_error",
                    default=f"Error: {err_msg}",
                    error=err_msg,
                )
            )
            return

        samples = payload.get("samples", [])
        for s in samples:
            self.req_tree.insert(
                "",
                tk.END,
                values=(
                    s.get("oid", ""),
                    s.get("oid_index", ""),
                    s.get("snmp_type", ""),
                    s.get("raw_value", ""),
                    s.get("type_name", ""),
                    s.get("status", 0),
                ),
            )
        self.req_summary_var.set(
            self.locale.t(
                "status_bar.ezsnmp_ok",
                default=f"OK: {op.upper()} on {dut} returned {len(samples)} sample(s) in {payload.get('latency_ms', 0):.2f} ms.",
                op=op.upper(),
                dut=dut,
                samples=len(samples),
                ms=payload.get("latency_ms", 0.0),
            )
        )

    def action_apply_settings_tab(self) -> None:
        self.config_doc["queue_capacity"] = int(
            self.settings_vars["queue_depth"].get() or 4096
        )
        self.config_doc["max_poll_cycles"] = int(
            self.settings_vars["max_cycles"].get() or 0
        )

        existing_sinks = self.config_doc.get("sinks", {})
        new_sinks: dict[str, Any] = {
            "sqlite": {
                "enabled": bool(self.settings_vars["sqlite_enabled"].get()),
                "path": str(self.settings_vars["sqlite_path"].get()),
                "batch_commit_size": 32,
                "busy_timeout_ms": 5000,
                "wal_mode": True,
            },
            "csv": {
                "enabled": bool(self.settings_vars["csv_enabled"].get()),
                "directory": str(self.settings_vars["csv_dir"].get()),
                "file_prefix": "purpleair_samples",
                "flush_every_batch": True,
            },
            "jsonl": {
                "enabled": bool(self.settings_vars["jsonl_enabled"].get()),
                "directory": str(self.settings_vars["jsonl_dir"].get()),
                "file_prefix": "purpleair_batches",
                "flush_every_batch": True,
            },
            "prometheus": {
                "enabled": bool(self.settings_vars["prom_enabled"].get()),
                "bind_host": "127.0.0.1",
                "port": int(self.settings_vars["prom_port"].get() or 9102),
                "namespace_prefix": "purpleair_logger",
            },
        }
        if isinstance(existing_sinks, dict) and "psql" in existing_sinks:
            new_sinks["psql"] = existing_sinks["psql"]
        self.config_doc["sinks"] = new_sinks

        gui = self.config_doc.setdefault("gui", {})
        gui["frontend"] = str(self.settings_vars["gui_frontend"].get())
        gui["theme"] = str(self.settings_vars["gui_theme"].get())
        gui["locale"] = str(self.settings_vars["gui_locale"].get()).strip().lower()
        gui["refresh_interval_ms"] = int(
            self.settings_vars["gui_refresh_ms"].get() or 1000
        )
        gui["port"] = int(self.settings_vars["gui_port"].get() or 8765)

        if gui["locale"] and gui["locale"] != self.locale.locale:
            self.locale.set_locale(gui["locale"])

        if gui["theme"] != self.theme_name:
            self.theme_name = "light" if gui["theme"] == "light" else "dark"
            self._apply_style()

        self.refresh_ms = max(250, int(gui["refresh_interval_ms"]))
        self.action_save_all()

    def action_inspect_sinks(self) -> None:
        res = self.bridge.inspect(
            limit=int(self.exp_limit_var.get() or 50),
            dut=self.exp_dut_var.get().strip(),
            metric=self.exp_metric_var.get().strip(),
        )
        self._update_audit_banner(res.get("audit"))
        for item in self.inspect_tree.get_children():
            self.inspect_tree.delete(item)
        payload = res.get("data") or {}
        for r in payload.get("rows", []):
            self.inspect_tree.insert(
                "",
                tk.END,
                values=(
                    r.get("ts_unix_ns") or r.get("timestamp_ns", 0),
                    r.get("dut_name", ""),
                    r.get("metric_name", ""),
                    r.get("oid", ""),
                    r.get("snmp_type", ""),
                    r.get("raw_value", "")
                    or r.get("str_val", "")
                    or r.get("value", ""),
                    r.get("sink_type", ""),
                ),
            )

    def action_load_template(self) -> None:
        res = self.bridge.init_config_template(self.tpl_var.get())
        self._update_audit_banner(res.get("audit"))
        if res["ok"] and res["stdout"].strip():
            self.json_editor.delete("1.0", tk.END)
            self.json_editor.insert("1.0", res["stdout"])
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.template_loaded",
                    default=f"Loaded '{self.tpl_var.get()}' template from CLI — click 'Save Editor JSON' to apply.",
                    template=self.tpl_var.get(),
                )
            )

    def action_validate_editor(self) -> None:
        raw = self.json_editor.get("1.0", tk.END)
        res = self.bridge.validate(config_text=raw)
        self._update_audit_banner(res.get("audit"))
        rep = res.get("data") or {}
        if rep.get("valid"):
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.validation_passed",
                    default=f"CLI Validation PASSED ({rep.get('enabled_duts', 0)} sensors, {rep.get('enabled_sinks', 0)} sinks).",
                    duts=rep.get("enabled_duts", 0),
                    sinks=rep.get("enabled_sinks", 0),
                )
            )
        else:
            errs = "; ".join(rep.get("errors", [res.get("stderr", "Invalid JSON")]))
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.validation_failed",
                    default=f"CLI Validation FAILED: {errs}",
                    errors=errs,
                )
            )

    def action_save_editor_json(self) -> None:
        raw = self.json_editor.get("1.0", tk.END)
        try:
            res = self.bridge.save_config_text(raw)
        except Exception as exc:
            messagebox.showerror(
                self.locale.t(
                    "dialogs.invalid_json_title", default="Invalid JSON Syntax"
                ),
                str(exc),
                parent=self.root,
            )
            return
        self._update_audit_banner(res.get("audit"))
        self.reload_from_disk()
        rep = res.get("data") or {}
        if rep.get("valid"):
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.saved_json_valid",
                    default="Saved JSON configuration and verified VALID via CLI.",
                )
            )
        else:
            errs = "; ".join(rep.get("errors", []))
            self.json_status_var.set(
                self.locale.t(
                    "status_bar.saved_json_invalid",
                    default=f"Saved JSON with validation errors: {errs}",
                    errors=errs,
                )
            )

    def action_show_schema(self) -> None:
        res = self.bridge.schema()
        self._update_audit_banner(res.get("audit"))
        if res["ok"]:
            win = tk.Toplevel(self.root)
            win.title(
                self.locale.t(
                    "app.schema_title",
                    default="JSON Schema (Draft 2020-12) — CLI `schema`",
                )
            )
            win.geometry("760x580")
            txt = tk.Text(win, font=("Courier", 10))
            txt.pack(fill=tk.BOTH, expand=True)
            txt.insert("1.0", res["stdout"])
            txt.configure(state=tk.DISABLED)

    def _update_audit_banner(self, audit: dict[str, Any] | None) -> None:
        if not audit:
            return
        rc = audit.get("exit_code")
        rc_str = "running" if rc is None else str(rc)
        self.audit_status_var.set(
            self.locale.t(
                "status_bar.last_command",
                default=f"Last CLI Command [{rc_str}, {audit.get('duration_ms', 0)} ms]: {audit.get('command', '')}",
                exit_code=rc_str,
                duration_ms=audit.get("duration_ms", 0),
                command=audit.get("command", ""),
            )
        )

    def action_select_all_series(self) -> None:
        """Select all available series for plotting."""
        self._user_modified_series = True
        for var in self._series_vars.values():
            var.set(True)
        self._draw_chart(self._last_series_map)

    def action_clear_all_series(self) -> None:
        """Deselect all series from plotting."""
        self._user_modified_series = True
        for var in self._series_vars.values():
            var.set(False)
        self._draw_chart(self._last_series_map)

    def _on_series_toggle(self) -> None:
        """Callback when a series checkbutton is toggled."""
        self._user_modified_series = True
        self._draw_chart(self._last_series_map)

    def _on_canvas_click(self, event: tk.Event[Any]) -> None:
        """Toggle a series when clicked in the canvas legend."""
        x, y = event.x, event.y
        for x1, y1, x2, y2, s_name in self._legend_hitboxes:
            if x1 <= x <= x2 and y1 <= y <= y2:
                var = self._series_vars.get(s_name)
                if var is not None:
                    self._user_modified_series = True
                    var.set(not var.get())
                    self._draw_chart(self._last_series_map)
                break

    def _draw_chart(self, series_map: dict[str, list[dict[str, Any]]]) -> None:
        self._last_series_map = series_map or {}
        pal = PALETTES[self.theme_name]
        c = self.chart_canvas
        c.delete("all")
        self._legend_hitboxes.clear()

        all_series = list(self._last_series_map.keys())
        for s_name in all_series:
            if s_name not in self._series_vars:
                var = tk.BooleanVar(
                    value=True if not self._user_modified_series else False
                )
                self._series_vars[s_name] = var
                cb = ttk.Checkbutton(
                    self.series_selector_frame,
                    text=f"● {s_name}",
                    variable=var,
                    command=self._on_series_toggle,
                )
                cb.pack(side=tk.LEFT, padx=4)
                self._series_cbs[s_name] = cb

        w = max(320, c.winfo_width())
        h = max(140, c.winfo_height())

        pad_l, pad_r, pad_t, pad_b = 54, 20, 26, 24
        plot_w = max(40, w - pad_l - pad_r)
        plot_h = max(40, h - pad_t - pad_b)

        for i in range(5):
            y = pad_t + (plot_h * i) / 4.0
            c.create_line(pad_l, y, pad_l + plot_w, y, fill=pal["border"], dash=(2, 4))

        non_empty = [(k, pts) for k, pts in self._last_series_map.items() if pts]
        if not non_empty:
            c.create_text(
                w / 2,
                h / 2,
                text=self.locale.t(
                    "status_bar.chart_empty",
                    default="Start CLI Logger or click 'Run Single Cycle' to stream real-time PurpleAir series",
                ),
                fill=pal["muted"],
            )
            return

        active_series = [
            (k, pts)
            for k, pts in non_empty
            if self._series_vars.get(k, tk.BooleanVar(value=True)).get()
        ]

        legend_x = pad_l
        for idx, (series_name, _pts) in enumerate(non_empty):
            is_active = self._series_vars.get(
                series_name, tk.BooleanVar(value=True)
            ).get()
            color = (
                SERIES_COLORS[idx % len(SERIES_COLORS)] if is_active else pal["muted"]
            )
            icon_mark = "●" if is_active else "○"
            item_id = c.create_text(
                legend_x,
                10,
                text=f"{icon_mark} {series_name}",
                anchor=tk.W,
                fill=color,
                font=("TkDefaultFont", 9, "bold" if is_active else "normal"),
            )
            bbox = c.bbox(item_id)
            if bbox:
                self._legend_hitboxes.append(
                    (bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2, series_name)
                )
            legend_x += min(210, len(series_name) * 7 + 28)

        if not active_series:
            c.create_text(
                w / 2,
                h / 2,
                text=self.locale.t(
                    "status_bar.no_series_selected",
                    default="No series selected. Select one or more fields above to view telemetry.",
                ),
                fill=pal["muted"],
            )
            return

        all_vals = [float(p["value"]) for _, pts in active_series for p in pts]
        vmin = min(all_vals)
        vmax = max(all_vals)
        if abs(vmax - vmin) < 1e-9:
            vmin -= 1.0
            vmax += 1.0

        c.create_text(
            pad_l - 6,
            pad_t,
            text=f"{vmax:.1f}",
            anchor=tk.E,
            fill=pal["muted"],
            font=("Courier", 8),
        )
        c.create_text(
            pad_l - 6,
            pad_t + plot_h,
            text=f"{vmin:.1f}",
            anchor=tk.E,
            fill=pal["muted"],
            font=("Courier", 8),
        )

        for series_name, pts in active_series:
            orig_idx = [k for k, _ in non_empty].index(series_name)
            color = SERIES_COLORS[orig_idx % len(SERIES_COLORS)]

            if len(pts) == 1:
                y = pad_t + plot_h - ((pts[0]["value"] - vmin) / (vmax - vmin)) * plot_h
                c.create_oval(
                    pad_l + plot_w / 2 - 3,
                    y - 3,
                    pad_l + plot_w / 2 + 3,
                    y + 3,
                    fill=color,
                    outline="",
                )
                continue

            coords: list[float] = []
            span = max(1, len(pts) - 1)
            for p_idx, pt in enumerate(pts):
                x = pad_l + (p_idx / span) * plot_w
                y = (
                    pad_t
                    + plot_h
                    - ((float(pt["value"]) - vmin) / (vmax - vmin)) * plot_h
                )
                coords.extend([x, y])
            c.create_line(*coords, fill=color, width=2, smooth=False)

    def refresh_live_state(self, reschedule: bool = True) -> None:
        snap = self.bridge.snapshot()
        st = snap["stats"]
        self.kpi_vars["state"].set("RUNNING" if snap["running"] else "IDLE")
        self.kpi_vars["cycles"].set(
            str(st.get("cycles_completed") or st.get("batches_polled", 0))
        )
        self.kpi_vars["batches"].set(
            str(st.get("processed_batches") or st.get("batches_written", 0))
        )
        self.kpi_vars["samples"].set(
            str(st.get("processed_samples") or st.get("samples_written", 0))
        )
        self.kpi_vars["queue"].set(str(st.get("queue_depth", 0)))
        self.kpi_vars["errors"].set(
            f"{st.get('poll_errors', 0)} / {st.get('sink_errors', 0)}"
        )

        self._draw_chart(snap.get("series", {}))

        lines = snap.get("cli_lines", [])
        self.cli_log_text.delete("1.0", tk.END)
        if lines:
            self.cli_log_text.insert("1.0", "\n".join(lines[-40:]))
            self.cli_log_text.see(tk.END)

        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
        for entry in snap.get("audit", [])[:30]:
            ts_short = str(entry.get("timestamp", ""))[11:19]
            rc = entry.get("exit_code")
            self.audit_tree.insert(
                "",
                tk.END,
                values=(
                    ts_short,
                    "..." if rc is None else rc,
                    entry.get("duration_ms", 0),
                    entry.get("command", ""),
                ),
            )

        if reschedule:
            self._after_id = self.root.after(self.refresh_ms, self.refresh_live_state)

    def on_close(self) -> None:
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self.bridge.stop_run()
        self.root.destroy()


def launch_desktop_gui(
    bridge: CliSubprocessBridge,
    locale_mgr: LocaleManager | None = None,
) -> int:
    """Launch the cross-platform tkinter.ttk Desktop Studio mainloop."""
    studio = DesktopLoggerStudio(bridge, schedule_refresh=True, locale_mgr=locale_mgr)
    studio.root.mainloop()
    return 0
