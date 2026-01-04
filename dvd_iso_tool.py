#!/usr/bin/env python3
"""
DVD to ISO Converter Tool
Phase 1: Convert DVD to ISO
Phase 2 (planned): Burn ISO to DVD
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import platform
import re
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
        
        self.setup_window()
        self.create_ui()
        self.root.after(100, self.detect_drives)
    
    def setup_window(self):
        """Configure window."""
        self.root.title("DVD to ISO Converter")
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
        main = tk.Frame(self.root, bg=s.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Configure grid weights for proper expansion
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(4, weight=1)  # Log section expands
        
        # === HEADER ===
        header = tk.Frame(main, bg=s.BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        tk.Label(header, text="💿", font=(s.FONT, 24), bg=s.BG, fg=s.PRIMARY).pack(side=tk.LEFT, padx=(0, 12))
        
        title_area = tk.Frame(header, bg=s.BG)
        title_area.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(title_area, text="DVD to ISO Converter", font=s.TITLE, bg=s.BG, fg=s.TEXT).pack(anchor="w")
        tk.Label(title_area, text="Create perfect backups of your discs", font=s.SMALL, bg=s.BG, fg=s.TEXT_SECONDARY).pack(anchor="w")
        
        badge = tk.Frame(header, bg=s.PRIMARY, padx=10, pady=3)
        badge.pack(side=tk.RIGHT)
        tk.Label(badge, text="PHASE 1", font=(s.FONT, 8, "bold"), bg=s.PRIMARY, fg=s.WHITE).pack()
        
        # === SOURCE DRIVE ===
        src_card = self.make_card(main, row=1)
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
        out_card = self.make_card(main, row=2)
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

        # === PROGRESS ===
        prog_card = self.make_card(main, row=3)
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
        log_card = self.make_card(main, row=4, expand=True)

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
        btn_frame = tk.Frame(main, bg=s.BG)
        btn_frame.grid(row=5, column=0, sticky="ew", pady=(12, 0))

        self.start_btn = tk.Button(btn_frame, text="▶  START CONVERSION", font=(s.FONT, 11, "bold"),
                                   bg=s.PRIMARY, fg=s.WHITE, activebackground=s.PRIMARY_HOVER,
                                   activeforeground=s.WHITE, relief=tk.FLAT, pady=10, cursor="hand2",
                                   command=self.start_conversion)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.cancel_btn = tk.Button(btn_frame, text="✕  CANCEL", font=s.BODY,
                                    bg=s.BG, fg=s.TEXT_SECONDARY, activebackground=s.DANGER,
                                    activeforeground=s.WHITE, relief=tk.SOLID, bd=1, pady=10, padx=20,
                                    cursor="hand2", state=tk.DISABLED, command=self.cancel_conversion)
        self.cancel_btn.pack(side=tk.RIGHT)

        # Auto-eject checkbox
        self.eject_check = tk.Checkbutton(btn_frame, text="Auto-eject", variable=self.auto_eject,
                                          font=s.SMALL, bg=s.BG, fg=s.TEXT_SECONDARY,
                                          activebackground=s.BG, selectcolor=s.BG, cursor="hand2")
        self.eject_check.pack(side=tk.RIGHT, padx=(0, 15))
        
        # Tab order: combo -> refresh -> entry -> browse -> start -> cancel
        self.drive_combo.lift()
        self.refresh_btn.lift()
        self.output_entry.lift()
        self.browse_btn.lift()
        self.start_btn.lift()
        self.cancel_btn.lift()
    
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
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")

        # Get volume info
        vol = ctypes.create_unicode_buffer(1024)
        fs = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetVolumeInformationW(f"{letter}:\\", vol, 1024, None, None, None, fs, 1024)

        label = vol.value or "Unknown"
        filesystem = fs.value or "Unknown"

        # Get size via PowerShell
        try:
            r = subprocess.run(['powershell', '-Command',
                f'(Get-Volume -DriveLetter "{letter}").Size'],
                capture_output=True, text=True, timeout=5,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            size = int(r.stdout.strip()) if r.stdout.strip() else 0
            size_str = self.format_size(size)
        except:
            size_str = "Unknown"

        disc_type = "DVD" if drive_type == 5 else "CD"
        return f"{disc_type} | {label} | {size_str} | {filesystem}"

    def _get_disc_info_linux(self, device):
        """Get disc info on Linux."""
        info_parts = []

        # Get disc type and size
        try:
            r = subprocess.run(['blockdev', '--getsize64', device], capture_output=True, text=True, timeout=5)
            size = int(r.stdout.strip()) if r.stdout.strip() else 0
            self.total_bytes = size  # Store for progress calculation
            disc_type = "DVD" if size > 700 * 1024 * 1024 else "CD"
            info_parts.append(disc_type)
            info_parts.append(self.format_size(size))
        except:
            pass

        # Get label
        try:
            r = subprocess.run(['blkid', '-o', 'value', '-s', 'LABEL', device],
                             capture_output=True, text=True, timeout=5)
            label = r.stdout.strip()
            if label:
                info_parts.insert(1, label)
        except:
            pass

        # Get filesystem
        try:
            r = subprocess.run(['blkid', '-o', 'value', '-s', 'TYPE', device],
                             capture_output=True, text=True, timeout=5)
            fs = r.stdout.strip()
            if fs:
                info_parts.append(fs.upper())
        except:
            pass

        return " | ".join(info_parts) if info_parts else "Disc inserted"

    def _get_disc_info_macos(self, device):
        """Get disc info on macOS."""
        try:
            r = subprocess.run(['diskutil', 'info', device], capture_output=True, text=True, timeout=5)
            info = {}
            for line in r.stdout.split('\n'):
                if ':' in line:
                    key, _, value = line.partition(':')
                    info[key.strip()] = value.strip()

            name = info.get('Volume Name', 'Unknown')
            size = info.get('Total Size', info.get('Disk Size', 'Unknown'))
            fs = info.get('File System Personality', info.get('Type (Bundle)', 'Unknown'))

            # Extract size number
            if size and 'Unknown' not in size:
                # Parse size like "4.7 GB (4700000000 Bytes)"
                size_match = re.search(r'[\d.]+\s*[GMKT]B', size)
                size = size_match.group(0) if size_match else size.split()[0]

            disc_type = "DVD" if 'DVD' in str(info) else "CD"
            return f"{disc_type} | {name} | {size} | {fs}"
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


def main():
    root = tk.Tk()
    
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = DVDtoISOConverter(root)
    
    # Window size - taller to fit new UI elements
    w, h = 650, 800
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(580, 750)
    
    root.mainloop()


if __name__ == "__main__":
    main()
