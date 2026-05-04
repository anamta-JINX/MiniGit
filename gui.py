import os
import sys
import re
import shlex
import threading
import traceback
import contextlib
from io import StringIO
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

import core


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


class Theme:
    # CustomTkinter tuple colors = (light_mode, dark_mode)

    APP_BG = ("#F7F1E3", "#050505")
    MAIN_BG = ("#FBF7EC", "#070707")
    SIDEBAR_BG = ("#EFE2C2", "#0D0D0D")

    PANEL_BG = ("#FFF9EC", "#11100D")
    PANEL_BG_2 = ("#F3E6C6", "#17140E")
    INPUT_BG = ("#FFFDF6", "#080808")
    OUTPUT_BG = ("#FFFDF7", "#030303")

    GOLD = "#D4AF37"
    GOLD_LIGHT = "#F5D76E"
    GOLD_DARK = "#9A761D"
    BRONZE = "#8A6A24"

    TEXT = ("#1C1608", "#F7F3E8")
    MUTED = ("#6E5A25", "#A79B7C")
    SUBTLE = ("#9B884B", "#6F6652")

    BUTTON = ("#F5E8C4", "#1A1710")
    BUTTON_HOVER = ("#E7D29A", "#2A2214")
    BUTTON_BORDER = ("#B9912E", "#3C2F12")

    PRIMARY_TEXT = ("#111111", "#050505")

    DANGER_BG = ("#F4D6D6", "#241010")
    DANGER_HOVER = ("#E8BABA", "#3A1515")
    DANGER_TEXT = ("#6B1111", "#F3D8D8")
    DANGER_BORDER = ("#B35A5A", "#5A2020")


class MiniGitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MiniGit Pro")
        self.geometry("1240x780")
        self.minsize(1080, 680)

        ctk.set_appearance_mode("dark")

        self.configure(fg_color=Theme.APP_BG)

        self.project_dir = Path.cwd()
        self.command_lock = threading.Lock()
        self.logo_image = None

        self.set_window_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

        self.write_banner()
        self.run_command(["manual"])

    # --------------------------------------------------
    # Resource / Logo Helpers
    # --------------------------------------------------

    def resource_path(self, relative_path):
        """
        Finds files both in normal Python mode and PyInstaller .exe mode.
        """

        try:
            if getattr(sys, "frozen", False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent

            return base_path / relative_path

        except Exception:
            return Path(relative_path)

    def load_logo(self):
        """
        Loads logo image for the sidebar.
        Expected path:
        assets/logo.png
        """

        logo_path = self.resource_path("assets/logo.png")

        if not logo_path.exists():
            return None

        try:
            logo_image = Image.open(logo_path)

            return ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(82, 82)
            )

        except Exception:
            return None

    def set_window_icon(self):
        """
        Sets app window icon when running from Python.
        For .exe icon, use PyInstaller --icon command.
        """

        try:
            icon_path = self.resource_path("assets/logo.ico")

            if icon_path.exists():
                self.iconbitmap(str(icon_path))

        except Exception:
            pass

    # --------------------------------------------------
    # Reusable UI helpers
    # --------------------------------------------------

    def gold_button(self, parent, text, command, height=38):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            corner_radius=12,
            fg_color=Theme.BUTTON,
            hover_color=Theme.BUTTON_HOVER,
            text_color=Theme.TEXT,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )

    def primary_button(self, parent, text, command, height=38):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            corner_radius=12,
            fg_color=Theme.GOLD_DARK,
            hover_color=Theme.GOLD,
            text_color=Theme.PRIMARY_TEXT
        )

    def danger_button(self, parent, text, command, height=38):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            corner_radius=12,
            fg_color=Theme.DANGER_BG,
            hover_color=Theme.DANGER_HOVER,
            text_color=Theme.DANGER_TEXT,
            border_width=1,
            border_color=Theme.DANGER_BORDER
        )

    # --------------------------------------------------
    # UI Layout
    # --------------------------------------------------

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=300,
            corner_radius=0,
            fg_color=Theme.SIDEBAR_BG
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(18, weight=1)

        self.logo_image = self.load_logo()

        self.logo_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=Theme.PANEL_BG,
            corner_radius=22,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )
        self.logo_card.grid(row=0, column=0, padx=18, pady=(22, 14), sticky="ew")
        self.logo_card.grid_columnconfigure(0, weight=1)

        if self.logo_image:
            self.logo_icon = ctk.CTkLabel(
                self.logo_card,
                image=self.logo_image,
                text=""
            )
            self.logo_icon.grid(row=0, column=0, padx=18, pady=(16, 6))

        self.logo_text = ctk.CTkLabel(
            self.logo_card,
            text="MiniGit Pro",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=Theme.GOLD_DARK
        )
        self.logo_text.grid(row=1, column=0, padx=18, pady=(0, 2))

        self.subtitle = ctk.CTkLabel(
            self.logo_card,
            text="Premium Local Version Control",
            font=ctk.CTkFont(size=12),
            text_color=Theme.MUTED
        )
        self.subtitle.grid(row=2, column=0, padx=18, pady=(0, 16))

        self.repo_label = ctk.CTkLabel(
            self.sidebar,
            text="Repository Folder",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.TEXT
        )
        self.repo_label.grid(row=1, column=0, padx=22, pady=(4, 6), sticky="w")

        self.repo_display = ctk.CTkTextbox(
            self.sidebar,
            height=58,
            corner_radius=14,
            fg_color=Theme.INPUT_BG,
            text_color=Theme.MUTED,
            border_width=1,
            border_color=Theme.BUTTON_BORDER,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.repo_display.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")
        self.repo_display.insert("1.0", str(self.project_dir))
        self.repo_display.configure(state="disabled")

        self.folder_btn = self.primary_button(
            self.sidebar,
            "Open Folder",
            self.choose_folder,
            height=38
        )
        self.folder_btn.grid(row=3, column=0, padx=18, pady=(0, 18), sticky="ew")

        buttons = [
            ("Initialize Repo", self.init_repo),
            ("Status", lambda: self.run_command(["status"])),
            ("Commit Log", lambda: self.run_command(["log"])),
            ("Commit Graph", lambda: self.run_command(["graph"])),
            ("Objects DB", lambda: self.run_command(["objects"])),
            ("Repo Stats", lambda: self.run_command(["stats"])),
            ("Tracked Files", lambda: self.run_command(["ls-files"])),
            ("Manual", lambda: self.run_command(["manual"])),
        ]

        start_row = 4
        for index, (text, command) in enumerate(buttons):
            btn = self.gold_button(self.sidebar, text, command, height=36)
            btn.grid(row=start_row + index, column=0, padx=18, pady=4, sticky="ew")

        self.clear_btn = self.gold_button(
            self.sidebar,
            "Clear Output",
            self.clear_output,
            height=36
        )
        self.clear_btn.grid(row=18, column=0, padx=18, pady=(20, 8), sticky="sew")

        self.theme_btn = self.primary_button(
            self.sidebar,
            "Toggle Theme",
            self.toggle_theme,
            height=36
        )
        self.theme_btn.grid(row=19, column=0, padx=18, pady=(0, 22), sticky="sew")

    def create_main_area(self):
        self.main = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=Theme.MAIN_BG
        )
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        self.header = ctk.CTkFrame(self.main, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=26, pady=(24, 10))
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="MiniGit Pro Control Center",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Theme.GOLD_DARK
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.path_label = ctk.CTkLabel(
            self.header,
            text=f"Running in: {self.project_dir}",
            font=ctk.CTkFont(size=13),
            text_color=Theme.MUTED
        )
        self.path_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        self.brand_line = ctk.CTkFrame(
            self.main,
            height=2,
            fg_color=Theme.GOLD_DARK,
            corner_radius=2
        )
        self.brand_line.grid(row=0, column=0, sticky="ew", padx=26, pady=(76, 0))

        self.actions = ctk.CTkFrame(
            self.main,
            fg_color=Theme.PANEL_BG,
            corner_radius=20,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )
        self.actions.grid(row=1, column=0, sticky="ew", padx=26, pady=12)

        for col in range(5):
            self.actions.grid_columnconfigure(col, weight=1)

        action_buttons = [
            ("Add File", self.add_file),
            ("Add Folder", self.add_folder),
            ("Add All", lambda: self.run_command(["add", "."])),
            ("Diff File", self.diff_file),
            ("Restore File", self.restore_file),
            ("Remove File", self.remove_file),
            ("Show Commit", self.show_commit_dialog),
            ("Cat Object", self.cat_object_dialog),
            ("Reset Stage", lambda: self.run_command(["reset"])),
            ("Ignore Sample", lambda: self.run_command(["ignore-sample"])),
        ]

        for index, (text, command) in enumerate(action_buttons):
            row = index // 5
            col = index % 5

            if text in ["Add File", "Add Folder", "Add All"]:
                btn = self.primary_button(self.actions, text, command)
            elif text in ["Remove File", "Reset Stage"]:
                btn = self.danger_button(self.actions, text, command)
            else:
                btn = self.gold_button(self.actions, text, command)

            btn.grid(row=row, column=col, padx=8, pady=8, sticky="ew")

        self.commit_panel = ctk.CTkFrame(
            self.main,
            fg_color=Theme.PANEL_BG,
            corner_radius=20,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )
        self.commit_panel.grid(row=2, column=0, sticky="ew", padx=26, pady=(0, 12))
        self.commit_panel.grid_columnconfigure(0, weight=1)

        self.commit_entry = ctk.CTkEntry(
            self.commit_panel,
            placeholder_text='Commit message, e.g. "initial premium snapshot"',
            height=44,
            corner_radius=14,
            fg_color=Theme.INPUT_BG,
            text_color=Theme.TEXT,
            placeholder_text_color=Theme.SUBTLE,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )
        self.commit_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        self.commit_btn = self.primary_button(
            self.commit_panel,
            "Commit Snapshot",
            self.commit,
            height=44
        )
        self.commit_btn.configure(width=170)
        self.commit_btn.grid(row=0, column=1, padx=(0, 12), pady=12)

        self.output_frame = ctk.CTkFrame(
            self.main,
            fg_color=Theme.MAIN_BG,
            corner_radius=0
        )
        self.output_frame.grid(row=3, column=0, sticky="nsew", padx=26, pady=(0, 12))
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output = ctk.CTkTextbox(
            self.output_frame,
            corner_radius=20,
            fg_color=Theme.OUTPUT_BG,
            text_color=Theme.TEXT,
            border_width=1,
            border_color=Theme.BUTTON_BORDER,
            font=ctk.CTkFont(family="Consolas", size=14),
            wrap="word"
        )
        self.output.grid(row=0, column=0, sticky="nsew")

        self.command_bar = ctk.CTkFrame(
            self.main,
            fg_color=Theme.PANEL_BG,
            corner_radius=18,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )
        self.command_bar.grid(row=4, column=0, sticky="ew", padx=26, pady=(0, 24))
        self.command_bar.grid_columnconfigure(0, weight=1)

        self.command_entry = ctk.CTkEntry(
            self.command_bar,
            placeholder_text="Run command, e.g. status / graph / diff demo_project.txt",
            height=42,
            corner_radius=14,
            fg_color=Theme.INPUT_BG,
            text_color=Theme.TEXT,
            placeholder_text_color=Theme.SUBTLE,
            border_width=1,
            border_color=Theme.BUTTON_BORDER
        )
        self.command_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        self.command_entry.bind("<Return>", lambda event: self.run_custom_command())

        self.run_btn = self.primary_button(
            self.command_bar,
            "Run",
            self.run_custom_command,
            height=42
        )
        self.run_btn.configure(width=96)
        self.run_btn.grid(row=0, column=1, padx=(0, 12), pady=12)

    # --------------------------------------------------
    # Core Command Runner
    # --------------------------------------------------

    def run_command(self, args):
        thread = threading.Thread(
            target=self._run_command_worker,
            args=(args,),
            daemon=True
        )
        thread.start()

    def _run_command_worker(self, args):
        with self.command_lock:
            display_command = " ".join(["python", "core.py"] + args)

            self.append_output("\n")
            self.append_output(f"▶ {display_command}\n\n")

            old_cwd = os.getcwd()
            old_argv = sys.argv[:]

            buffer = StringIO()

            try:
                os.chdir(self.project_dir)
                sys.argv = ["core.py"] + args

                with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                    core.main()

                output_text = buffer.getvalue()

                if output_text.strip():
                    self.append_output(output_text + "\n")
                else:
                    self.append_output("No output returned.\n")

            except SystemExit:
                output_text = buffer.getvalue()

                if output_text.strip():
                    self.append_output(output_text + "\n")

            except Exception:
                output_text = buffer.getvalue()

                if output_text.strip():
                    self.append_output(output_text + "\n")

                self.append_output("GUI command error:\n")
                self.append_output(traceback.format_exc() + "\n")

            finally:
                sys.argv = old_argv
                os.chdir(old_cwd)

    def strip_ansi(self, text):
        return ANSI_ESCAPE.sub("", text)

    def append_output(self, text):
        text = self.strip_ansi(text)

        def write():
            self.output.configure(state="normal")
            self.output.insert("end", text)
            self.output.see("end")
            self.output.configure(state="normal")

        self.after(0, write)

    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="normal")
        self.write_banner()

    # --------------------------------------------------
    # Button Actions
    # --------------------------------------------------

    def init_repo(self):
        self.run_command(["init"])

    def add_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file to stage",
            initialdir=self.project_dir
        )

        if not file_path:
            return

        relative = self.relative_path(file_path)
        self.run_command(["add", relative])

    def add_folder(self):
        folder_path = filedialog.askdirectory(
            title="Select folder to stage",
            initialdir=self.project_dir
        )

        if not folder_path:
            return

        relative = self.relative_path(folder_path)
        self.run_command(["add", relative])

    def commit(self):
        message = self.commit_entry.get().strip()

        if not message:
            messagebox.showwarning(
                "Missing Commit Message",
                "Please write a commit message first."
            )
            return

        self.run_command(["commit", message])
        self.commit_entry.delete(0, "end")

    def diff_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file to diff",
            initialdir=self.project_dir
        )

        if not file_path:
            return

        relative = self.relative_path(file_path)
        self.run_command(["diff", relative])

    def restore_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file to restore",
            initialdir=self.project_dir
        )

        if not file_path:
            return

        relative = self.relative_path(file_path)

        commit_id = self.simple_input(
            "Restore File",
            "Optional commit ID. Leave empty to restore from HEAD:"
        )

        if commit_id:
            self.run_command(["restore", relative, commit_id])
        else:
            self.run_command(["restore", relative])

    def remove_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file to remove from MiniGit",
            initialdir=self.project_dir
        )

        if not file_path:
            return

        relative = self.relative_path(file_path)

        confirm = messagebox.askyesno(
            "Remove File",
            f"This will delete and stage removal:\n\n{relative}\n\nContinue?"
        )

        if confirm:
            self.run_command(["rm", relative])

    def show_commit_dialog(self):
        commit_id = self.simple_input(
            "Show Commit",
            "Enter commit ID or prefix:"
        )

        if commit_id:
            self.run_command(["show", commit_id])

    def cat_object_dialog(self):
        object_hash = self.simple_input(
            "Cat Object",
            "Enter object hash or prefix:"
        )

        if object_hash:
            self.run_command(["cat", object_hash])

    def run_custom_command(self):
        raw = self.command_entry.get().strip()

        if not raw:
            return

        try:
            args = shlex.split(raw)
        except ValueError as error:
            messagebox.showerror("Invalid Command", str(error))
            return

        self.run_command(args)
        self.command_entry.delete(0, "end")

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Choose MiniGit Project Folder",
            initialdir=self.project_dir
        )

        if not folder:
            return

        self.project_dir = Path(folder)

        self.repo_display.configure(state="normal")
        self.repo_display.delete("1.0", "end")
        self.repo_display.insert("1.0", str(self.project_dir))
        self.repo_display.configure(state="disabled")

        self.path_label.configure(text=f"Running in: {self.project_dir}")

        self.clear_output()
        self.run_command(["manual"])

    def relative_path(self, path):
        path = Path(path)

        try:
            return str(path.relative_to(self.project_dir))
        except ValueError:
            return str(path)

    def simple_input(self, title, prompt):
        dialog = ctk.CTkInputDialog(text=prompt, title=title)
        value = dialog.get_input()

        if value is None:
            return ""

        return value.strip()

    def toggle_theme(self):
        current = ctk.get_appearance_mode()

        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="Dark Theme")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="Light Theme")

    def write_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              MiniGit Pro GUI                                ║
║                 Premium local control center for your VCS                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

"""
        self.output.configure(state="normal")
        self.output.insert("end", banner)
        self.output.configure(state="normal")