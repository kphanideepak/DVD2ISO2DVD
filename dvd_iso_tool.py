#!/usr/bin/env python3
"""
DVD to ISO Converter Tool
Phase 1: Convert DVD to ISO
Phase 2 (planned): Burn ISO to DVD

Copyright (c) 2025 Phanideepak K - kalluriit.com.au

DISCLAIMER: This software is provided for personal backup purposes only.
Users are responsible for ensuring their use complies with applicable
copyright laws in their jurisdiction. The author assumes no liability
for misuse of this software.
"""

__version__ = "1.2.0"
__author__ = "Phanideepak K"
__website__ = "https://kalluriit.com.au"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import platform
import re
import webbrowser
from datetime import datetime


class Style:
    """Clean, professional color scheme."""
    
    # Colors
    BG = "#f5f5f5"
    CARD = "#ffffff"
    INPUT_BG = "#fafafa"
    
    PRIMARY = "#2e7d32"       # Green
    PRIMARY_HOVER = "#1b5e20"
    DANGER = "#c62828"
    
    BORDER = "#e0e0e0"
    
    TEXT = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_LIGHT = "#9e9e9e"
    WHITE = "#ffffff"
    
    # Log colors
    LOG_BG = "#fafafa"
    LOG_INFO = "#424242"
    LOG_SUCCESS = "#2e7d32"
    LOG_WARNING = "#f57c00"
    LOG_ERROR = "#c62828"
    
    # Fonts
    FONT = "Segoe UI"
    TITLE = (FONT, 18, "bold")
    HEADING = (FONT, 11, "bold")
    BODY = (FONT, 10)
    SMALL = (FONT, 9)
    MONO = ("Consolas", 9)


class DVDtoISOConverter:
    def __init__(self, root):
        self.root = root
        self.s = Style()
        
        # Variables
        self.source_drive = tk.StringVar()
        self.output_path = tk.StringVar()
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        self.is_converting = False
        self.process = None
        self.start_time = None

        # New Phase 1 enhancements
        self.log_level = tk.IntVar(value=1)  # 1=Normal, 2=Verbose, 3=Debug
        self.verify_after = tk.BooleanVar(value=False)
        self.auto_eject = tk.BooleanVar(value=False)
        self.bytes_copied = 0
        self.total_bytes = 0
        self.last_speed_time = None
        self.last_speed_bytes = 0
        self.current_speed = 0
        self.disc_info_var = tk.StringVar(value="")
        self.elapsed_timer_id = None  # For independent elapsed time updates
        self.activity_counter = 0  # For activity indicator animation

        # ISO to USB mode variables
        self.current_mode = tk.StringVar(value="dvd_to_iso")  # or "iso_to_usb"
        self.iso_source_path = tk.StringVar()
        self.target_usb = tk.StringVar()
        self.boot_mode = tk.StringVar(value="both")  # "both", "uefi", "bios"
        self.iso_type_var = tk.StringVar(value="")
        self.usb_info_var = tk.StringVar(value="")
        self.detected_iso_type = None  # "windows", "linux_hybrid", "unknown"
        
        self.setup_window()
        self.create_ui()
        self.root.after(100, self.detect_drives)
    
    def setup_window(self):
        """Configure window."""
        self.root.title("DVD & ISO Tool")
        self.root.configure(bg=self.s.BG)
        
        # DPI awareness
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    def create_ui(self):
        """Build the UI."""
        s = self.s

        # Main frame
        self.main = tk.Frame(self.root, bg=s.BG)
        self.main.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Configure grid weights for proper expansion
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(4, weight=1)  # Log section expands (row 4)

        # === HEADER ===
        header = tk.Frame(self.main, bg=s.BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(header, text="💿", font=(s.FONT, 24), bg=s.BG, fg=s.PRIMARY).pack(side=tk.LEFT, padx=(0, 12))

        title_area = tk.Frame(header, bg=s.BG)
        title_area.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(title_area, text="DVD & ISO Tool", font=s.TITLE, bg=s.BG, fg=s.TEXT).pack(anchor="w")

        subtitle_row = tk.Frame(title_area, bg=s.BG)
        subtitle_row.pack(anchor="w")
        tk.Label(subtitle_row, text="Create backups and bootable drives", font=s.SMALL, bg=s.BG, fg=s.TEXT_SECONDARY).pack(side=tk.LEFT)
        tk.Label(subtitle_row, text=" • ", font=s.SMALL, bg=s.BG, fg=s.TEXT_LIGHT).pack(side=tk.LEFT)
        website_link = tk.Label(subtitle_row, text="kalluriit.com.au", font=s.SMALL, bg=s.BG, fg=s.PRIMARY, cursor="hand2")
        website_link.pack(side=tk.LEFT)
        website_link.bind("<Button-1>", lambda e: webbrowser.open(__website__))
        website_link.bind("<Enter>", lambda e: website_link.configure(font=(s.FONT, 9, "underline")))
        website_link.bind("<Leave>", lambda e: website_link.configure(font=s.SMALL))

        # Version badge
        tk.Label(header, text=f"v{__version__}", font=s.SMALL, bg=s.BG, fg=s.TEXT_LIGHT).pack(side=tk.RIGHT)

        # === MODE SELECTOR ===
        mode_frame = tk.Frame(self.main, bg=s.BG)
        mode_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.dvd_to_iso_btn = tk.Button(mode_frame, text="📀 DVD → ISO", font=(s.FONT, 10, "bold"),
                                        bg=s.PRIMARY, fg=s.WHITE, activebackground=s.PRIMARY_HOVER,
                                        activeforeground=s.WHITE, relief=tk.FLAT, pady=8, padx=20,
                                        cursor="hand2", command=lambda: self.switch_mode("dvd_to_iso"))
        self.dvd_to_iso_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.iso_to_usb_btn = tk.Button(mode_frame, text="💾 ISO → USB", font=(s.FONT, 10, "bold"),
                                        bg=s.BORDER, fg=s.TEXT, activebackground=s.PRIMARY,
                                        activeforeground=s.WHITE, relief=tk.FLAT, pady=8, padx=20,
                                        cursor="hand2", command=lambda: self.switch_mode("iso_to_usb"))
        self.iso_to_usb_btn.pack(side=tk.LEFT)

        # === CONTENT AREA (mode-specific) ===
        self.content_frame = tk.Frame(self.main, bg=s.BG)
        self.content_frame.grid(row=2, column=0, sticky="ew")

        # Create both mode panels (will show/hide)
        self.dvd_to_iso_panel = tk.Frame(self.content_frame, bg=s.BG)
        self.iso_to_usb_panel = tk.Frame(self.content_frame, bg=s.BG)

        self._create_dvd_to_iso_panel()
        self._create_iso_to_usb_panel()

        # Show DVD→ISO by default
        self.dvd_to_iso_panel.pack(fill=tk.X)

        # === PROGRESS ===
        prog_card = self.make_card(self.main, row=3)
        self.make_card_header(prog_card, "Progress", None)

        prog_info = tk.Frame(prog_card, bg=s.CARD)
        prog_info.pack(fill=tk.X, padx=15)

        self.status_label = tk.Label(prog_info, textvariable=self.status_var, font=s.BODY, bg=s.CARD, fg=s.TEXT_SECONDARY)
        self.status_label.pack(side=tk.LEFT)

        self.percent_label = tk.Label(prog_info, text="0%", font=(s.FONT, 11, "bold"), bg=s.CARD, fg=s.PRIMARY)
        self.percent_label.pack(side=tk.RIGHT)

        prog_bar_bg = tk.Frame(prog_card, bg=s.BORDER, height=6)
        prog_bar_bg.pack(fill=tk.X, padx=15, pady=(6, 4))
        prog_bar_bg.pack_propagate(False)

        self.prog_fill = tk.Frame(prog_bar_bg, bg=s.PRIMARY, width=0)
        self.prog_fill.place(x=0, y=0, relheight=1)
        self.prog_bar_bg = prog_bar_bg

        # Speed, ETA, and bytes info row
        speed_eta_row = tk.Frame(prog_card, bg=s.CARD)
        speed_eta_row.pack(fill=tk.X, padx=15, pady=(4, 0))

        self.speed_label = tk.Label(speed_eta_row, text="", font=s.SMALL, bg=s.CARD, fg=s.TEXT_SECONDARY)
        self.speed_label.pack(side=tk.LEFT)

        self.eta_label = tk.Label(speed_eta_row, text="", font=s.SMALL, bg=s.CARD, fg=s.TEXT_SECONDARY)
        self.eta_label.pack(side=tk.RIGHT)

        # Elapsed time and bytes copied row
        time_bytes_row = tk.Frame(prog_card, bg=s.CARD)
        time_bytes_row.pack(fill=tk.X, padx=15, pady=(2, 10))

        self.time_label = tk.Label(time_bytes_row, text="", font=s.SMALL, bg=s.CARD, fg=s.TEXT_LIGHT)
        self.time_label.pack(side=tk.LEFT)

        self.bytes_label = tk.Label(time_bytes_row, text="", font=s.SMALL, bg=s.CARD, fg=s.TEXT_LIGHT)
        self.bytes_label.pack(side=tk.RIGHT)

        # === LOG ===
        log_card = self.make_card(self.main, row=4, expand=True)

        log_head = tk.Frame(log_card, bg=s.CARD)
        log_head.pack(fill=tk.X, padx=15, pady=(10, 6))
        tk.Label(log_head, text="Activity Log", font=s.HEADING, bg=s.CARD, fg=s.TEXT).pack(side=tk.LEFT)

        # Clear button
        tk.Button(log_head, text="Clear", font=s.SMALL, bg=s.CARD, fg=s.TEXT_LIGHT,
                  activebackground=s.CARD, relief=tk.FLAT, cursor="hand2", command=self.clear_log).pack(side=tk.RIGHT)

        # Log level dropdown
        log_level_frame = tk.Frame(log_head, bg=s.CARD)
        log_level_frame.pack(side=tk.RIGHT, padx=(0, 15))
        tk.Label(log_level_frame, text="Level:", font=s.SMALL, bg=s.CARD, fg=s.TEXT_LIGHT).pack(side=tk.LEFT, padx=(0, 5))
        self.log_level_combo = ttk.Combobox(log_level_frame, width=8, state='readonly', font=s.SMALL,
                                            values=["Normal", "Verbose", "Debug"])
        self.log_level_combo.current(0)
        self.log_level_combo.pack(side=tk.LEFT)
        self.log_level_combo.bind("<<ComboboxSelected>>", self._on_log_level_change)

        log_wrap = tk.Frame(log_card, bg=s.BORDER, padx=1, pady=1)
        log_wrap.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 12))

        self.log_text = tk.Text(log_wrap, font=s.MONO, bg=s.LOG_BG, fg=s.LOG_INFO,
                                relief=tk.FLAT, padx=8, pady=6, wrap=tk.WORD,
                                state=tk.DISABLED, cursor="arrow")  # READONLY
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(log_wrap, command=self.log_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scroll.set)

        # Remove log from tab order
        self.log_text.configure(takefocus=0)

        # === BUTTONS ===
        self.btn_frame = tk.Frame(self.main, bg=s.BG)
        self.btn_frame.grid(row=5, column=0, sticky="ew", pady=(12, 0))

        self.start_btn = tk.Button(self.btn_frame, text="▶  START CONVERSION", font=(s.FONT, 11, "bold"),
                                   bg=s.PRIMARY, fg=s.WHITE, activebackground=s.PRIMARY_HOVER,
                                   activeforeground=s.WHITE, relief=tk.FLAT, pady=10, cursor="hand2",
                                   command=self.start_action)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.cancel_btn = tk.Button(self.btn_frame, text="✕  CANCEL", font=s.BODY,
                                    bg=s.BG, fg=s.TEXT_SECONDARY, activebackground=s.DANGER,
                                    activeforeground=s.WHITE, relief=tk.SOLID, bd=1, pady=10, padx=20,
                                    cursor="hand2", state=tk.DISABLED, command=self.cancel_action)
        self.cancel_btn.pack(side=tk.RIGHT)

        # Auto-eject checkbox (DVD mode) / placeholder for USB mode
        self.eject_check = tk.Checkbutton(self.btn_frame, text="Auto-eject", variable=self.auto_eject,
                                          font=s.SMALL, bg=s.BG, fg=s.TEXT_SECONDARY,
                                          activebackground=s.BG, selectcolor=s.BG, cursor="hand2")
        self.eject_check.pack(side=tk.RIGHT, padx=(0, 15))

    def _create_dvd_to_iso_panel(self):
        """Create the DVD → ISO mode panel."""
        s = self.s
        panel = self.dvd_to_iso_panel

        # === SOURCE DRIVE ===
        src_card = tk.Frame(panel, bg=s.CARD, highlightbackground=s.BORDER, highlightthickness=1)
        src_card.pack(fill=tk.X, pady=(0, 10))
        self.make_card_header(src_card, "Source Drive", "Select your DVD/CD drive")

        src_row = tk.Frame(src_card, bg=s.CARD)
        src_row.pack(fill=tk.X, padx=15, pady=(0, 12))

        combo_wrap = tk.Frame(src_row, bg=s.BORDER, padx=1, pady=1)
        combo_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.drive_combo = ttk.Combobox(combo_wrap, textvariable=self.source_drive, state='readonly', font=s.BODY)
        self.drive_combo.pack(fill=tk.X, ipady=5)

        self.refresh_btn = tk.Button(src_row, text="⟳ Refresh", font=s.BODY, bg=s.CARD, fg=s.TEXT,
                                     activebackground=s.BG, relief=tk.SOLID, bd=1, padx=12, pady=4,
                                     cursor="hand2", command=self.detect_drives)
        self.refresh_btn.pack(side=tk.RIGHT)

        # Disc info label
        self.disc_info_label = tk.Label(src_card, textvariable=self.disc_info_var, font=s.SMALL,
                                        bg=s.CARD, fg=s.TEXT_SECONDARY)
        self.disc_info_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Bind drive selection change to update disc info
        self.drive_combo.bind("<<ComboboxSelected>>", lambda e: self.update_disc_info())

        # === OUTPUT FILE ===
        out_card = tk.Frame(panel, bg=s.CARD, highlightbackground=s.BORDER, highlightthickness=1)
        out_card.pack(fill=tk.X, pady=(0, 10))
        self.make_card_header(out_card, "Output File", "Choose where to save the ISO")

        out_row = tk.Frame(out_card, bg=s.CARD)
        out_row.pack(fill=tk.X, padx=15, pady=(0, 12))

        entry_wrap = tk.Frame(out_row, bg=s.BORDER, padx=1, pady=1)
        entry_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.output_entry = tk.Entry(entry_wrap, textvariable=self.output_path, font=s.BODY,
                                     bg=s.CARD, fg=s.TEXT, relief=tk.FLAT)
        self.output_entry.pack(fill=tk.X, ipady=5, padx=3)

        self.browse_btn = tk.Button(out_row, text="📁 Browse", font=s.BODY, bg=s.CARD, fg=s.TEXT,
                                    activebackground=s.BG, relief=tk.SOLID, bd=1, padx=12, pady=4,
                                    cursor="hand2", command=self.browse_output)
        self.browse_btn.pack(side=tk.RIGHT)

        # Verify checkbox
        verify_row = tk.Frame(out_card, bg=s.CARD)
        verify_row.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.verify_check = tk.Checkbutton(verify_row, text="Verify ISO after copy",
                                           variable=self.verify_after, font=s.SMALL,
                                           bg=s.CARD, fg=s.TEXT_SECONDARY, activebackground=s.CARD,
                                           selectcolor=s.CARD, cursor="hand2")
        self.verify_check.pack(side=tk.LEFT)

    def _create_iso_to_usb_panel(self):
        """Create the ISO → USB mode panel."""
        s = self.s
        panel = self.iso_to_usb_panel

        # === SOURCE ISO ===
        iso_card = tk.Frame(panel, bg=s.CARD, highlightbackground=s.BORDER, highlightthickness=1)
        iso_card.pack(fill=tk.X, pady=(0, 10))
        self.make_card_header(iso_card, "Source ISO", "Select ISO image file")

        iso_row = tk.Frame(iso_card, bg=s.CARD)
        iso_row.pack(fill=tk.X, padx=15, pady=(0, 12))

        entry_wrap = tk.Frame(iso_row, bg=s.BORDER, padx=1, pady=1)
        entry_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.iso_entry = tk.Entry(entry_wrap, textvariable=self.iso_source_path, font=s.BODY,
                                  bg=s.CARD, fg=s.TEXT, relief=tk.FLAT)
        self.iso_entry.pack(fill=tk.X, ipady=5, padx=3)

        self.iso_browse_btn = tk.Button(iso_row, text="📁 Browse", font=s.BODY, bg=s.CARD, fg=s.TEXT,
                                        activebackground=s.BG, relief=tk.SOLID, bd=1, padx=12, pady=4,
                                        cursor="hand2", command=self.browse_iso)
        self.iso_browse_btn.pack(side=tk.RIGHT)

        # ISO info label
        self.iso_info_label = tk.Label(iso_card, textvariable=self.iso_type_var, font=s.SMALL,
                                       bg=s.CARD, fg=s.TEXT_SECONDARY)
        self.iso_info_label.pack(anchor="w", padx=15, pady=(0, 10))

        # === TARGET USB ===
        usb_card = tk.Frame(panel, bg=s.CARD, highlightbackground=s.BORDER, highlightthickness=1)
        usb_card.pack(fill=tk.X, pady=(0, 10))
        self.make_card_header(usb_card, "Target USB Drive", "Select destination USB drive")

        usb_row = tk.Frame(usb_card, bg=s.CARD)
        usb_row.pack(fill=tk.X, padx=15, pady=(0, 12))

        combo_wrap = tk.Frame(usb_row, bg=s.BORDER, padx=1, pady=1)
        combo_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.usb_combo = ttk.Combobox(combo_wrap, textvariable=self.target_usb, state='readonly', font=s.BODY)
        self.usb_combo.pack(fill=tk.X, ipady=5)

        self.usb_refresh_btn = tk.Button(usb_row, text="⟳ Refresh", font=s.BODY, bg=s.CARD, fg=s.TEXT,
                                         activebackground=s.BG, relief=tk.SOLID, bd=1, padx=12, pady=4,
                                         cursor="hand2", command=self.detect_usb_drives)
        self.usb_refresh_btn.pack(side=tk.RIGHT)

        # USB info and warning
        usb_info_row = tk.Frame(usb_card, bg=s.CARD)
        usb_info_row.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.usb_info_label = tk.Label(usb_info_row, textvariable=self.usb_info_var, font=s.SMALL,
                                       bg=s.CARD, fg=s.TEXT_SECONDARY)
        self.usb_info_label.pack(side=tk.LEFT)
        tk.Label(usb_info_row, text="⚠️ All data will be erased!", font=s.SMALL,
                 bg=s.CARD, fg=s.DANGER).pack(side=tk.RIGHT)

        # === BOOT MODE ===
        boot_card = tk.Frame(panel, bg=s.CARD, highlightbackground=s.BORDER, highlightthickness=1)
        boot_card.pack(fill=tk.X, pady=(0, 10))
        self.make_card_header(boot_card, "Boot Mode", "Target system compatibility")

        boot_row = tk.Frame(boot_card, bg=s.CARD)
        boot_row.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Radiobutton(boot_row, text="BIOS + UEFI (Maximum Compatibility)", variable=self.boot_mode,
                       value="both", font=s.SMALL, bg=s.CARD, fg=s.TEXT,
                       activebackground=s.CARD, selectcolor=s.CARD).pack(anchor="w")
        tk.Radiobutton(boot_row, text="UEFI Only (Modern systems)", variable=self.boot_mode,
                       value="uefi", font=s.SMALL, bg=s.CARD, fg=s.TEXT,
                       activebackground=s.CARD, selectcolor=s.CARD).pack(anchor="w")
        tk.Radiobutton(boot_row, text="BIOS Only (Legacy systems)", variable=self.boot_mode,
                       value="bios", font=s.SMALL, bg=s.CARD, fg=s.TEXT,
                       activebackground=s.CARD, selectcolor=s.CARD).pack(anchor="w")

    def switch_mode(self, mode):
        """Switch between DVD→ISO and ISO→USB modes."""
        if self.is_converting:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        self.current_mode.set(mode)
        s = self.s

        if mode == "dvd_to_iso":
            # Update button styles
            self.dvd_to_iso_btn.configure(bg=s.PRIMARY, fg=s.WHITE)
            self.iso_to_usb_btn.configure(bg=s.BORDER, fg=s.TEXT)
            # Show/hide panels
            self.iso_to_usb_panel.pack_forget()
            self.dvd_to_iso_panel.pack(fill=tk.X)
            # Update action button
            self.start_btn.configure(text="▶  START CONVERSION")
            self.eject_check.pack(side=tk.RIGHT, padx=(0, 15))
            self.log("Switched to DVD → ISO mode")
        else:
            # Update button styles
            self.dvd_to_iso_btn.configure(bg=s.BORDER, fg=s.TEXT)
            self.iso_to_usb_btn.configure(bg=s.PRIMARY, fg=s.WHITE)
            # Show/hide panels
            self.dvd_to_iso_panel.pack_forget()
            self.iso_to_usb_panel.pack(fill=tk.X)
            # Update action button
            self.start_btn.configure(text="▶  CREATE BOOTABLE USB")
            self.eject_check.pack_forget()
            self.log("Switched to ISO → USB mode")
            # Detect USB drives
            self.detect_usb_drives()

    def start_action(self):
        """Start the appropriate action based on current mode."""
        if self.current_mode.get() == "dvd_to_iso":
            self.start_conversion()
        else:
            self.start_usb_creation()

    def cancel_action(self):
        """Cancel the appropriate action based on current mode."""
        if self.current_mode.get() == "dvd_to_iso":
            self.cancel_conversion()
        else:
            self.cancel_usb_creation()
    
    def make_card(self, parent, row, expand=False):
        """Create a card frame."""
        card = tk.Frame(parent, bg=self.s.CARD, highlightbackground=self.s.BORDER, highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew" if expand else "ew", pady=(0, 10))
        return card
    
    def make_card_header(self, card, title, subtitle):
        """Add header to card."""
        head = tk.Frame(card, bg=self.s.CARD)
        head.pack(fill=tk.X, padx=15, pady=(10, 8))
        tk.Label(head, text=title, font=self.s.HEADING, bg=self.s.CARD, fg=self.s.TEXT).pack(side=tk.LEFT)
        if subtitle:
            tk.Label(head, text=subtitle, font=self.s.SMALL, bg=self.s.CARD, fg=self.s.TEXT_LIGHT).pack(side=tk.RIGHT)

    # === HELPER METHODS ===

    def format_size(self, bytes_val):
        """Format bytes as human-readable size."""
        if bytes_val >= 1073741824:  # 1 GB
            return f"{bytes_val / 1073741824:.2f} GB"
        elif bytes_val >= 1048576:  # 1 MB
            return f"{bytes_val / 1048576:.1f} MB"
        elif bytes_val >= 1024:  # 1 KB
            return f"{bytes_val / 1024:.1f} KB"
        else:
            return f"{bytes_val} B"

    def format_speed(self, bytes_per_sec):
        """Format speed as human-readable."""
        if bytes_per_sec >= 1048576:  # 1 MB/s
            return f"{bytes_per_sec / 1048576:.1f} MB/s"
        elif bytes_per_sec >= 1024:  # 1 KB/s
            return f"{bytes_per_sec / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec:.0f} B/s"

    def format_eta(self, seconds):
        """Format seconds as human-readable ETA."""
        if seconds < 0 or seconds > 86400:  # > 24 hours
            return "--:--"
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def _on_log_level_change(self, event=None):
        """Handle log level dropdown change."""
        level_map = {"Normal": 1, "Verbose": 2, "Debug": 3}
        selected = self.log_level_combo.get()
        self.log_level.set(level_map.get(selected, 1))
        self.log(f"Log level changed to: {selected}")

    def start_elapsed_timer(self):
        """Start the independent elapsed time timer."""
        self.update_elapsed_time()

    def update_elapsed_time(self):
        """Update elapsed time display independently of progress."""
        if self.is_converting and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            m, sec = divmod(int(elapsed), 60)
            h, m = divmod(m, 60)
            if h > 0:
                time_str = f"{h}:{m:02d}:{sec:02d}"
            else:
                time_str = f"{m:02d}:{sec:02d}"
            self.time_label.configure(text=f"Elapsed: {time_str}")

            # Fallback: Check output file size if no progress updates received
            out_path = self.output_path.get()
            if out_path and os.path.exists(out_path):
                try:
                    file_size = os.path.getsize(out_path)
                    if file_size > self.bytes_copied:
                        # Update from file size
                        self.bytes_copied = file_size
                        # Calculate speed from file growth
                        if elapsed > 0:
                            self.current_speed = file_size / elapsed
                            self.speed_label.configure(text=f"Speed: {self.format_speed(self.current_speed)}")
                        # Update bytes display
                        if self.total_bytes > 0:
                            pct = min(99, int((file_size / self.total_bytes) * 100))
                            self.percent_label.configure(text=f"{pct}%")
                            self.bytes_label.configure(
                                text=f"{self.format_size(file_size)} / {self.format_size(self.total_bytes)}"
                            )
                            # Update progress bar
                            w = self.prog_bar_bg.winfo_width()
                            self.prog_fill.place(x=0, y=0, relheight=1, width=int((pct/100)*w))
                            # Calculate ETA
                            if self.current_speed > 0:
                                remaining = self.total_bytes - file_size
                                eta = remaining / self.current_speed
                                self.eta_label.configure(text=f"ETA: {self.format_eta(eta)}")
                        else:
                            self.bytes_label.configure(text=f"{self.format_size(file_size)} copied")
                except:
                    pass

            # Update activity indicator in status
            self.activity_counter = (self.activity_counter + 1) % 4
            indicators = ["◐", "◓", "◑", "◒"]
            if self.bytes_copied > 0:
                base_status = "Copying"
            else:
                base_status = "Initializing"
            self.status_var.set(f"{indicators[self.activity_counter]} {base_status}...")

            # Schedule next update (every 500ms)
            self.elapsed_timer_id = self.root.after(500, self.update_elapsed_time)

    def stop_elapsed_timer(self):
        """Stop the elapsed time timer."""
        if self.elapsed_timer_id:
            self.root.after_cancel(self.elapsed_timer_id)
            self.elapsed_timer_id = None

    def update_disc_info(self):
        """Get and display disc information."""
        src = self.source_drive.get()
        if not src or "No drives" in src:
            self.disc_info_var.set("")
            return

        dev = src.split()[0]
        self.log(f"Getting disc info for {dev}...", min_verbosity=2)

        # Run in thread to avoid UI freeze
        threading.Thread(target=self._get_disc_info_thread, args=(dev,), daemon=True).start()

    def _get_disc_info_thread(self, dev):
        """Background thread to get disc info."""
        info = self.get_disc_info(dev)
        self.root.after(0, lambda: self.disc_info_var.set(info))
        if info:
            self.root.after(0, lambda: self.log(f"Disc: {info}", min_verbosity=2))

    def get_disc_info(self, device):
        """Get disc information (platform-specific)."""
        try:
            if platform.system() == "Windows":
                return self._get_disc_info_windows(device)
            elif platform.system() == "Linux":
                return self._get_disc_info_linux(device)
            elif platform.system() == "Darwin":
                return self._get_disc_info_macos(device)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Disc info error: {e}", "warning", min_verbosity=3))
        return ""

    def _get_disc_info_windows(self, device):
        """Get disc info on Windows."""
        import ctypes
        letter = device[0]

        # Get volume info
        vol = ctypes.create_unicode_buffer(1024)
        fs = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetVolumeInformationW(f"{letter}:\\", vol, 1024, None, None, None, fs, 1024)

        label = vol.value if vol.value else None
        filesystem = fs.value or ""

        # Get size via multiple methods
        size = 0

        # Method 1: WMI (most reliable for optical drives)
        if size == 0:
            try:
                r = subprocess.run(['powershell', '-Command',
                    f'(Get-WmiObject Win32_LogicalDisk -Filter "DeviceID=\'{letter}:\'").Size'],
                    capture_output=True, text=True, timeout=5,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if r.stdout.strip():
                    size = int(r.stdout.strip())
            except:
                pass

        # Method 2: CIM fallback
        if size == 0:
            try:
                r = subprocess.run(['powershell', '-Command',
                    f'(Get-CimInstance Win32_LogicalDisk -Filter "DeviceID=\'{letter}:\'").Size'],
                    capture_output=True, text=True, timeout=5,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if r.stdout.strip():
                    size = int(r.stdout.strip())
            except:
                pass

        # Store for progress calculation
        if size > 0:
            self.total_bytes = size

        # Build info string: Label | Size | Filesystem
        parts = []
        if label:
            parts.append(label)
        if size > 0:
            parts.append(self.format_size(size))
        if filesystem:
            parts.append(filesystem)

        return " | ".join(parts) if parts else "Disc inserted"

    def _get_disc_info_linux(self, device):
        """Get disc info on Linux."""
        label = None
        size = 0
        filesystem = None

        # Get label
        try:
            r = subprocess.run(['blkid', '-o', 'value', '-s', 'LABEL', device],
                             capture_output=True, text=True, timeout=5)
            label = r.stdout.strip() if r.stdout.strip() else None
        except:
            pass

        # Get size
        try:
            r = subprocess.run(['blockdev', '--getsize64', device], capture_output=True, text=True, timeout=5)
            size = int(r.stdout.strip()) if r.stdout.strip() else 0
            self.total_bytes = size  # Store for progress calculation
        except:
            pass

        # Get filesystem
        try:
            r = subprocess.run(['blkid', '-o', 'value', '-s', 'TYPE', device],
                             capture_output=True, text=True, timeout=5)
            filesystem = r.stdout.strip().upper() if r.stdout.strip() else None
        except:
            pass

        # Build info string: Label | Size | Filesystem
        parts = []
        if label:
            parts.append(label)
        if size > 0:
            parts.append(self.format_size(size))
        if filesystem:
            parts.append(filesystem)

        return " | ".join(parts) if parts else "Disc inserted"

    def _get_disc_info_macos(self, device):
        """Get disc info on macOS."""
        try:
            r = subprocess.run(['diskutil', 'info', device], capture_output=True, text=True, timeout=5)
            info = {}
            for line in r.stdout.split('\n'):
                if ':' in line:
                    key, _, value = line.partition(':')
                    info[key.strip()] = value.strip()

            label = info.get('Volume Name', None)
            if label == 'Not applicable':
                label = None
            size_str = info.get('Total Size', info.get('Disk Size', None))
            filesystem = info.get('File System Personality', info.get('Type (Bundle)', None))

            # Extract size in bytes for progress calculation
            if size_str:
                bytes_match = re.search(r'\((\d+)\s*Bytes\)', size_str)
                if bytes_match:
                    self.total_bytes = int(bytes_match.group(1))
                # Extract human-readable size
                size_match = re.search(r'[\d.]+\s*[GMKT]B', size_str)
                size_str = size_match.group(0) if size_match else None

            # Build info string: Label | Size | Filesystem
            parts = []
            if label:
                parts.append(label)
            if size_str:
                parts.append(size_str)
            if filesystem and filesystem != 'Unknown':
                parts.append(filesystem)

            return " | ".join(parts) if parts else "Disc inserted"
        except:
            return "Disc inserted"

    def eject_disc(self, device):
        """Eject disc (platform-specific)."""
        try:
            if platform.system() == "Windows":
                letter = device[0]
                script = f'(New-Object -ComObject Shell.Application).NameSpace(17).ParseName("{letter}:").InvokeVerb("Eject")'
                subprocess.run(['powershell', '-Command', script],
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            elif platform.system() == "Linux":
                subprocess.run(['eject', device])
            elif platform.system() == "Darwin":
                subprocess.run(['drutil', 'eject'])
            self.log("Disc ejected", "success")
        except Exception as e:
            self.log(f"Eject failed: {e}", "warning")

    def verify_iso(self, iso_path, expected_size=None):
        """Verify ISO integrity by reading it back."""
        self.log("Verifying ISO...", "info")
        self.status_var.set("Verifying...")

        try:
            actual_size = os.path.getsize(iso_path)

            # Size check
            if expected_size and abs(actual_size - expected_size) > 2048:
                self.log(f"Size mismatch: expected {self.format_size(expected_size)}, got {self.format_size(actual_size)}", "warning")
                return False

            # Read verification - ensure file is readable
            self.log(f"Reading back {self.format_size(actual_size)}...", min_verbosity=2)
            bytes_read = 0
            buffer_size = 1024 * 1024  # 1 MB chunks

            with open(iso_path, 'rb') as f:
                while True:
                    chunk = f.read(buffer_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    pct = int((bytes_read / actual_size) * 100)
                    self.root.after(0, lambda p=pct: self.status_var.set(f"Verifying... {p}%"))

            self.log(f"Verification complete: {self.format_size(bytes_read)} verified", "success")
            return True
        except Exception as e:
            self.log(f"Verification failed: {e}", "error")
            return False

    def log(self, msg, level="info", min_verbosity=1):
        """Add to log (readonly-safe). Only shows if current log_level >= min_verbosity."""
        # Check verbosity level
        if self.log_level.get() < min_verbosity:
            return

        ts = datetime.now().strftime("%H:%M:%S")
        colors = {"info": self.s.LOG_INFO, "success": self.s.LOG_SUCCESS,
                  "warning": self.s.LOG_WARNING, "error": self.s.LOG_ERROR}

        # Add verbosity indicator for verbose/debug messages
        prefix = ""
        if min_verbosity == 2:
            prefix = "[V] "
        elif min_verbosity == 3:
            prefix = "[D] "

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] ", "ts")
        self.log_text.insert(tk.END, f"{prefix}{msg}\n", level)
        self.log_text.tag_configure("ts", foreground=self.s.TEXT_LIGHT)
        self.log_text.tag_configure(level, foreground=colors.get(level, colors["info"]))
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear log."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log("Log cleared")
    
    def update_progress(self, pct, bytes_copied=None, total_bytes=None):
        """Update progress display with optional speed/ETA calculation."""
        # Update bytes tracking first
        if bytes_copied is not None and bytes_copied > 0:
            self.bytes_copied = bytes_copied
        if total_bytes is not None and total_bytes > 0:
            self.total_bytes = total_bytes

        # Recalculate percentage if we have bytes info but pct is 0
        if pct == 0 and self.bytes_copied > 0 and self.total_bytes > 0:
            pct = min(99, int((self.bytes_copied / self.total_bytes) * 100))

        self.progress_var.set(pct)
        self.percent_label.configure(text=f"{int(pct)}%")

        self.root.update_idletasks()
        w = self.prog_bar_bg.winfo_width()
        self.prog_fill.place(x=0, y=0, relheight=1, width=int((pct/100)*w))

        now = datetime.now()

        if self.start_time and self.is_converting:
            elapsed = (now - self.start_time).total_seconds()

            # Calculate speed from elapsed time and bytes copied (more reliable)
            if elapsed > 0 and self.bytes_copied > 0:
                # Use overall average speed for stability
                avg_speed = self.bytes_copied / elapsed

                # Also calculate recent speed for responsiveness
                if self.last_speed_time is None or (now - self.last_speed_time).total_seconds() >= 1.0:
                    if self.last_speed_time and self.bytes_copied > self.last_speed_bytes:
                        time_delta = (now - self.last_speed_time).total_seconds()
                        bytes_delta = self.bytes_copied - self.last_speed_bytes
                        if time_delta > 0:
                            recent_speed = bytes_delta / time_delta
                            # Blend recent and average for smooth display
                            self.current_speed = (recent_speed * 0.7) + (avg_speed * 0.3)

                    self.last_speed_time = now
                    self.last_speed_bytes = self.bytes_copied

                # If no recent speed calculated yet, use average
                if self.current_speed == 0:
                    self.current_speed = avg_speed

            # Always update speed label if we have speed data
            if self.current_speed > 0:
                self.speed_label.configure(text=f"Speed: {self.format_speed(self.current_speed)}")

                # Calculate ETA
                if self.total_bytes > 0 and self.bytes_copied < self.total_bytes:
                    remaining_bytes = self.total_bytes - self.bytes_copied
                    eta_seconds = remaining_bytes / self.current_speed
                    self.eta_label.configure(text=f"ETA: {self.format_eta(eta_seconds)}")
                elif pct >= 100:
                    self.eta_label.configure(text="Done")
                else:
                    self.eta_label.configure(text="Calculating...")
            else:
                self.speed_label.configure(text="Calculating...")

            # Always update bytes label - show what we have
            if self.bytes_copied > 0:
                if self.total_bytes > 0:
                    self.bytes_label.configure(
                        text=f"{self.format_size(self.bytes_copied)} / {self.format_size(self.total_bytes)}"
                    )
                else:
                    self.bytes_label.configure(text=f"{self.format_size(self.bytes_copied)} copied")

            # Log verbose progress updates (every 5%)
            if pct > 0 and pct % 5 == 0 and self.current_speed > 0:
                self.log(f"Progress: {int(pct)}% | {self.format_speed(self.current_speed)}", min_verbosity=2)
    
    def detect_drives(self):
        """Find DVD drives."""
        self.log("Scanning for drives...")
        drives = []
        
        if platform.system() == "Windows":
            import string, ctypes
            for letter in string.ascii_uppercase:
                try:
                    if ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\") == 5:
                        vol = ctypes.create_unicode_buffer(1024)
                        ctypes.windll.kernel32.GetVolumeInformationW(f"{letter}:\\", vol, 1024, None, None, None, None, 0)
                        label = vol.value or "CD/DVD Drive"
                        drives.append(f"{letter}: ({label})")
                except:
                    pass
        elif platform.system() == "Linux":
            for dev in ['/dev/sr0', '/dev/sr1', '/dev/cdrom']:
                if os.path.exists(dev):
                    drives.append(f"{dev} (Optical)")
        elif platform.system() == "Darwin":
            try:
                r = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
                for line in r.stdout.split('\n'):
                    if 'CD' in line or 'DVD' in line:
                        drives.append(f"/dev/{line.split()[-1]} (Optical)")
            except:
                pass
        
        if not drives:
            drives = ["No drives found - Insert disc"]
            self.log("No drives found", "warning")
        else:
            self.log(f"Found {len(drives)} drive(s)", "success")
        
        self.drive_combo['values'] = drives
        if drives:
            self.drive_combo.current(0)
            # Update disc info for selected drive
            self.root.after(200, self.update_disc_info)
    
    def browse_output(self):
        """Pick output file."""
        name = "backup.iso"
        drv = self.source_drive.get()
        if "(" in drv:
            lbl = drv.split("(")[1].rstrip(")")
            if lbl not in ["CD/DVD Drive", "Optical"]:
                name = re.sub(r'[<>:"/\\|?*]', '_', lbl) + ".iso"
        
        path = filedialog.asksaveasfilename(title="Save ISO", defaultextension=".iso",
                                            filetypes=[("ISO", "*.iso"), ("All", "*.*")], initialfile=name)
        if path:
            self.output_path.set(path)
            self.log(f"Output: {path}")
    
    def start_conversion(self):
        """Begin conversion."""
        src = self.source_drive.get()
        out = self.output_path.get()
        
        if "No drives" in src:
            messagebox.showerror("Error", "No DVD drive found.\nInsert a disc and click Refresh.")
            return
        if not out:
            messagebox.showerror("Error", "Select an output file first.")
            return
        if os.path.exists(out) and not messagebox.askyesno("Overwrite?", f"Overwrite existing file?\n{out}"):
            return
        
        dev = src.split()[0]
        self.is_converting = True
        self.start_time = datetime.now()

        # Reset progress tracking
        self.bytes_copied = 0
        self.total_bytes = 0
        self.last_speed_time = None
        self.last_speed_bytes = 0
        self.current_speed = 0
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")
        self.bytes_label.configure(text="")

        self.start_btn.configure(state=tk.DISABLED, bg=self.s.BORDER)
        self.cancel_btn.configure(state=tk.NORMAL, bg=self.s.DANGER, fg=self.s.WHITE)
        self.update_progress(0)
        self.status_var.set("◐ Initializing...")
        self.activity_counter = 0
        self.log(f"Converting {dev} → {os.path.basename(out)}")

        # Start the elapsed time timer
        self.start_elapsed_timer()

        threading.Thread(target=self.run_conversion, args=(dev, out), daemon=True).start()
    
    def run_conversion(self, dev, out):
        """Background conversion."""
        try:
            if platform.system() == "Windows":
                self.convert_windows(dev, out)
            elif platform.system() == "Linux":
                self.convert_linux(dev, out)
            elif platform.system() == "Darwin":
                self.convert_macos(dev, out)
            
            if self.is_converting:
                self.root.after(0, self.done, True, "Conversion complete!")
        except Exception as e:
            if self.is_converting:
                self.root.after(0, self.done, False, str(e))
    
    def convert_windows(self, dev, out):
        """Windows PowerShell conversion with reliable progress reporting."""
        # PowerShell script with forced output flushing and better error handling
        script = f'''
$ErrorActionPreference = "Stop"
$drive = "{dev[0]}:"
$outPath = "{out}"

Write-Host "STATUS:Checking disc..."
[Console]::Out.Flush()

# Check if disc is present
$vol = Get-Volume -DriveLetter "{dev[0]}" -ErrorAction SilentlyContinue
if (-not $vol) {{
    Write-Host "ERROR:No disc found in drive {dev[0]}:"
    exit 1
}}

# Get disc size using multiple methods
$size = [long]0

# Method 1: Try WMI (most reliable for optical drives)
Write-Host "STATUS:Detecting disc size..."
[Console]::Out.Flush()
try {{
    $wmiDisk = Get-WmiObject -Query "SELECT Size FROM Win32_LogicalDisk WHERE DeviceID='{dev[0]}:'" -ErrorAction SilentlyContinue
    if ($wmiDisk -and $wmiDisk.Size) {{
        $size = [long]$wmiDisk.Size
        Write-Host ("STATUS:WMI detected size: " + $size)
    }}
}} catch {{ }}

# Method 2: Try CIM if WMI failed
if ($size -eq 0) {{
    try {{
        $cimDisk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='{dev[0]}:'" -ErrorAction SilentlyContinue
        if ($cimDisk -and $cimDisk.Size) {{
            $size = [long]$cimDisk.Size
            Write-Host ("STATUS:CIM detected size: " + $size)
        }}
    }} catch {{ }}
}}

# Method 3: Use a reasonable default based on disc type
if ($size -eq 0) {{
    # Default to dual-layer DVD size (8.5 GB) as safe upper bound
    $size = [long]8500000000
    Write-Host "STATUS:Using estimated size (8.5 GB)"
}}

Write-Host ("SIZE:" + $size)
[Console]::Out.Flush()

Write-Host "STATUS:Opening disc for reading..."
[Console]::Out.Flush()

try {{
    $stream = [System.IO.File]::OpenRead("\\\\.\\" + $drive)
}} catch {{
    Write-Host ("ERROR:Cannot open disc - " + $_.Exception.Message)
    exit 1
}}

Write-Host "STATUS:Creating output file..."
[Console]::Out.Flush()

try {{
    $writer = [System.IO.File]::OpenWrite($outPath)
}} catch {{
    $stream.Close()
    Write-Host ("ERROR:Cannot create output file - " + $_.Exception.Message)
    exit 1
}}

# Use larger buffer for performance (1MB)
$bufSize = 1048576
$buf = New-Object byte[] $bufSize
$total = [long]0
$lastPct = -1
$lastReport = [DateTime]::Now

Write-Host "STATUS:Copying disc data..."
Write-Host ("PROGRESS:0:" + $total + ":" + $size)
[Console]::Out.Flush()

try {{
    while ($true) {{
        $n = $stream.Read($buf, 0, $bufSize)
        if ($n -le 0) {{ break }}

        $writer.Write($buf, 0, $n)
        $total += $n

        # Calculate percentage
        $pct = 0
        if ($size -gt 0) {{
            $pct = [int](($total / $size) * 100)
            if ($pct -gt 99) {{ $pct = 99 }}
        }}

        # Report progress every 1% change OR every 500ms
        $now = [DateTime]::Now
        $elapsed = ($now - $lastReport).TotalMilliseconds
        if (($pct -ne $lastPct) -or ($elapsed -gt 500)) {{
            Write-Host ("PROGRESS:" + $pct + ":" + $total + ":" + $size)
            [Console]::Out.Flush()
            $lastPct = $pct
            $lastReport = $now
        }}
    }}
}} catch {{
    $stream.Close()
    $writer.Close()
    Write-Host ("ERROR:Read/write error - " + $_.Exception.Message)
    exit 1
}}

$stream.Close()
$writer.Close()

# Update size to actual bytes written
Write-Host ("PROGRESS:100:" + $total + ":" + $total)
Write-Host "STATUS:Complete"
[Console]::Out.Flush()
'''
        self.root.after(0, lambda: self.log("Starting Windows disc read...", min_verbosity=2))

        self.process = subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        self._monitor_with_bytes()
    
    def convert_linux(self, dev, out):
        """Linux dd conversion."""
        self.process = subprocess.Popen(['dd', f'if={dev}', f'of={out}', 'bs=2048', 'status=progress'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        size = None
        try:
            r = subprocess.run(['blockdev', '--getsize64', dev], capture_output=True, text=True)
            size = int(r.stdout.strip())
            self.total_bytes = size
            self.root.after(0, lambda: self.log(f"Disc size: {self.format_size(size)}", min_verbosity=2))
        except:
            pass

        while self.process.poll() is None and self.is_converting:
            line = self.process.stderr.readline()
            if line:
                # Log raw output in debug mode
                self.root.after(0, lambda l=line.strip(): self.log(f"dd: {l}", min_verbosity=3))

                if 'bytes' in line:
                    m = re.search(r'(\d+)\s+bytes', line)
                    if m:
                        bytes_copied = int(m.group(1))
                        pct = min(99, (bytes_copied / size * 100)) if size else 0
                        self.root.after(0, lambda p=pct, b=bytes_copied, s=size:
                                       self.update_progress(p, bytes_copied=b, total_bytes=s))

        if self.process.returncode and self.is_converting:
            raise Exception(self.process.stderr.read())
    
    def convert_macos(self, dev, out):
        """macOS hdiutil conversion."""
        # Try to get disc size first
        try:
            r = subprocess.run(['diskutil', 'info', dev], capture_output=True, text=True, timeout=5)
            for line in r.stdout.split('\n'):
                if 'Total Size' in line or 'Disk Size' in line:
                    # Extract bytes from line like "Total Size: 4.7 GB (4700000000 Bytes)"
                    m = re.search(r'\((\d+)\s*Bytes\)', line)
                    if m:
                        self.total_bytes = int(m.group(1))
                        self.root.after(0, lambda: self.log(f"Disc size: {self.format_size(self.total_bytes)}", min_verbosity=2))
                    break
        except:
            pass

        self.process = subprocess.Popen(['hdiutil', 'makehybrid', '-iso', '-joliet', '-o', out, dev],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self._monitor()
    
    def _monitor(self):
        """Watch subprocess output (basic progress only)."""
        while self.process and self.process.poll() is None and self.is_converting:
            line = self.process.stdout.readline()
            if line:
                # Log raw output in debug mode
                self.root.after(0, lambda l=line.strip(): self.log(f"Output: {l}", min_verbosity=3))

                if line.startswith("PROGRESS:"):
                    try:
                        self.root.after(0, self.update_progress, int(line.split(":")[1]))
                    except:
                        pass
        if self.process and self.process.returncode and self.is_converting:
            raise Exception(self.process.stderr.read() if self.process.stderr else "Unknown error")

    def _monitor_with_bytes(self):
        """Watch subprocess output with bytes tracking, status updates, and error handling."""
        error_msg = None

        while self.process and self.process.poll() is None and self.is_converting:
            line = self.process.stdout.readline()
            if line:
                line = line.strip()
                # Log raw output in debug mode
                self.root.after(0, lambda l=line: self.log(f"PS: {l}", min_verbosity=3))

                if line.startswith("PROGRESS:"):
                    try:
                        parts = line.split(":")
                        pct = int(parts[1])
                        bytes_copied = int(parts[2]) if len(parts) > 2 else None
                        total_bytes = int(parts[3]) if len(parts) > 3 else None
                        self.root.after(0, lambda p=pct, b=bytes_copied, t=total_bytes:
                                       self.update_progress(p, bytes_copied=b, total_bytes=t))
                    except:
                        pass
                elif line.startswith("SIZE:"):
                    try:
                        size = int(line.split(":")[1])
                        if size > 0:
                            self.total_bytes = size
                            self.root.after(0, lambda s=size: self.log(f"Disc size: {self.format_size(s)}", min_verbosity=2))
                    except:
                        pass
                elif line.startswith("STATUS:"):
                    # Log status messages
                    status = line.split(":", 1)[1] if ":" in line else line
                    self.root.after(0, lambda s=status: self.log(s, min_verbosity=2))
                elif line.startswith("ERROR:"):
                    # Capture error message
                    error_msg = line.split(":", 1)[1] if ":" in line else "Unknown error"
                    self.root.after(0, lambda e=error_msg: self.log(f"Error: {e}", "error"))

        # Check for errors
        if error_msg and self.is_converting:
            raise Exception(error_msg)

        # Check process return code
        if self.process and self.process.returncode and self.is_converting:
            stderr_output = ""
            try:
                stderr_output = self.process.stderr.read()
            except:
                pass
            raise Exception(stderr_output if stderr_output else "Conversion failed")
    
    def done(self, ok, msg):
        """Conversion finished."""
        self.is_converting = False
        self.process = None
        self.stop_elapsed_timer()  # Stop the timer
        self.start_btn.configure(state=tk.NORMAL, bg=self.s.PRIMARY)
        self.cancel_btn.configure(state=tk.DISABLED, bg=self.s.BG, fg=self.s.TEXT_SECONDARY)

        out = self.output_path.get()
        dev = self.source_drive.get().split()[0] if self.source_drive.get() else None

        if ok:
            self.update_progress(100, bytes_copied=self.total_bytes, total_bytes=self.total_bytes)
            self.status_var.set("✓ Complete")
            self.log(msg, "success")

            if os.path.exists(out):
                sz = os.path.getsize(out)
                self.log(f"Size: {self.format_size(sz)}", "success")

            if self.start_time:
                el = int((datetime.now() - self.start_time).total_seconds())
                self.log(f"Time: {el//60:02d}:{el%60:02d}")

                # Log average speed
                if self.bytes_copied > 0 and el > 0:
                    avg_speed = self.bytes_copied / el
                    self.log(f"Average speed: {self.format_speed(avg_speed)}", min_verbosity=2)

            # Post-copy verification
            verification_ok = True
            if self.verify_after.get() and os.path.exists(out):
                self.log("Starting verification...", "info")
                verification_ok = self.verify_iso(out, self.total_bytes)
                if verification_ok:
                    self.log("Verification passed!", "success")
                else:
                    self.log("Verification failed!", "error")
                    msg += "\n\nWarning: Verification failed!"

            # Auto-eject
            if self.auto_eject.get() and dev:
                self.log("Ejecting disc...", min_verbosity=2)
                self.eject_disc(dev)

            self.status_var.set("✓ Complete" if verification_ok else "⚠ Verify Failed")
            messagebox.showinfo("Done", f"{msg}\n\nSaved to:\n{out}")
        else:
            self.status_var.set("✗ Failed")
            self.log(f"Error: {msg}", "error")
            messagebox.showerror("Error", msg)
    
    def cancel_conversion(self):
        """Stop conversion."""
        if self.is_converting and messagebox.askyesno("Cancel?", "Stop the conversion?"):
            self.is_converting = False
            self.stop_elapsed_timer()  # Stop the timer
            if self.process:
                self.process.terminate()

            self.status_var.set("Cancelled")
            self.log("Cancelled", "warning")
            self.start_btn.configure(state=tk.NORMAL, bg=self.s.PRIMARY)
            self.cancel_btn.configure(state=tk.DISABLED, bg=self.s.BG, fg=self.s.TEXT_SECONDARY)
            
            out = self.output_path.get()
            if out and os.path.exists(out):
                try:
                    os.remove(out)
                    self.log("Partial file removed", "warning")
                except:
                    pass


    # ========== ISO → USB METHODS ==========

    def browse_iso(self):
        """Browse for ISO file."""
        path = filedialog.askopenfilename(
            title="Select ISO Image",
            filetypes=[("ISO Images", "*.iso"), ("All Files", "*.*")]
        )
        if path:
            self.iso_source_path.set(path)
            self.log(f"Selected: {os.path.basename(path)}")
            # Detect ISO type in background
            threading.Thread(target=self._detect_iso_type_thread, args=(path,), daemon=True).start()

    def _detect_iso_type_thread(self, iso_path):
        """Background thread to detect ISO type."""
        iso_type, info = self.detect_iso_type(iso_path)
        self.detected_iso_type = iso_type
        self.root.after(0, lambda: self.iso_type_var.set(info))
        self.root.after(0, lambda: self.log(f"ISO type: {info}", min_verbosity=2))

    def detect_iso_type(self, iso_path):
        """Detect ISO type (Windows, Linux hybrid, etc.) by examining ISO contents."""
        try:
            size = os.path.getsize(iso_path)
            size_str = self.format_size(size)

            # Check for ISOHybrid (has MBR boot signature at offset 510-511)
            is_hybrid = False
            with open(iso_path, 'rb') as f:
                f.seek(510)
                sig = f.read(2)
                if sig == b'\x55\xAA':
                    is_hybrid = True

            # Try to detect Windows by checking for Windows-specific markers in ISO
            is_windows = False

            # Method 1: Check for Windows markers by mounting ISO (Windows/macOS)
            if platform.system() == "Windows":
                try:
                    # Mount ISO and check for Windows files
                    r = subprocess.run(['powershell', '-Command',
                        f'$m = Mount-DiskImage -ImagePath "{iso_path}" -PassThru; ' +
                        f'$v = Get-Volume -DiskImage $m; $l = $v.DriveLetter; ' +
                        f'$hasWin = (Test-Path "$l`:\\sources\\install.wim") -or (Test-Path "$l`:\\sources\\install.esd"); ' +
                        f'Dismount-DiskImage -ImagePath "{iso_path}" | Out-Null; ' +
                        f'Write-Host $hasWin'],
                        capture_output=True, text=True, timeout=30,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                    if 'True' in r.stdout:
                        is_windows = True
                except:
                    pass
            elif platform.system() == "Darwin":
                try:
                    # Mount and check on macOS
                    import tempfile
                    mount_point = tempfile.mkdtemp(prefix="iso_check_")
                    subprocess.run(['hdiutil', 'attach', iso_path, '-mountpoint', mount_point, '-nobrowse'],
                                 capture_output=True, timeout=30)
                    # Check for Windows markers
                    if (os.path.exists(os.path.join(mount_point, 'sources', 'install.wim')) or
                        os.path.exists(os.path.join(mount_point, 'sources', 'install.esd'))):
                        is_windows = True
                    subprocess.run(['hdiutil', 'detach', mount_point], capture_output=True)
                    os.rmdir(mount_point)
                except:
                    pass

            # Method 2: Fallback to filename heuristics
            if not is_windows:
                basename = os.path.basename(iso_path).lower()
                if 'win' in basename or 'windows' in basename:
                    is_windows = True
                elif any(x in basename for x in ['ubuntu', 'fedora', 'debian', 'linux', 'mint', 'arch', 'centos', 'manjaro', 'opensuse', 'kali', 'pop_os']):
                    is_windows = False

            # Determine final type
            if is_windows:
                return 'windows', f"Windows Install ISO | {size_str}"
            elif is_hybrid:
                return 'linux_hybrid', f"Linux Hybrid ISO | {size_str} (DD mode)"
            else:
                return 'unknown', f"ISO Image | {size_str}"

        except Exception as e:
            return 'unknown', f"Error: {e}"

    def detect_usb_drives(self):
        """Detect removable USB drives."""
        self.log("Scanning for USB drives...")
        drives = []

        if platform.system() == "Windows":
            drives = self._detect_usb_drives_windows()
        elif platform.system() == "Darwin":
            drives = self._detect_usb_drives_macos()
        elif platform.system() == "Linux":
            drives = self._detect_usb_drives_linux()

        if not drives:
            drives = ["No USB drives found"]
            self.log("No USB drives found", "warning")
        else:
            self.log(f"Found {len(drives)} USB drive(s)", "success")

        self.usb_combo['values'] = drives
        if drives:
            self.usb_combo.current(0)
            self._update_usb_info()

    def _detect_usb_drives_windows(self):
        """Detect USB drives on Windows."""
        drives = []
        try:
            # Use PowerShell to get USB drives
            script = '''
Get-WmiObject Win32_DiskDrive | Where-Object {$_.InterfaceType -eq 'USB'} | ForEach-Object {
    $disk = $_
    $diskNum = $disk.Index
    $size = [math]::Round($disk.Size / 1GB, 1)
    $model = $disk.Model
    Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} WHERE AssocClass=Win32_DiskDriveToDiskPartition" | ForEach-Object {
        Get-WmiObject -Query "ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($_.DeviceID)'} WHERE AssocClass=Win32_LogicalDiskToPartition" | ForEach-Object {
            Write-Host "$diskNum|$($_.DeviceID)|$model|$size"
        }
    }
}
'''
            r = subprocess.run(['powershell', '-Command', script],
                             capture_output=True, text=True, timeout=10,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

            seen_disks = set()
            for line in r.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        disk_num, letter, model, size = parts[0], parts[1], parts[2], parts[3]
                        if disk_num not in seen_disks:
                            seen_disks.add(disk_num)
                            drives.append(f"{letter} ({model.strip()}, {size} GB) [Disk {disk_num}]")

            # If no partitions found, list disks directly
            if not drives:
                script2 = '''
Get-WmiObject Win32_DiskDrive | Where-Object {$_.InterfaceType -eq 'USB'} | ForEach-Object {
    $size = [math]::Round($_.Size / 1GB, 1)
    Write-Host "$($_.Index)|$($_.Model)|$size"
}
'''
                r = subprocess.run(['powershell', '-Command', script2],
                                 capture_output=True, text=True, timeout=10,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                for line in r.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            disk_num, model, size = parts[0], parts[1], parts[2]
                            drives.append(f"Disk {disk_num} ({model.strip()}, {size} GB)")

        except Exception as e:
            self.log(f"USB detection error: {e}", "warning", min_verbosity=3)

        return drives

    def _detect_usb_drives_macos(self):
        """Detect USB drives on macOS."""
        drives = []
        try:
            # Get list of external disks
            r = subprocess.run(['diskutil', 'list', 'external'], capture_output=True, text=True, timeout=10)

            current_disk = None
            for line in r.stdout.split('\n'):
                if line.startswith('/dev/disk'):
                    current_disk = line.split()[0]
                elif current_disk and '*' in line:
                    # Get disk info
                    info_r = subprocess.run(['diskutil', 'info', current_disk],
                                          capture_output=True, text=True, timeout=5)
                    name = "USB Drive"
                    size = "Unknown"
                    for info_line in info_r.stdout.split('\n'):
                        if 'Media Name:' in info_line:
                            name = info_line.split(':')[1].strip()
                        elif 'Disk Size:' in info_line:
                            size_match = re.search(r'([\d.]+\s*[GMKT]B)', info_line)
                            if size_match:
                                size = size_match.group(1)

                    drives.append(f"{current_disk} ({name}, {size})")
                    current_disk = None

        except Exception as e:
            self.log(f"USB detection error: {e}", "warning", min_verbosity=3)

        return drives

    def _detect_usb_drives_linux(self):
        """Detect USB drives on Linux."""
        drives = []
        try:
            # Use lsblk to find removable devices
            r = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,MODEL,RM', '-n'],
                             capture_output=True, text=True, timeout=10)

            for line in r.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 4 and parts[-1] == '1':  # RM=1 means removable
                    name = f"/dev/{parts[0]}"
                    size = parts[1]
                    model = ' '.join(parts[2:-1]) if len(parts) > 4 else parts[2]
                    drives.append(f"{name} ({model}, {size})")

        except Exception as e:
            self.log(f"USB detection error: {e}", "warning", min_verbosity=3)

        return drives

    def _update_usb_info(self):
        """Update USB info label based on selection."""
        selected = self.target_usb.get()
        if selected and "No USB" not in selected:
            # Extract size from selection string
            size_match = re.search(r'([\d.]+\s*G?B)', selected)
            if size_match:
                self.usb_info_var.set(f"Capacity: {size_match.group(1)}")
            else:
                self.usb_info_var.set("")
        else:
            self.usb_info_var.set("")

    def start_usb_creation(self):
        """Start creating bootable USB."""
        iso_path = self.iso_source_path.get()
        usb_target = self.target_usb.get()

        # Validation
        if not iso_path:
            messagebox.showerror("Error", "Please select an ISO file.")
            return
        if not os.path.exists(iso_path):
            messagebox.showerror("Error", f"ISO file not found:\n{iso_path}")
            return
        if not usb_target or "No USB" in usb_target:
            messagebox.showerror("Error", "Please select a USB drive.")
            return

        # Safety confirmation
        if not messagebox.askyesno("Warning - Data Loss",
                                   f"⚠️ ALL DATA on the USB drive will be ERASED!\n\n"
                                   f"Target: {usb_target}\n\n"
                                   f"Are you sure you want to continue?"):
            return

        # Start the operation
        self.is_converting = True
        self.start_time = datetime.now()

        # Reset progress
        self.bytes_copied = 0
        self.total_bytes = os.path.getsize(iso_path)
        self.last_speed_time = None
        self.last_speed_bytes = 0
        self.current_speed = 0
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")
        self.bytes_label.configure(text="")

        self.start_btn.configure(state=tk.DISABLED, bg=self.s.BORDER)
        self.cancel_btn.configure(state=tk.NORMAL, bg=self.s.DANGER, fg=self.s.WHITE)
        self.update_progress(0)
        self.status_var.set("◐ Preparing...")
        self.log(f"Creating bootable USB from {os.path.basename(iso_path)}")
        self.log(f"Target: {usb_target}")
        self.log(f"Boot mode: {self.boot_mode.get()}")

        # Start elapsed timer
        self.start_elapsed_timer()

        # Run in background thread
        threading.Thread(target=self._run_usb_creation, args=(iso_path, usb_target), daemon=True).start()

    def _run_usb_creation(self, iso_path, usb_target):
        """Background thread for USB creation."""
        try:
            # Determine write method based on ISO type
            if self.detected_iso_type == 'linux_hybrid':
                self.root.after(0, lambda: self.log("Using DD mode (Linux hybrid ISO)"))
                if platform.system() == "Windows":
                    self._write_usb_dd_windows(iso_path, usb_target)
                elif platform.system() == "Darwin":
                    self._write_usb_dd_macos(iso_path, usb_target)
                else:
                    self._write_usb_dd_linux(iso_path, usb_target)
            elif self.detected_iso_type == 'windows':
                # Windows ISOs need extract mode with dual partition
                self.root.after(0, lambda: self.log("Using Extract mode (Windows ISO - FAT32+NTFS)"))
                if platform.system() == "Windows":
                    self._write_usb_extract_windows(iso_path, usb_target)
                elif platform.system() == "Darwin":
                    self._write_usb_extract_macos(iso_path, usb_target)
                else:
                    # Linux can use similar approach
                    self._write_usb_extract_linux(iso_path, usb_target)
            else:
                # Unknown ISOs - try DD mode, works for most bootable ISOs
                self.root.after(0, lambda: self.log("Using DD mode (unknown ISO type)"))
                if platform.system() == "Windows":
                    self._write_usb_dd_windows(iso_path, usb_target)
                elif platform.system() == "Darwin":
                    self._write_usb_dd_macos(iso_path, usb_target)
                else:
                    self._write_usb_dd_linux(iso_path, usb_target)

            if self.is_converting:
                self.root.after(0, self._usb_done, True, "Bootable USB created successfully!")
        except Exception as e:
            if self.is_converting:
                self.root.after(0, self._usb_done, False, str(e))

    def _write_usb_dd_windows(self, iso_path, usb_target):
        """Write ISO to USB using DD mode on Windows."""
        # Extract disk number from target string
        disk_match = re.search(r'\[?Disk\s*(\d+)\]?', usb_target, re.IGNORECASE)
        if not disk_match:
            # Try to get disk number from drive letter
            letter_match = re.search(r'([A-Z]):', usb_target)
            if letter_match:
                letter = letter_match.group(1)
                # Get disk number from letter
                r = subprocess.run(['powershell', '-Command',
                    f"(Get-Partition -DriveLetter '{letter}').DiskNumber"],
                    capture_output=True, text=True, timeout=10,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                disk_num = r.stdout.strip()
            else:
                raise Exception("Could not determine disk number")
        else:
            disk_num = disk_match.group(1)

        self.root.after(0, lambda: self.log(f"Target disk: {disk_num}", min_verbosity=2))

        # PowerShell script to write ISO to disk
        script = f'''
$ErrorActionPreference = "Stop"
$diskNum = {disk_num}
$isoPath = "{iso_path}"

Write-Host "STATUS:Clearing disk..."
[Console]::Out.Flush()

# Clear the disk
Clear-Disk -Number $diskNum -RemoveData -RemoveOEM -Confirm:$false -ErrorAction SilentlyContinue

Write-Host "STATUS:Opening files..."
[Console]::Out.Flush()

# Get file size
$fileInfo = Get-Item $isoPath
$totalSize = $fileInfo.Length

Write-Host ("SIZE:" + $totalSize)
[Console]::Out.Flush()

# Open files
$iso = [System.IO.File]::OpenRead($isoPath)
$disk = [System.IO.File]::OpenWrite("\\\\.\\PhysicalDrive$diskNum")

# Write with progress
$bufSize = 4194304  # 4MB buffer
$buf = New-Object byte[] $bufSize
$total = [long]0
$lastPct = -1

Write-Host "STATUS:Writing ISO to USB..."
Write-Host "PROGRESS:0:0:$totalSize"
[Console]::Out.Flush()

try {{
    while ($true) {{
        $n = $iso.Read($buf, 0, $bufSize)
        if ($n -le 0) {{ break }}

        $disk.Write($buf, 0, $n)
        $total += $n

        $pct = [int](($total / $totalSize) * 100)
        if ($pct -ne $lastPct) {{
            Write-Host ("PROGRESS:" + $pct + ":" + $total + ":" + $totalSize)
            [Console]::Out.Flush()
            $lastPct = $pct
        }}
    }}
}} finally {{
    $iso.Close()
    $disk.Close()
}}

Write-Host "PROGRESS:100:$total:$totalSize"
Write-Host "STATUS:Complete"
[Console]::Out.Flush()
'''
        self.process = subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        self._monitor_with_bytes()

    def _write_usb_dd_macos(self, iso_path, usb_target):
        """Write ISO to USB using DD mode on macOS."""
        # Extract disk path
        disk_match = re.search(r'(/dev/disk\d+)', usb_target)
        if not disk_match:
            raise Exception("Could not determine disk path")

        disk_path = disk_match.group(1)
        raw_disk = disk_path.replace('/dev/disk', '/dev/rdisk')  # Use raw device for speed

        self.root.after(0, lambda: self.log(f"Target: {disk_path}", min_verbosity=2))

        # Unmount the disk first
        subprocess.run(['diskutil', 'unmountDisk', disk_path], capture_output=True)

        # Use dd to write
        self.process = subprocess.Popen(
            ['dd', f'if={iso_path}', f'of={raw_disk}', 'bs=4m', 'status=progress'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Monitor dd output (progress is on stderr)
        total_size = os.path.getsize(iso_path)
        while self.process.poll() is None and self.is_converting:
            line = self.process.stderr.readline()
            if line and 'bytes' in line:
                m = re.search(r'(\d+)\s+bytes', line)
                if m:
                    bytes_written = int(m.group(1))
                    pct = min(99, int((bytes_written / total_size) * 100))
                    self.root.after(0, lambda p=pct, b=bytes_written, t=total_size:
                                   self.update_progress(p, bytes_copied=b, total_bytes=t))

        if self.process.returncode and self.is_converting:
            raise Exception(self.process.stderr.read() or "dd failed")

    def _write_usb_dd_linux(self, iso_path, usb_target):
        """Write ISO to USB using DD mode on Linux."""
        # Extract device path
        dev_match = re.search(r'(/dev/\w+)', usb_target)
        if not dev_match:
            raise Exception("Could not determine device path")

        device = dev_match.group(1)
        self.root.after(0, lambda: self.log(f"Target: {device}", min_verbosity=2))

        # Use dd with progress
        self.process = subprocess.Popen(
            ['dd', f'if={iso_path}', f'of={device}', 'bs=4M', 'status=progress', 'conv=fsync'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        total_size = os.path.getsize(iso_path)
        while self.process.poll() is None and self.is_converting:
            line = self.process.stderr.readline()
            if line and 'bytes' in line:
                m = re.search(r'(\d+)\s+bytes', line)
                if m:
                    bytes_written = int(m.group(1))
                    pct = min(99, int((bytes_written / total_size) * 100))
                    self.root.after(0, lambda p=pct, b=bytes_written, t=total_size:
                                   self.update_progress(p, bytes_copied=b, total_bytes=t))

        if self.process.returncode and self.is_converting:
            raise Exception(self.process.stderr.read() or "dd failed")

    def _write_usb_extract_windows(self, iso_path, usb_target):
        """Write Windows ISO using extract mode with dual partition (FAT32 EFI + NTFS data)."""
        # Extract disk number from target string
        disk_match = re.search(r'\[?Disk\s*(\d+)\]?', usb_target, re.IGNORECASE)
        if not disk_match:
            letter_match = re.search(r'([A-Z]):', usb_target)
            if letter_match:
                letter = letter_match.group(1)
                r = subprocess.run(['powershell', '-Command',
                    f"(Get-Partition -DriveLetter '{letter}').DiskNumber"],
                    capture_output=True, text=True, timeout=10,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                disk_num = r.stdout.strip()
            else:
                raise Exception("Could not determine disk number")
        else:
            disk_num = disk_match.group(1)

        self.root.after(0, lambda: self.log(f"Target disk: {disk_num}", min_verbosity=2))
        self.root.after(0, lambda: self.status_var.set("◐ Partitioning USB..."))

        # PowerShell script to partition and copy Windows ISO
        script = f'''
$ErrorActionPreference = "Stop"
$diskNum = {disk_num}
$isoPath = "{iso_path}"

Write-Host "STATUS:Clearing disk $diskNum..."
[Console]::Out.Flush()

# Clear the disk completely
try {{
    Clear-Disk -Number $diskNum -RemoveData -RemoveOEM -Confirm:$false -ErrorAction SilentlyContinue
}} catch {{
    # Disk might already be clean
}}

# Initialize with MBR for BIOS compatibility
Write-Host "STATUS:Initializing disk with MBR..."
[Console]::Out.Flush()
Initialize-Disk -Number $diskNum -PartitionStyle MBR -ErrorAction SilentlyContinue

# Get disk size
$disk = Get-Disk -Number $diskNum
$diskSizeGB = [math]::Round($disk.Size / 1GB, 2)
Write-Host "STATUS:Disk size: $diskSizeGB GB"
[Console]::Out.Flush()

# Calculate partition sizes
# FAT32 partition: 1GB for EFI boot files
# NTFS partition: Rest of the disk for Windows files (handles >4GB)
$fatSizeMB = 1024

Write-Host "STATUS:Creating FAT32 boot partition (1 GB)..."
[Console]::Out.Flush()

# Create FAT32 partition first (will get a drive letter)
$fatPartition = New-Partition -DiskNumber $diskNum -Size ($fatSizeMB * 1MB) -AssignDriveLetter
$fatLetter = $fatPartition.DriveLetter
Format-Volume -DriveLetter $fatLetter -FileSystem FAT32 -NewFileSystemLabel "BOOT" -Confirm:$false | Out-Null

Write-Host "STATUS:Creating NTFS data partition..."
[Console]::Out.Flush()

# Create NTFS partition with remaining space
$ntfsPartition = New-Partition -DiskNumber $diskNum -UseMaximumSize -AssignDriveLetter
$ntfsLetter = $ntfsPartition.DriveLetter
Format-Volume -DriveLetter $ntfsLetter -FileSystem NTFS -NewFileSystemLabel "WINDOWS_USB" -Confirm:$false | Out-Null

# Set FAT32 partition as active (for BIOS boot)
Set-Partition -DriveLetter $fatLetter -IsActive $true

Write-Host "STATUS:FAT32 = $fatLetter`:, NTFS = $ntfsLetter`:"
[Console]::Out.Flush()

# Mount the ISO
Write-Host "STATUS:Mounting ISO..."
[Console]::Out.Flush()
$mountResult = Mount-DiskImage -ImagePath $isoPath -PassThru
$isoVolume = Get-Volume -DiskImage $mountResult
$isoLetter = $isoVolume.DriveLetter
Write-Host "STATUS:ISO mounted at $isoLetter`:"
[Console]::Out.Flush()

# Count total files for progress
Write-Host "STATUS:Analyzing ISO contents..."
[Console]::Out.Flush()
$allFiles = Get-ChildItem -Path "$isoLetter`:\" -Recurse -File -ErrorAction SilentlyContinue
$totalFiles = $allFiles.Count
$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum
Write-Host ("SIZE:" + $totalSize)
Write-Host "STATUS:Found $totalFiles files to copy"
[Console]::Out.Flush()

$copiedFiles = 0
$copiedBytes = [long]0

# Function to copy with progress
function Copy-WithProgress {{
    param($source, $dest, $description)

    $files = Get-ChildItem -Path $source -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {{
        $relativePath = $file.FullName.Substring($source.Length)
        $destPath = Join-Path $dest $relativePath
        $destDir = Split-Path $destPath -Parent

        if (-not (Test-Path $destDir)) {{
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }}

        Copy-Item -Path $file.FullName -Destination $destPath -Force
        $script:copiedBytes += $file.Length
        $script:copiedFiles++

        $pct = [int](($script:copiedBytes / $totalSize) * 100)
        if ($pct -gt 99) {{ $pct = 99 }}
        Write-Host ("PROGRESS:" + $pct + ":" + $script:copiedBytes + ":" + $totalSize)
        [Console]::Out.Flush()
    }}
}}

# Copy EFI boot files to FAT32 partition
Write-Host "STATUS:Copying EFI boot files to FAT32 partition..."
[Console]::Out.Flush()

# Copy EFI folder
if (Test-Path "$isoLetter`:\\efi") {{
    Copy-WithProgress -source "$isoLetter`:\\efi" -dest "$fatLetter`:\\efi" -description "EFI"
}}

# Copy boot folder for BIOS
if (Test-Path "$isoLetter`:\\boot") {{
    Copy-WithProgress -source "$isoLetter`:\\boot" -dest "$fatLetter`:\\boot" -description "boot"
}}

# Copy bootmgr files for BIOS boot
$bootFiles = @("bootmgr", "bootmgr.efi")
foreach ($bootFile in $bootFiles) {{
    if (Test-Path "$isoLetter`:\\$bootFile") {{
        Copy-Item "$isoLetter`:\\$bootFile" "$fatLetter`:\\$bootFile" -Force
        $fileSize = (Get-Item "$isoLetter`:\\$bootFile").Length
        $copiedBytes += $fileSize
    }}
}}

Write-Host "STATUS:Copying Windows files to NTFS partition..."
[Console]::Out.Flush()

# Copy ALL files to NTFS partition (including large install.wim)
Copy-WithProgress -source "$isoLetter`:\" -dest "$ntfsLetter`:\" -description "Windows files"

# Unmount ISO
Write-Host "STATUS:Unmounting ISO..."
[Console]::Out.Flush()
Dismount-DiskImage -ImagePath $isoPath | Out-Null

Write-Host "PROGRESS:100:$copiedBytes:$totalSize"
Write-Host "STATUS:Bootable USB created successfully!"
[Console]::Out.Flush()
'''
        self.process = subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        self._monitor_with_bytes()

    def _write_usb_extract_macos(self, iso_path, usb_target):
        """Write Windows ISO using extract mode on macOS (FAT32 EFI + ExFAT data)."""
        # Extract disk path
        disk_match = re.search(r'(/dev/disk\d+)', usb_target)
        if not disk_match:
            raise Exception("Could not determine disk path")

        disk_path = disk_match.group(1)
        self.root.after(0, lambda: self.log(f"Target: {disk_path}", min_verbosity=2))
        self.root.after(0, lambda: self.status_var.set("◐ Partitioning USB..."))

        # Unmount the disk first
        subprocess.run(['diskutil', 'unmountDisk', disk_path], capture_output=True)

        # Get disk size for partition calculation
        r = subprocess.run(['diskutil', 'info', disk_path], capture_output=True, text=True)
        disk_size_bytes = 0
        for line in r.stdout.split('\n'):
            if 'Disk Size' in line:
                m = re.search(r'\((\d+)\s*Bytes\)', line)
                if m:
                    disk_size_bytes = int(m.group(1))
                    break

        self.root.after(0, lambda: self.log(f"Disk size: {self.format_size(disk_size_bytes)}", min_verbosity=2))

        # Partition the disk with MBR scheme
        # FAT32 (1GB) for EFI boot + ExFAT for data (macOS can't easily create NTFS)
        self.root.after(0, lambda: self.log("Creating partitions (FAT32 + ExFAT)..."))

        # Use diskutil to partition
        # Format: MBR with FAT32 (BOOT) and ExFAT (WINDOWS_USB)
        result = subprocess.run([
            'diskutil', 'partitionDisk', disk_path,
            'MBR',
            'FAT32', 'BOOT', '1G',
            'ExFAT', 'WINDOWS_USB', 'R'  # R = remaining space
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Partitioning failed: {result.stderr}")

        # Find the new partition mount points
        import time
        time.sleep(2)  # Wait for partitions to mount

        boot_volume = None
        data_volume = None

        r = subprocess.run(['diskutil', 'list', disk_path], capture_output=True, text=True)
        for line in r.stdout.split('\n'):
            if 'BOOT' in line:
                parts = line.split()
                if parts:
                    boot_volume = f"/Volumes/BOOT"
            elif 'WINDOWS_USB' in line:
                data_volume = f"/Volumes/WINDOWS_USB"

        if not boot_volume or not data_volume:
            # Try to find by listing /Volumes
            if os.path.exists('/Volumes/BOOT'):
                boot_volume = '/Volumes/BOOT'
            if os.path.exists('/Volumes/WINDOWS_USB'):
                data_volume = '/Volumes/WINDOWS_USB'

        if not boot_volume or not data_volume:
            raise Exception("Could not find mounted partitions")

        self.root.after(0, lambda: self.log(f"Boot: {boot_volume}, Data: {data_volume}", min_verbosity=2))

        # Mount the ISO
        self.root.after(0, lambda: self.log("Mounting ISO..."))
        import tempfile
        iso_mount = tempfile.mkdtemp(prefix="win_iso_")
        result = subprocess.run(['hdiutil', 'attach', iso_path, '-mountpoint', iso_mount, '-nobrowse'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to mount ISO: {result.stderr}")

        try:
            # Count files for progress
            self.root.after(0, lambda: self.log("Analyzing ISO contents..."))
            total_size = 0
            file_list = []
            for root, dirs, files in os.walk(iso_mount):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        total_size += sz
                        file_list.append((fp, sz))
                    except:
                        pass

            self.total_bytes = total_size
            self.root.after(0, lambda: self.log(f"Total: {len(file_list)} files, {self.format_size(total_size)}"))

            copied_bytes = 0

            # Copy EFI and boot files to FAT32 partition
            self.root.after(0, lambda: self.log("Copying boot files to FAT32..."))
            boot_dirs = ['efi', 'EFI', 'boot', 'BOOT']
            boot_files = ['bootmgr', 'bootmgr.efi', 'BOOTMGR', 'BOOTMGR.EFI']

            for bd in boot_dirs:
                src_dir = os.path.join(iso_mount, bd)
                if os.path.exists(src_dir):
                    dst_dir = os.path.join(boot_volume, bd)
                    for root, dirs, files in os.walk(src_dir):
                        for f in files:
                            src_file = os.path.join(root, f)
                            rel_path = os.path.relpath(src_file, src_dir)
                            dst_file = os.path.join(dst_dir, rel_path)
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            try:
                                import shutil
                                shutil.copy2(src_file, dst_file)
                                sz = os.path.getsize(src_file)
                                copied_bytes += sz
                                pct = min(99, int((copied_bytes / total_size) * 100))
                                self.root.after(0, lambda p=pct, b=copied_bytes:
                                              self.update_progress(p, bytes_copied=b, total_bytes=total_size))
                            except Exception as e:
                                self.root.after(0, lambda e=e: self.log(f"Copy error: {e}", "warning", min_verbosity=3))

            for bf in boot_files:
                src_file = os.path.join(iso_mount, bf)
                if os.path.exists(src_file):
                    import shutil
                    shutil.copy2(src_file, os.path.join(boot_volume, bf))

            # Copy all files to ExFAT partition
            self.root.after(0, lambda: self.log("Copying Windows files to ExFAT..."))
            import shutil
            for src_file, sz in file_list:
                if not self.is_converting:
                    break
                rel_path = os.path.relpath(src_file, iso_mount)
                dst_file = os.path.join(data_volume, rel_path)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                try:
                    shutil.copy2(src_file, dst_file)
                    copied_bytes += sz
                    pct = min(99, int((copied_bytes / total_size) * 100))
                    self.root.after(0, lambda p=pct, b=copied_bytes:
                                  self.update_progress(p, bytes_copied=b, total_bytes=total_size))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.log(f"Copy error: {e}", "warning", min_verbosity=3))

            self.bytes_copied = copied_bytes

        finally:
            # Unmount ISO
            subprocess.run(['hdiutil', 'detach', iso_mount], capture_output=True)
            try:
                os.rmdir(iso_mount)
            except:
                pass

        self.root.after(0, lambda: self.log("Windows USB created successfully!"))

    def _write_usb_extract_linux(self, iso_path, usb_target):
        """Write Windows ISO using extract mode on Linux (FAT32 EFI + NTFS data)."""
        # Extract device path
        dev_match = re.search(r'(/dev/\w+)', usb_target)
        if not dev_match:
            raise Exception("Could not determine device path")

        device = dev_match.group(1)
        self.root.after(0, lambda: self.log(f"Target: {device}", min_verbosity=2))
        self.root.after(0, lambda: self.status_var.set("◐ Partitioning USB..."))

        # Unmount any existing partitions
        subprocess.run(['umount', f'{device}*'], capture_output=True, shell=True)

        # Create MBR partition table with parted
        self.root.after(0, lambda: self.log("Creating partition table..."))
        subprocess.run(['parted', '-s', device, 'mklabel', 'msdos'], capture_output=True)

        # Create FAT32 partition (1GB) and NTFS partition (rest)
        subprocess.run(['parted', '-s', device, 'mkpart', 'primary', 'fat32', '1MiB', '1025MiB'], capture_output=True)
        subprocess.run(['parted', '-s', device, 'mkpart', 'primary', 'ntfs', '1025MiB', '100%'], capture_output=True)
        subprocess.run(['parted', '-s', device, 'set', '1', 'boot', 'on'], capture_output=True)

        import time
        time.sleep(2)  # Wait for partition table to be recognized

        # Format partitions
        fat_part = f"{device}1"
        ntfs_part = f"{device}2"

        self.root.after(0, lambda: self.log("Formatting FAT32 partition..."))
        subprocess.run(['mkfs.fat', '-F', '32', '-n', 'BOOT', fat_part], capture_output=True)

        self.root.after(0, lambda: self.log("Formatting NTFS partition..."))
        subprocess.run(['mkfs.ntfs', '-f', '-L', 'WINDOWS_USB', ntfs_part], capture_output=True)

        # Create mount points
        import tempfile
        fat_mount = tempfile.mkdtemp(prefix="boot_")
        ntfs_mount = tempfile.mkdtemp(prefix="data_")
        iso_mount = tempfile.mkdtemp(prefix="iso_")

        try:
            # Mount partitions
            subprocess.run(['mount', fat_part, fat_mount], capture_output=True)
            subprocess.run(['mount', ntfs_part, ntfs_mount], capture_output=True)

            # Mount ISO
            self.root.after(0, lambda: self.log("Mounting ISO..."))
            result = subprocess.run(['mount', '-o', 'loop,ro', iso_path, iso_mount], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to mount ISO: {result.stderr}")

            # Count files for progress
            total_size = 0
            file_list = []
            for root, dirs, files in os.walk(iso_mount):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        total_size += sz
                        file_list.append((fp, sz))
                    except:
                        pass

            self.total_bytes = total_size
            copied_bytes = 0

            # Copy boot files to FAT32
            self.root.after(0, lambda: self.log("Copying boot files to FAT32..."))
            import shutil
            boot_items = ['efi', 'EFI', 'boot', 'BOOT', 'bootmgr', 'bootmgr.efi', 'BOOTMGR']
            for item in boot_items:
                src = os.path.join(iso_mount, item)
                if os.path.exists(src):
                    dst = os.path.join(fat_mount, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)

            # Copy all files to NTFS
            self.root.after(0, lambda: self.log("Copying Windows files to NTFS..."))
            for src_file, sz in file_list:
                if not self.is_converting:
                    break
                rel_path = os.path.relpath(src_file, iso_mount)
                dst_file = os.path.join(ntfs_mount, rel_path)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                try:
                    shutil.copy2(src_file, dst_file)
                    copied_bytes += sz
                    pct = min(99, int((copied_bytes / total_size) * 100))
                    self.root.after(0, lambda p=pct, b=copied_bytes:
                                  self.update_progress(p, bytes_copied=b, total_bytes=total_size))
                except Exception as e:
                    pass

            self.bytes_copied = copied_bytes

        finally:
            # Unmount everything
            subprocess.run(['umount', iso_mount], capture_output=True)
            subprocess.run(['umount', fat_mount], capture_output=True)
            subprocess.run(['umount', ntfs_mount], capture_output=True)
            try:
                os.rmdir(iso_mount)
                os.rmdir(fat_mount)
                os.rmdir(ntfs_mount)
            except:
                pass

    def _usb_done(self, ok, msg):
        """USB creation finished."""
        self.is_converting = False
        self.process = None
        self.stop_elapsed_timer()
        self.start_btn.configure(state=tk.NORMAL, bg=self.s.PRIMARY)
        self.cancel_btn.configure(state=tk.DISABLED, bg=self.s.BG, fg=self.s.TEXT_SECONDARY)

        if ok:
            self.update_progress(100, bytes_copied=self.total_bytes, total_bytes=self.total_bytes)
            self.status_var.set("✓ Complete")
            self.log(msg, "success")

            if self.start_time:
                el = int((datetime.now() - self.start_time).total_seconds())
                self.log(f"Time: {el//60:02d}:{el%60:02d}")

                if self.bytes_copied > 0 and el > 0:
                    avg_speed = self.bytes_copied / el
                    self.log(f"Average speed: {self.format_speed(avg_speed)}", min_verbosity=2)

            messagebox.showinfo("Success", f"{msg}\n\nYou can now safely eject the USB drive.")
        else:
            self.status_var.set("✗ Failed")
            self.log(f"Error: {msg}", "error")
            messagebox.showerror("Error", msg)

    def cancel_usb_creation(self):
        """Cancel USB creation."""
        if self.is_converting and messagebox.askyesno("Cancel?", "Stop USB creation?"):
            self.is_converting = False
            self.stop_elapsed_timer()
            if self.process:
                self.process.terminate()

            self.status_var.set("Cancelled")
            self.log("USB creation cancelled", "warning")
            self.start_btn.configure(state=tk.NORMAL, bg=self.s.PRIMARY)
            self.cancel_btn.configure(state=tk.DISABLED, bg=self.s.BG, fg=self.s.TEXT_SECONDARY)


def main():
    root = tk.Tk()

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = DVDtoISOConverter(root)

    # Window size - taller to fit new UI elements
    w, h = 650, 850
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(580, 800)

    root.mainloop()


if __name__ == "__main__":
    main()
