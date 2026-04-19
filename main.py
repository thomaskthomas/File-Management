from pathlib import Path
import shutil
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ─── Core Logic ───────────────────────────────────────────────────────────────

class FileOrganizer:

    FILE_TYPES: dict[str, list[str]] = {
        "Image_Files":      ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        "Video_Files":      ['.mp4', '.mkv', '.avi', '.mov', '.flv'],
        "Audio_Files":      ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
        "Executable_Files": ['.exe', '.bat', '.sh', '.msi', '.apk'],
        "TXT_Files":        ['.txt'],
        "PDF_Files":        ['.pdf'],
        "Word_Files":       ['.docx', '.doc'],
        "Excel_Files":      ['.xlsx', '.xls', '.csv'],
    }

    def __init__(self, source: str):
        self.source_folder = Path(source)
        self._ext_map: dict[str, str] = {
            ext: folder
            for folder, exts in self.FILE_TYPES.items()
            for ext in exts
        }
        self._validate_source()

    def _validate_source(self):
        if not self.source_folder.exists():
            raise FileNotFoundError(f"Source folder not found: {self.source_folder}")
        if not self.source_folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.source_folder}")

    def _get_target_folder(self, extension: str) -> str:
        return self._ext_map.get(extension, "Other_Files")

    def _move_file(self, file: Path, target_folder_name: str) -> bool:
        target_folder = self.source_folder / target_folder_name
        target_folder.mkdir(exist_ok=True)
        destination = target_folder / file.name
        counter = 1
        while destination.exists():
            destination = target_folder / f"{file.stem}_{counter}{file.suffix}"
            counter += 1
        shutil.move(str(file), str(destination))
        return True

    def organize(self, progress_cb=None) -> dict[str, int]:
        stats = {"moved": 0, "skipped": 0, "failed": 0}
        files = [f for f in self.source_folder.iterdir()]
        total = len(files)

        for i, file in enumerate(files):
            if file.is_dir():
                stats["skipped"] += 1
            else:
                try:
                    target = self._get_target_folder(file.suffix.lower())
                    self._move_file(file, target)
                    stats["moved"] += 1
                    if progress_cb:
                        progress_cb(i + 1, total, f"Moved: {file.name}")
                except (OSError, shutil.Error) as e:
                    logger.warning("Failed to move '%s': %s", file.name, e)
                    stats["failed"] += 1
                    if progress_cb:
                        progress_cb(i + 1, total, f"Failed: {file.name}")

        return stats


# ─── GUI ──────────────────────────────────────────────────────────────────────

# Palette
BG        = "#0f1117"
SURFACE   = "#1a1d27"
BORDER    = "#2a2d3a"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bfa"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
ERROR     = "#ef4444"
TEXT      = "#e2e8f0"
SUBTEXT   = "#94a3b8"
FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI Semibold", 12)
FONT_TITLE= ("Segoe UI Light", 22)


class FileOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer")
        self.geometry("680x600")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._folder_var = tk.StringVar()
        self._running = False

        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(28, 0))

        tk.Label(
            header, text="File Organizer", font=FONT_TITLE,
            bg=BG, fg=TEXT
        ).pack(side="left")

        tk.Label(
            header, text="v1.0", font=("Segoe UI", 9),
            bg=BG, fg=SUBTEXT
        ).pack(side="left", padx=(8, 0), pady=(12, 0))

        # ── Divider ───────────────────────────────────────────────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(14, 0))

        # ── Folder picker ─────────────────────────────────────────────────
        picker_frame = tk.Frame(self, bg=BG)
        picker_frame.pack(fill="x", padx=30, pady=(22, 0))

        tk.Label(
            picker_frame, text="Source folder", font=FONT_HEAD,
            bg=BG, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            picker_frame,
            text="Select the directory whose files you want to organise.",
            font=("Segoe UI", 9), bg=BG, fg=SUBTEXT
        ).pack(anchor="w", pady=(2, 10))

        entry_row = tk.Frame(picker_frame, bg=BG)
        entry_row.pack(fill="x")

        self._path_entry = tk.Entry(
            entry_row, textvariable=self._folder_var,
            font=FONT_MONO, bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT2,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self._path_entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=6)

        browse_btn = tk.Button(
            entry_row, text=" Browse ",
            font=FONT_UI, bg=SURFACE, fg=ACCENT2,
            activebackground=BORDER, activeforeground=ACCENT,
            relief="flat", bd=0, cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER,
            command=self._browse
        )
        browse_btn.pack(side="left", padx=(8, 0), ipady=8, ipadx=4)

        # ── File-type reference card ───────────────────────────────────────
        card = tk.Frame(self, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(
            card, text="Recognised types", font=("Segoe UI Semibold", 9),
            bg=SURFACE, fg=SUBTEXT
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(10, 6))

        types = list(FileOrganizer.FILE_TYPES.items())
        for idx, (folder, exts) in enumerate(types):
            r, c = divmod(idx, 2)
            label = folder.replace("_Files", "").replace("_", " ")
            ext_str = "  " + "  ".join(exts[:3]) + ("…" if len(exts) > 3 else "")

            tk.Label(
                card, text=f"● {label}", font=("Segoe UI", 9),
                bg=SURFACE, fg=ACCENT2, anchor="w"
            ).grid(row=r + 1, column=c * 2, sticky="w", padx=(14, 2), pady=2)

            tk.Label(
                card, text=ext_str, font=("Courier New", 8),
                bg=SURFACE, fg=SUBTEXT, anchor="w"
            ).grid(row=r + 1, column=c * 2 + 1, sticky="w", padx=(0, 14), pady=2)

        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(3, weight=1)

        # Pad bottom of card
        tk.Frame(card, bg=SURFACE, height=8).grid(
            row=len(types) // 2 + 2, columnspan=4
        )

        # ── Progress bar ──────────────────────────────────────────────────
        prog_frame = tk.Frame(self, bg=BG)
        prog_frame.pack(fill="x", padx=30, pady=(20, 0))

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=SURFACE,
            background=ACCENT,
            bordercolor=BORDER,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=6
        )

        self._progress = ttk.Progressbar(
            prog_frame, style="Custom.Horizontal.TProgressbar",
            orient="horizontal", length=620, mode="determinate"
        )
        self._progress.pack(fill="x")

        self._status_var = tk.StringVar(value="Ready.")
        tk.Label(
            prog_frame, textvariable=self._status_var,
            font=("Courier New", 9), bg=BG, fg=SUBTEXT, anchor="w"
        ).pack(anchor="w", pady=(4, 0))

        # ── Log box ───────────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=30, pady=(14, 0))

        self._log = tk.Text(
            log_frame, height=7,
            font=FONT_MONO, bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT2,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            state="disabled", wrap="word"
        )
        self._log.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(self._log, command=self._log.yview, bg=BORDER)
        scrollbar.pack(side="right", fill="y")
        self._log.configure(yscrollcommand=scrollbar.set)

        # Tag colours for log entries
        self._log.tag_configure("info",    foreground=TEXT)
        self._log.tag_configure("success", foreground=SUCCESS)
        self._log.tag_configure("warning", foreground=WARNING)
        self._log.tag_configure("error",   foreground=ERROR)
        self._log.tag_configure("dim",     foreground=SUBTEXT)

        # ── Action button ─────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=30, pady=(16, 28))

        self._organise_btn = tk.Button(
            btn_row,
            text="  Organise Files  ",
            font=("Segoe UI Semibold", 11),
            bg=ACCENT, fg="#ffffff",
            activebackground=ACCENT2, activeforeground="#ffffff",
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=10,
            command=self._start_organise
        )
        self._organise_btn.pack(side="right")

        self._clear_btn = tk.Button(
            btn_row, text="Clear log",
            font=("Segoe UI", 9), bg=BG, fg=SUBTEXT,
            activebackground=BG, activeforeground=TEXT,
            relief="flat", bd=0, cursor="hand2",
            command=self._clear_log
        )
        self._clear_btn.pack(side="right", padx=(0, 14))

    # ── Actions ────────────────────────────────────────────────────────────

    def _browse(self):
        folder = filedialog.askdirectory(title="Select source folder")
        if folder:
            self._folder_var.set(folder)

    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
        self._progress["value"] = 0
        self._status_var.set("Ready.")

    def _start_organise(self):
        if self._running:
            return
        path = self._folder_var.get().strip()
        if not path:
            messagebox.showwarning("No folder selected", "Please choose a source folder first.")
            return
        self._running = True
        self._organise_btn.configure(state="disabled", text="  Working…  ")
        self._progress["value"] = 0
        threading.Thread(target=self._run_organiser, args=(path,), daemon=True).start()

    def _run_organiser(self, path: str):
        try:
            organizer = FileOrganizer(path)
        except (FileNotFoundError, NotADirectoryError) as e:
            self.after(0, self._finish, None, str(e))
            return

        self._log_line(f"Starting organiser on: {path}", "dim")

        def on_progress(done, total, msg):
            pct = (done / total * 100) if total else 0
            self.after(0, lambda: self._progress.configure(value=pct))
            self.after(0, lambda: self._status_var.set(f"{done}/{total}  {msg}"))
            tag = "warning" if msg.startswith("Failed") else "info"
            self.after(0, lambda m=msg, t=tag: self._log_line(m, t))

        stats = organizer.organize(progress_cb=on_progress)
        self.after(0, self._finish, stats, None)

    def _finish(self, stats, error: str | None):
        self._running = False
        self._organise_btn.configure(state="normal", text="  Organise Files  ")
        self._progress["value"] = 100 if not error else 0

        if error:
            self._log_line(f"Error: {error}", "error")
            self._status_var.set("Failed.")
            messagebox.showerror("Error", error)
        else:
            summary = (
                f"Done — {stats['moved']} moved, "
                f"{stats['skipped']} skipped, "
                f"{stats['failed']} failed."
            )
            self._log_line(summary, "success")
            self._status_var.set(summary)

    def _log_line(self, text: str, tag: str = "info"):
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()