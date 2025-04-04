# Copyright 2025 Karma3u
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import re
import subprocess
import threading
import time # Import time for potential delays or checks
import sys # To get platform for path separators

class K3U_Installer_GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("K3U Installer GUI")
        # Main window size
        self.main_width = 950
        self.main_height = 750
        self.master.geometry(f"{self.main_width}x{self.main_height}")

        # --- State Variables ---
        self.k3u_data = None
        self.selected_setup_key = None
        self.current_setup_data = None
        self.current_k3u_type = "external_venv" # Default type
        self.total_steps_for_progress = 0
        self.worker_thread = None
        self.user_inputs = {} # Stores user choices {input_key: selected_value_string}
        self._config_vars = {} # Stores tk.StringVar for config window {input_key: tk.StringVar}
        self.placeholders = {} # Stores resolved placeholder values
        self._flash_after_id = None # ID for the flashing animation timer
        self._is_flashing = False # Flag to control flashing state

        # --- Log File Setup ---
        self.log_file = "install_log.txt"
        try:
            # Clear log file on start
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"=== Log Installazione K3U ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
        except IOError as e:
            print(f"Errore apertura log file '{self.log_file}': {e}")
            messagebox.showwarning("Log Error", f"Unable to write to log file:\n{e}\nIl logging su file sarà disabilitato.")
            messagebox.showwarning("Log Error", "File logging will be disabled.")
            self.log_file = None # Disable file logging if opening failed

        self.setup_ui()

    def setup_ui(self):
        # --- Top Frame for Paths ---
        top_frame = ttk.Frame(self.master, padding="10")
        top_frame.pack(fill=tk.X)

        # --- Installation Path Frame ---
        path_frame = ttk.Frame(top_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(path_frame, text="Installation Base Path:", width=22, anchor="w").pack(side=tk.LEFT)
        self.install_path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.install_path_var, width=60)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.browse_path_button = ttk.Button(path_frame, text="Browse 📁.", command=self.choose_install_path)
        self.browse_path_button.pack(side=tk.LEFT, padx=5)

        # --- Python Executable Frame (State depends on K3U type) ---
        python_frame = ttk.Frame(top_frame)
        python_frame.pack(fill=tk.X)
        self.python_label = ttk.Label(python_frame, text="Python exe. Target:", width=22, anchor="w")
        self.python_label.pack(side=tk.LEFT)
        self.python_exe_var = tk.StringVar()
        self.python_entry = ttk.Entry(python_frame, textvariable=self.python_exe_var, width=60)
        self.python_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.browse_python_button = ttk.Button(python_frame, text="Browse 📁.", command=self.choose_python_exe)
        self.browse_python_button.pack(side=tk.LEFT, padx=5)
        self.python_label.config(state="normal")
        self.python_entry.config(state="normal")
        self.browse_python_button.config(state="normal")


        # --- K3U File Frame ---
        self.file_frame = ttk.Frame(self.master, padding="10")
        self.file_frame.pack(fill=tk.X)
        ttk.Label(self.file_frame, text="File K3U:", width=22, anchor="w").pack(side=tk.LEFT) # Added width for alignment
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.browse_button = ttk.Button(self.file_frame, text="Browse 📁.", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT)

        # --- Setup Selection and Info Frame ---
        self.setup_frame = ttk.LabelFrame(self.master, text="Setup Selection", padding="10")
        self.setup_frame.pack(fill=tk.X, padx=10, pady=5)

        setup_select_frame = ttk.Frame(self.setup_frame)
        setup_select_frame.pack(fill=tk.X)
        ttk.Label(setup_select_frame, text="Available Setups:").pack(side=tk.LEFT)
        self.setup_var = tk.StringVar()
        self.setup_combobox = ttk.Combobox(setup_select_frame, textvariable=self.setup_var, state="disabled", width=40)
        self.setup_combobox.pack(side=tk.LEFT, padx=10)
        self.setup_combobox.bind("<<ComboboxSelected>>", self.on_setup_selected)

        # Description
        self.description_label = ttk.Label(self.setup_frame, text="Description:", font=('TkDefaultFont', 10, 'bold'))
        self.description_label.pack(fill=tk.X, pady=(10, 0), anchor='w')
        self.description_text = tk.StringVar()
        self.description_value = ttk.Label(self.setup_frame, textvariable=self.description_text, wraplength=self.main_width - 100, justify=tk.LEFT)
        self.description_value.pack(fill=tk.X, anchor='w')

        # Info
        self.info_label = ttk.Label(self.setup_frame, text="Info:", font=('TkDefaultFont', 10, 'bold'))
        self.info_label.pack(fill=tk.X, pady=(5, 0), anchor='w')
        self.info_text = tk.StringVar()
        self.info_value = ttk.Label(self.setup_frame, textvariable=self.info_text, wraplength=self.main_width - 100, justify=tk.LEFT)
        self.info_value.pack(fill=tk.X, anchor='w')

        # --- Log Area Frame ---
        self.log_frame = ttk.LabelFrame(self.master, text="Installation Log", padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, height=15, state="disabled", font=("Courier New", 9), bg="black", fg="lime")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # Configure tags for colored logging
        self.log_text.tag_config("ERROR", foreground="red", font=("Courier New", 9, "bold"))
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("INFO", foreground="cyan")
        self.log_text.tag_config("SUCCESS", foreground="lightgreen")
        self.log_text.tag_config("STEP", foreground="yellow", font=("Courier New", 9, "bold"))
        self.log_text.tag_config("CMD", foreground="white")
        self.log_text.tag_config("OUTPUT", foreground="#cccccc") # Light gray for output


        # --- Progress Bar ---
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.master, maximum=100, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(5, 0)) # Padding adjusted


        # --- Control Frame (Modified Layout) ---
        self.control_frame = ttk.Frame(self.master, padding="10")
        self.control_frame.pack(fill=tk.X, pady=(5, 10))

        # Start Button (Left)
        self.start_button = ttk.Button(self.control_frame, text="Summary and Start", command=self.open_config_window, state="disabled")
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Reset Button (Right)
        self.reset_button = ttk.Button(self.control_frame, text="Reset", command=self.reset_ui)
        self.reset_button.pack(side=tk.RIGHT, padx=5)

        # Status Display Frame (Middle, expands) - NEW
        self.status_display_frame = ttk.Frame(self.control_frame)
        # Packed later when needed (in start_flashing)
        # self.status_display_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        # Flashing Indicator Label (inside status frame) - NEW
        self.flash_label = ttk.Label(self.status_display_frame, text="", width=3, font=("Courier New", 10, "bold"))
        self.flash_label.pack(side=tk.LEFT, padx=(0, 5))

        # Status Text Label (inside status frame) - NEW
        self.status_label_var = tk.StringVar(value="") # Initially empty
        self.status_label = ttk.Label(self.status_display_frame, textvariable=self.status_label_var, anchor="w")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)


    # --- Methods for Status/Flashing ---

    def update_status_text(self, text):
        """Updates the status label text."""
        try:
            self.status_label_var.set(text)
        except tk.TclError:
             # Handle error if the window/widget is destroyed during update
             print("Warning: Could not update status text (widget destroyed?).")


    def _animate_status(self, state=0):
        """Internal method to animate the flashing label."""
        if not self._is_flashing: # Stop if flashing was cancelled
             self.flash_label.config(text="")
             return

        # Simple animation: [*] / [-]
        new_text = "[*]" if state == 0 else "[-]"
        foreground_color = "lime" if state == 0 else "orange"

        try:
            self.flash_label.config(text=new_text, foreground=foreground_color)
            # Schedule next frame
            self._flash_after_id = self.master.after(400, self._animate_status, 1 - state)
        except tk.TclError:
             # Handle error if the window/widget is destroyed during update
             print("Warning: Could not animate status (widget destroyed?).")
             self._is_flashing = False


    def start_flashing(self):
        """Starts the flashing animation and shows the status frame."""
        if not self._is_flashing:
            self._is_flashing = True
            # Make the status frame visible by packing it
            # Pack reset button first to ensure it stays on the right
            self.reset_button.pack_forget()
            self.status_display_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
            self.reset_button.pack(side=tk.RIGHT, padx=5) # Re-pack reset button
            self.update_status_text("Avvio...") # Initial text
            self._animate_status(0) # Start animation

    def stop_flashing(self):
        """Stops the flashing animation and hides the status frame."""
        if self._is_flashing:
            self._is_flashing = False
            if self._flash_after_id:
                try:
                    self.master.after_cancel(self._flash_after_id)
                except tk.TclError:
                     pass # Ignore if timer already cancelled or window destroyed
            self._flash_after_id = None
            try:
                self.flash_label.config(text="") # Clear flash label
                # Hide the status frame
                self.status_display_frame.pack_forget()
            except tk.TclError:
                 pass # Ignore if widgets already destroyed

    # --- Rest of the methods ---

    def reset_ui(self):
        """Resets the UI elements to their initial state."""
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Attention", "Cannot reset while an installation is in progress.")
            return

        self.install_path_var.set("")
        self.python_exe_var.set("")
        self.file_path_var.set("")
        self.setup_var.set("")
        self.description_text.set("")
        self.info_text.set("")
        self.setup_combobox.set("")
        self.setup_combobox.config(state="disabled", values=[])
        self.start_button.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state="disabled")
        self.progress_var.set(0)
        self.k3u_data = None
        self.selected_setup_key = None
        self.current_setup_data = None
        self.current_k3u_type = "external_venv" # Reset type
        self.user_inputs = {}
        self._config_vars = {}
        self.placeholders = {}
        # Stop flashing and clear status on reset
        self.stop_flashing()
        self.update_status_text("") # Clear status text too
        self.enable_controls() # Ensure controls are enabled after reset
        # Re-enable Python input by default on reset
        self.python_label.config(state="normal")
        self.python_entry.config(state="normal")
        self.browse_python_button.config(state="normal")
        self.log("UI Resettata.", tag="INFO")

    def log(self, message, tag=None, is_error=False):
        """Appends a message to the log text area and optionally to a file."""
        if tag is None and is_error:
            tag = "ERROR"

        def append_log():
            try:
                self.log_text.config(state="normal")
                if tag:
                    self.log_text.insert(tk.END, message + "\n", tag)
                else:
                    self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state="disabled")
            except tk.TclError:
                 print(f"Warning: Log widget destroyed, could not log: {message}")


        self.master.after(0, append_log)

        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    timestamp = time.strftime('%H:%M:%S')
                    log_prefix = f"[{timestamp}] "
                    if tag:
                         log_prefix += f"[{tag}] "
                    f.write(log_prefix + message + "\n")
            except IOError as e:
                if not hasattr(self, '_log_file_error_shown'):
                    print(f"Error writing log file '{self.log_file}': {e}")
                    self._log_file_error_shown = True

    def browse_file(self):
        """Opens a dialog to select the K3U JSON file."""
        if self.worker_thread and self.worker_thread.is_alive(): return
        filepath = filedialog.askopenfilename(
            title="Seleziona File K3U",
            filetypes=[("K3U files", "*.k3u"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.file_path_var.set(filepath)
            self.load_k3u_file()

    def choose_install_path(self):
        """Opens a dialog to select the base installation directory."""
        if self.worker_thread and self.worker_thread.is_alive(): return
        path = filedialog.askdirectory(title="Scegli cartella base per l'installazione")
        if path:
            self.install_path_var.set(path)
            self.log(f"Base installation path set to: {path}", tag="INFO")

    def choose_python_exe(self):
        """Opens a dialog to select the target Python executable."""
        if self.worker_thread and self.worker_thread.is_alive(): return
        filetypes = [("Python Executable", "python.exe"), ("All files", "*.*")] if sys.platform == "win32" else [("Python Executable", "python*"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(
            title="Select the target Python executable (if required by K3U)",
            filetypes=filetypes
        )
        if filepath:
            self.python_exe_var.set(filepath)
            self.log(f"Python executable target set to: {filepath}", tag="INFO")


    def load_k3u_file(self):
        """Loads and parses the selected K3U JSON file and determines its type."""
        filepath = self.file_path_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Errore", "Invalid or missing K3U file.")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.k3u_data = json.load(f)

            if "setups" not in self.k3u_data or not isinstance(self.k3u_data["setups"], dict) or not self.k3u_data["setups"]:
                messagebox.showerror("Errore", "The K3U file does not contain a valid or empty 'setups' section.")
                self.reset_ui()
                return

            self.current_k3u_type = self.k3u_data.get("k3u_type", "external_venv")
            self.log(f"Type K3U detected: {self.current_k3u_type}", tag="INFO")

            if self.current_k3u_type == "embedded":
                self.python_label.config(state="disabled")
                self.python_entry.config(state="disabled")
                self.browse_python_button.config(state="disabled")
                self.python_exe_var.set("")
                self.log("Input Python Target disabled (setup embedded).", tag="INFO")
            else:
                self.python_label.config(state="normal")
                self.python_entry.config(state="normal")
                self.browse_python_button.config(state="normal")
                self.log("Input Python Target enabled.", tag="INFO")


            keys = list(self.k3u_data["setups"].keys())
            self.setup_combobox['values'] = keys
            self.setup_combobox.config(state="readonly")
            self.setup_combobox.set(keys[0])
            self.on_setup_selected()
            self.log(f"File K3U uploaded: {filepath}", tag="SUCCESS")
            self.log(f"Available setups: {', '.join(keys)}", tag="INFO")

        except json.JSONDecodeError as e:
            err_msg = f"Error parsing the K3U file (invalid JSON):\n{e.msg}\nLinea: {e.lineno}, Colonna: {e.colno}"
            messagebox.showerror("Errore JSON", err_msg)
            self.reset_ui()
        except Exception as e:
            messagebox.showerror("Errore", f"Unexpected error while loading the K3U file.\n{e}")
            self.reset_ui()

    # get_step_order is no longer needed

    def on_setup_selected(self, event=None):
        """Updates UI elements when a setup is selected from the combobox."""
        if not self.k3u_data: return

        self.log_text.config(state="normal")
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state="disabled")

        self.selected_setup_key = self.setup_var.get()
        setup = self.k3u_data["setups"].get(self.selected_setup_key)
        if not setup:
             messagebox.showerror("Internal Error", f"Setup '{self.selected_setup_key}' not found in the loaded data")
             return
        self.current_setup_data = setup

        self.description_text.set(setup.get("description", "No description provided."))
        self.info_text.set(setup.get("info", "No additional information available.."))
        self.start_button.config(state="normal")

        self.log(f"--- Setup Preview: {self.selected_setup_key} ---", tag="INFO")

        steps = setup.get("steps", [])
        if not steps:
             self.log("(No steps defined for this setup!)", tag="WARNING")

        for step_info in steps:
            key = step_info.get("key", "CHIAVE_MANCANTE")
            step_data = step_info.get("step_data")
            self.log(f"[{key.upper()}]", tag="STEP")

            if isinstance(step_data, list):
                if not step_data:
                     self.log("  (No action defined)")
                for item in step_data:
                    if isinstance(item, dict):
                        descr = item.get("name", "Unrecognized element.")
                        cmd = item.get("command", "")
                        # Log custom message if present for preview
                        msg = item.get("message", "")
                        log_extra = f" (Msg: {msg})" if msg else (f" (Cmd: {cmd[:60]}{'...' if len(cmd)>60 else ''})" if cmd else "")
                        self.log(f"  - {descr}{log_extra}")
                    elif isinstance(item, str):
                        self.log(f"  - Comando: {item}")
                    else:
                         self.log(f"  - Unrecognized element. {item}", tag="WARNING")

            elif isinstance(step_data, dict) and key.startswith("input"):
                question = step_data.get("question", f"Input requested for {key}")
                self.log(f"  ? {question}")
                choices = step_data.get("choices", {})
                if not choices:
                     self.log("    (No selection defined!)", tag="WARNING")
                else:
                    is_first = True
                    for choice_key, choice_content in choices.items():
                        prefix = "[*]" if is_first else "[ ]"
                        self.log(f"    {prefix} {choice_key}")
                        choice_steps = choice_content.get("steps", [])
                        if choice_steps:
                             for c_item in choice_steps:
                                 if isinstance(c_item, dict):
                                     c_descr = c_item.get("name", "Unnamed action")
                                     c_cmd = c_item.get("command", "")
                                     c_msg = c_item.get("message","")
                                     c_log_extra = f" (Msg: {c_msg})" if c_msg else (f" (Cmd: {c_cmd[:50]}{'...' if len(c_cmd)>50 else ''})" if c_cmd else "")
                                     self.log(f"      -> {c_descr}{c_log_extra}")
                                 elif isinstance(c_item, str):
                                     self.log(f"      -> Comando: {c_item}")
                        is_first = False
            elif isinstance(step_data, dict):
                 self.log(f"  (Specific details for {key} not displayed in the preview)", tag="INFO")
            else:
                 self.log(f"  Type of data not recognized for the step '{key}': {type(step_data)}", tag="WARNING")
        self.log("--- End preview ---", tag="INFO")

    def open_config_window(self):
        """Opens a Toplevel window showing a summary of all steps
           and allowing configuration of input steps."""
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Attention", "Window not available during installation.")
            return
        if not self.current_setup_data:
            messagebox.showerror("Error", "No selected setup.")
            return

        config_win = tk.Toplevel(self.master)
        config_win.title("Summary and setup configuration")
        config_win.geometry(f"{self.main_width - 20}x{self.main_height - 70}")
        config_win.minsize(600, 400)
        config_win.resizable(True, True)

        config_win.grab_set()
        config_win.transient(self.master)

        ttk.Label(config_win, text=f"Plan for: {self.selected_setup_key}", font=("Arial", 12, "bold")).pack(pady=10)

        steps_frame = ttk.Frame(config_win)
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(steps_frame)
        scrollbar = ttk.Scrollbar(steps_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=(10, 5))

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _configure_scrollable_frame(event):
             canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _configure_scrollable_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._config_vars.clear()
        setup_data = self.current_setup_data
        steps = setup_data.get("steps", [])

        style = ttk.Style()
        style.configure("Step.TLabel", font=("Arial", 10, "bold"))
        style.configure("Desc.TLabel", foreground="#333333")
        style.configure("InputQ.TLabel", font=("Arial", 10, "bold"), foreground="darkgreen")
        style.configure("Action.TLabel", foreground="gray", font=('TkDefaultFont', 8))

        if not steps:
             ttk.Label(scrollable_frame, text="(No step defined for this setup!)").pack(anchor="w", padx=5)

        initial_wraplength = self.main_width - 80

        for step_info in steps:
            key = step_info.get("key", "CHIAVE_MANCANTE")
            step_data = step_info.get("step_data")

            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=(10, 5), padx=5)
            ttk.Label(scrollable_frame, text=f"Step: {key.upper()}", style="Step.TLabel").pack(anchor="w", padx=5)

            if isinstance(step_data, list):
                if not step_data:
                    ttk.Label(scrollable_frame, text="(No defined action)", style="Desc.TLabel", foreground="gray").pack(anchor="w", padx=20)
                for item_index, item in enumerate(step_data):
                    display_text = f"{item_index+1}. "
                    if isinstance(item, dict):
                        descr = item.get("name", "Nameless action")
                        display_text += f"{descr}"
                        # Show custom message if available
                        msg = item.get("message")
                        if msg: display_text += f"  -> {msg[:60]}{'...' if len(msg)>60 else ''}"
                    elif isinstance(item, str):
                        display_text += f"{item}"
                    else:
                        display_text += f"Element not recognized: {str(item)}"
                    ttk.Label(scrollable_frame, text=display_text, style="Desc.TLabel", wraplength=initial_wraplength - 40).pack(anchor="w", padx=20, fill='x')

            elif isinstance(step_data, dict) and key.startswith("input"):
                question = step_data.get("question", f"Input required for {key}")
                choices = step_data.get("choices", {})

                ttk.Label(scrollable_frame, text=question, style="InputQ.TLabel").pack(anchor="w", padx=5, pady=(5, 2))

                if not choices:
                    ttk.Label(scrollable_frame, text="(ATTENTION: No choice defined!)", foreground="red").pack(anchor="w", padx=20)
                    continue

                default_value = list(choices.keys())[0]
                current_selection = self.user_inputs.get(key, default_value)
                var = tk.StringVar(value=current_selection)
                self._config_vars[key] = var

                for choice_key, choice_content in choices.items():
                    choice_frame = ttk.Frame(scrollable_frame)
                    choice_frame.pack(anchor="w", fill="x", padx=15, pady=2)
                    rb = ttk.Radiobutton(choice_frame, text=choice_key, variable=var, value=choice_key)
                    rb.pack(side=tk.LEFT, anchor="nw", padx=(0, 5))

                    actions_frame = ttk.Frame(choice_frame)
                    actions_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    steps_in_choice = choice_content.get("steps", [])
                    if steps_in_choice:
                        steps_label_text = "Associated actions:\n" + "\n".join([
                             f"  - {s.get('name', s if isinstance(s, str) else 'Action unknown')[:70]}{'...' if isinstance(s, dict) and len(s.get('name',''))>70 else ('...' if isinstance(s,str) and len(s)>70 else '')}"
                             + (f" -> {s['message'][:50]}{'...' if len(s['message'])>50 else ''}" if isinstance(s, dict) and s.get('message') else "") # Show message hint
                             for s in steps_in_choice
                        ])
                        steps_label = ttk.Label(actions_frame, text=steps_label_text, style="Action.TLabel", justify=tk.LEFT, wraplength=initial_wraplength - 150)
                        steps_label.pack(anchor="nw")
                    else:
                         ttk.Label(actions_frame, text="(No associated action)", style="Action.TLabel").pack(anchor="nw")

            elif isinstance(step_data, dict):
                 ttk.Label(scrollable_frame, text="(Specific details not shown here)", foreground="gray").pack(anchor="w", padx=20)
            else:
                 ttk.Label(scrollable_frame, text=f"(Type of data not recognizedo: {type(step_data)})", foreground="red").pack(anchor="w", padx=20)

        button_frame = ttk.Frame(config_win)
        button_frame.pack(pady=10, fill=tk.X, side=tk.BOTTOM)
        center_frame = ttk.Frame(button_frame)
        center_frame.pack()
        confirm_button = ttk.Button(center_frame, text="Confirm and start",
                                    command=lambda w=config_win: self.confirm_config_and_start(w))
        confirm_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(center_frame, text="Cancel", command=config_win.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)


    def confirm_config_and_start(self, config_window):
        """Saves selections from config window, prepares placeholders based on k3u_type, and starts the installation thread."""
        self.user_inputs.clear()
        for key, var in self._config_vars.items():
            self.user_inputs[key] = var.get()

        self.log("--- User configuration selected ---", tag="INFO")
        if not self._config_vars:
             self.log("(No input configurable for this setup)")
        else:
            for key, value in self.user_inputs.items():
                 self.log(f"Input '{key}': Scelta = {value}")
        self.log("-------------------------------------", tag="INFO")

        if config_window:
            config_window.grab_release()
            config_window.destroy()

        install_path = self.install_path_var.get()
        python_exe_target = self.python_exe_var.get()

        self.log(f"DEBUG: Raw value from install_path_var: '{install_path}'", tag="INFO")

        if not install_path:
             messagebox.showerror("Errore", "Base installation path not specified..")
             self.enable_controls()
             return
        parent_dir = os.path.dirname(install_path)
        if parent_dir and not os.path.isdir(parent_dir):
             messagebox.showerror("Errore", f"The parent directory of the installation path does not exist.:\n{parent_dir}")
             self.enable_controls()
             return
        if os.path.exists(install_path) and not os.path.isdir(install_path):
            messagebox.showerror("Errore", f"The base installation path exists but is not a folder.:\n{install_path}")
            self.enable_controls()
            return

        norm_install_path = os.path.normpath(install_path)
        self.log(f"DEBUG: Normalized install path value: '{norm_install_path}'", tag="INFO")
        comfyui_dir = os.path.join(norm_install_path, "ComfyUI")

        self.placeholders = {
             "{INSTALL_PATH}": norm_install_path,
             "{COMFYUI_PATH}": comfyui_dir
        }

        if self.current_k3u_type == "embedded":
            embed_dir = os.path.join(norm_install_path, "python_embeded")
            embed_python_exe = os.path.join(embed_dir, "python.exe")
            self.placeholders["{EMBEDDED_PYTHON_DIR}"] = embed_dir
            self.placeholders["{EMBEDDED_PYTHON_EXE}"] = embed_python_exe
            self.placeholders["{PYTHON_EXE}"] = ""

        elif self.current_k3u_type == "external_venv":
            if not python_exe_target:
                 messagebox.showerror("Errore", "Python target executable not specified (required for setup external_venv).")
                 self.enable_controls(); return
            if not os.path.isfile(python_exe_target):
                 messagebox.showerror("Errore", f"Python target executable not found:\n{python_exe_target}")
                 self.enable_controls(); return
            norm_python_exe_target = os.path.normpath(python_exe_target)
            venv_dir = os.path.join(comfyui_dir, "venv")
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(venv_dir, "bin", "python")
            self.placeholders["{PYTHON_EXE}"] = norm_python_exe_target
            self.placeholders["{VENV_PATH}"] = venv_dir
            self.placeholders["{VENV_PYTHON}"] = venv_python
            self.placeholders["{EMBEDDED_PYTHON_DIR}"] = ""
            self.placeholders["{EMBEDDED_PYTHON_EXE}"] = ""
        else:
             messagebox.showwarning("Attenzione", f"Tipo K3U '{self.current_k3u_type}' not recognized.I proceed like 'external_venv'.")
             self.current_k3u_type = "external_venv"
             if not python_exe_target or not os.path.isfile(python_exe_target):
                  messagebox.showerror("Errore", "Executable Python Target not specified or not valid.")
                  self.enable_controls(); return
             norm_python_exe_target = os.path.normpath(python_exe_target)
             venv_dir = os.path.join(comfyui_dir, "venv")
             venv_python = os.path.join(venv_dir, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(venv_dir, "bin", "python")
             self.placeholders["{PYTHON_EXE}"] = norm_python_exe_target
             self.placeholders["{VENV_PATH}"] = venv_dir
             self.placeholders["{VENV_PYTHON}"] = venv_python
             self.placeholders["{EMBEDDED_PYTHON_DIR}"] = ""
             self.placeholders["{EMBEDDED_PYTHON_EXE}"] = ""

        self.log("Placeholders impostati:", tag="INFO")
        for k,v in self.placeholders.items():
             if v: self.log(f"  {k} = {v}")

        # Start flashing and show status frame BEFORE disabling controls
        self.update_status_text("Avvio...")
        self.start_flashing()
        self.disable_controls()
        self.start_installation_thread()

    def disable_controls(self):
        """Disables UI controls during installation."""
        self.start_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.browse_path_button.config(state="disabled")
        self.browse_python_button.config(state="disabled")
        self.setup_combobox.config(state="disabled")
        self.path_entry.config(state="disabled")
        self.python_entry.config(state="disabled")
        self.file_entry.config(state="disabled")

    def enable_controls(self):
        """Enables UI controls after installation or on error."""
        self.start_button.config(state="normal" if self.current_setup_data else "disabled")
        self.reset_button.config(state="normal")
        self.browse_button.config(state="normal")
        self.browse_path_button.config(state="normal")
        # Enable/disable Python input based on last loaded k3u type
        python_input_state = "disabled" if self.current_k3u_type == "embedded" else "normal"
        self.browse_python_button.config(state=python_input_state)
        self.python_entry.config(state=python_input_state)
        self.python_label.config(state=python_input_state)

        self.setup_combobox.config(state="readonly" if self.k3u_data else "disabled")
        self.path_entry.config(state="normal")
        self.file_entry.config(state="normal")


    def start_installation_thread(self):
        """Prepares and starts the background thread for installation steps."""
        if self.worker_thread is not None and self.worker_thread.is_alive():
             messagebox.showwarning("Attention", "Un processo di installazione è già in corso.")
             self.enable_controls()
             return
        if not self.placeholders or not self.placeholders.get("{INSTALL_PATH}"):
             messagebox.showerror("Errore Interno", "Placeholders not correctly initialized before starting the thread.")
             self.enable_controls()
             # Stop flashing if validation failed after starting it
             self.stop_flashing()
             self.update_status_text("Error Placeholder")
             return

        self.total_steps_for_progress = self._calculate_total_steps()
        self.progress_var.set(0)

        self.log("\n=== Installation start ===", tag="INFO")
        self.log(f"Selected setup: {self.selected_setup_key} (Tipo: {self.current_k3u_type})")
        self.log(f"Basic installation route: {self.placeholders.get('{INSTALL_PATH}', 'N/D')}")
        if self.current_k3u_type == "embedded":
             self.log(f"Python Embedded Path: {self.placeholders.get('{EMBEDDED_PYTHON_EXE}', 'N/D')}")
        else:
             self.log(f"Python Target Path: {self.placeholders.get('{PYTHON_EXE}', 'N/D')}")

        if self.user_inputs:
            self.log("With the following options:")
            for k, v in self.user_inputs.items():
                self.log(f"  - {k}: {v}")

        self.worker_thread = threading.Thread(target=self._run_installation_steps, daemon=True)
        self.worker_thread.start()
        self.master.after(100, self._check_thread_completion)

    def _check_thread_completion(self):
        """Periodically checks if the worker thread has finished."""
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.master.after(100, self._check_thread_completion)
        else:
            # Stop flashing and update status when thread completes
            self.stop_flashing()
            # Final status message is set in _run_installation_steps
            # self.update_status_text("Completato/Fallito") # Set by thread end
            self.enable_controls()
            self.worker_thread = None
            final_progress = self.progress_var.get()
            # Log if incomplete only if some progress was made
            if final_progress < 100 and final_progress > 0:
                 self.log("The installation process is finished (it could be incomplete or failed).", tag="WARNING")


    def _calculate_total_steps(self):
        """Calculates the total number of command items for the progress bar based on the 'steps' structure."""
        count = 0
        if not self.current_setup_data or "steps" not in self.current_setup_data:
             return 1

        steps_list = self.current_setup_data.get("steps", [])

        temp_user_inputs = self.user_inputs.copy()
        if not temp_user_inputs: # Estimate using defaults if run before config
            for step_info in steps_list:
                key = step_info.get("key")
                step_data = step_info.get("step_data")
                if isinstance(step_data, dict) and key and key.startswith("input"):
                    choices = step_data.get("choices", {})
                    if choices:
                        default_choice = list(choices.keys())[0]
                        temp_user_inputs[key] = default_choice

        for step_info in steps_list:
            key = step_info.get("key")
            step_data = step_info.get("step_data")
            commands_in_step = []

            if isinstance(step_data, list):
                commands_in_step = step_data
            elif isinstance(step_data, dict) and key and key.startswith("input"):
                user_choice = temp_user_inputs.get(key) # Use temp map for calculation
                if user_choice:
                    choice_data = step_data.get("choices", {}).get(user_choice, {})
                    commands_in_step = choice_data.get("steps", [])

            for item in commands_in_step:
                 if isinstance(item, str) and item.strip():
                     count += 1
                 elif isinstance(item, dict) and item.get("command", "").strip():
                     count += 1

        return count if count > 0 else 1


    def _substitute_placeholders(self, command_string):
        """Replaces all known placeholders in a command string."""
        substituted_cmd = command_string
        try:
            if not self.placeholders:
                 raise ValueError("Placeholders dictionary not initialized.")
            for key, value in sorted(self.placeholders.items(), key=lambda item: len(item[0]), reverse=True):
                 str_value = str(value) if value is not None else ""
                 if key.startswith("{") and key.endswith("}"):
                      substituted_cmd = substituted_cmd.replace(key, str_value)
        except Exception as e:
             self.log(f"Error during replacement placeholder in '{command_string}': {e}", tag="ERROR")
             raise ValueError(f"Failed replacement placeholder for: {command_string}") from e
        return substituted_cmd


    def _run_installation_steps(self):
        """Executes the installation steps in the background thread using the 'steps' structure."""
        current_step_count = 0
        success = True
        final_message = "Successful installation."
        final_tag = "SUCCESS"

        base_install_path = self.placeholders.get("{INSTALL_PATH}")
        comfyui_base_dir = self.placeholders.get("{COMFYUI_PATH}")

        if not base_install_path:
             self.log("Critical error: Placeholder {INSTALL_PATH} undefined.", tag="ERROR")
             final_message = "Internal error: missing basic installation route."
             final_tag = "ERROR"; success = False
             # Update status from thread using after()
             self.master.after(0, self.update_status_text, final_message)
             self.master.after(0, self.progress_var.set, 0)
             return # Stop thread execution


        try:
            # Initial status update from thread
            self.master.after(0, self.update_status_text, "In processing...")

            steps_list = self.current_setup_data.get("steps", [])
            for step_info in steps_list:
                if not success: break

                key = step_info.get("key", "CHIAVE_SCONOSCIUTA")
                step_data = step_info.get("step_data")
                self.log(f"\n--- Execution step: {key.upper()} ---", tag="STEP")

                commands_to_run = []
                step_source_info = ""

                if isinstance(step_data, list):
                    commands_to_run = step_data
                    step_source_info = f"(da '{key}')"
                elif isinstance(step_data, dict) and key.startswith("input"):
                    user_choice = self.user_inputs.get(key)
                    if user_choice:
                        step_source_info = f"(da Input '{key}', choice '{user_choice}')"
                        self.log(f"I run through the user choice: {user_choice}")
                        choice_data = step_data.get("choices", {}).get(user_choice, {})
                        commands_to_run = choice_data.get("steps", [])
                        if not commands_to_run:
                             self.log(f"  (No step defined for the choice '{user_choice}')", tag="WARNING")
                    else:
                        self.log(f"ATTENTION: No user choice found for input '{key}', step saltato.", tag="WARNING")
                        continue

                for item_index, item in enumerate(commands_to_run):
                    if not success: break

                    command_template = None
                    name = None

                    if isinstance(item, str) and item.strip():
                        command_template = item
                        name = f"{key} - Comando {item_index+1}"
                    elif isinstance(item, dict):
                        command_template = item.get("command")
                        name = item.get("name", f"{key} - Azione {item_index+1}")
                    else:
                        self.log(f"Invalid element ignored {step_source_info}: {item}", tag="WARNING")
                        continue

                    if not command_template or not command_template.strip():
                         self.log(f"Empty command ignored for '{name}' {step_source_info}", tag="WARNING")
                         continue

                    # Set status text before running command (use custom message if available)
                    message = item.get("message") if isinstance(item, dict) else None
                    default_status = f"Execution: {name}..."
                    status_to_show = message if message else default_status
                    if len(status_to_show) > 100: status_to_show = status_to_show[:97] + "..."
                    self.master.after(0, self.update_status_text, status_to_show)


                    try:
                        final_command = self._substitute_placeholders(command_template)
                    except ValueError as e:
                         self.log(str(e), tag="ERROR")
                         success = False; final_message = "Placeholder replacement error."; final_tag="ERROR"; break
                    except Exception as e:
                         self.log(f"Unexpected error during the replacement of the placeholders for [{name}]: {e}", tag="ERROR")
                         self.log(f"Original command: {command_template}", tag="ERROR")
                         success = False; final_message = "Placeholder replacement error."; final_tag="ERROR"; break

                    self.log(f"--> Run [{name}] {step_source_info}:", tag="CMD")
                    self.log(f"    Command: {final_command}")

                    # --- Determine and Validate CWD ---
                    cwd_template = base_install_path
                    try:
                        resolved_comfyui_dir_template = self.placeholders.get("{COMFYUI_PATH}", base_install_path)
                        resolved_comfyui_dir = self._substitute_placeholders(resolved_comfyui_dir_template)
                        if os.path.isdir(resolved_comfyui_dir):
                            cwd_template = resolved_comfyui_dir_template
                    except Exception as e:
                         self.log(f"ATTENTION: error in determining CWD default based on Comfyui: {e}", tag="WARNING")

                    if "setup.py install" in final_command and "SageAttention" in name:
                         cwd_template = os.path.join(base_install_path, "temp_sage")
                    elif key in ["start", "setup_embed_python", "install_include_libs"] or "git clone" in command_template:
                         cwd_template = base_install_path
                    elif "custom_nodes" in command_template:
                         nodes_dir_template = os.path.join(self.placeholders.get("{COMFYUI_PATH}", ""), "custom_nodes")
                         try:
                              resolved_nodes_dir = self._substitute_placeholders(nodes_dir_template)
                              if os.path.isdir(resolved_nodes_dir):
                                   cwd_template = nodes_dir_template
                         except: pass

                    try:
                        resolved_cwd = self._substitute_placeholders(cwd_template)
                        resolved_cwd = os.path.normpath(resolved_cwd)
                    except ValueError as e:
                        self.log(f"Error while replacing Placeholder for CWD '{cwd_template}': {e}", tag="ERROR")
                        success = False; final_message = "Error CWD."; final_tag="ERROR"; break
                    except Exception as e:
                        self.log(f"Unexpected error while replacing Placeholder for CWD '{cwd_template}': {e}", tag="ERROR")
                        success = False; final_message = "Error Cwd."; final_tag="ERROR"; break

                    if not os.path.isdir(resolved_cwd):
                         fallback_cwd_template = self.placeholders.get('{INSTALL_PATH}', '.')
                         try:
                              resolved_fallback_cwd = self._substitute_placeholders(fallback_cwd_template)
                              resolved_fallback_cwd = os.path.normpath(resolved_fallback_cwd)
                         except Exception as e:
                              self.log(f"Error while replacing Placeholder for Fallback CWD '{fallback_cwd_template}': {e}", tag="ERROR")
                              success = False; final_message = "Error CWD Fallback."; final_tag="ERROR"; break

                         self.log(f"    ATTENTION: the work directory '{resolved_cwd}' (da '{cwd_template}') does not exist, use '{resolved_fallback_cwd}'.", tag="WARNING")
                         resolved_cwd = resolved_fallback_cwd
                         if not os.path.isdir(resolved_cwd):
                              self.log(f"    Error: also the Fallback Directory '{resolved_cwd}' it does not exist!", tag="ERROR")
                              success = False; final_message = "Errore CWD Fallback."; final_tag="ERROR"; break


                    # --- Execute Command ---
                    try:
                        process = subprocess.run(
                            final_command,
                            shell=True,
                            cwd=resolved_cwd,
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='replace'
                        )

                        if process.stdout and process.stdout.strip():
                            self.log(f"    Output:\n{process.stdout.strip()}", tag="OUTPUT")
                        if process.stderr and process.stderr.strip():
                            stderr_tag = "ERROR" if process.returncode != 0 else "WARNING"
                            self.log(f"    Error Output:\n{process.stderr.strip()}", tag=stderr_tag)

                        if process.returncode != 0:
                            self.log(f"Error: Command [{name}] Failed with code. {process.returncode}", tag="ERROR")
                            success = False
                            final_message = f"Command '{name}' Failed."
                            final_tag = "ERROR"
                            if key.startswith("prequire"):
                                 final_message = f"Prerequisite control '{name}' failed.Impossible to continue."
                            break # Stop processing commands in this step
                        else:
                             self.log(f"<-- Command [{name}] completed.", tag="SUCCESS")

                    except FileNotFoundError:
                         cmd_part = final_command.split()[0]
                         self.log(f"Error: Command or program not found: '{cmd_part}'. Make sure it is in the path or uses an absolute path.", tag="ERROR")
                         success = False; final_message = "Command not found."; final_tag="ERROR"; break
                    except subprocess.TimeoutExpired:
                         self.log(f"Error: Timeout expired for the command [{name}]", tag="ERROR")
                         success = False; final_message = "Timeout comando."; final_tag="ERROR"; break
                    except Exception as e:
                        self.log(f"Unexpected error during the execution of [{name}] in CWD '{resolved_cwd}': {e}", tag="ERROR")
                        success = False; final_message = "Command execution error."; final_tag="ERROR"; break

                    # --- Update Progress Bar ---
                    current_step_count += 1
                    progress = (current_step_count / self.total_steps_for_progress) * 100 if self.total_steps_for_progress > 0 else 100.0
                    self.master.after(0, self.progress_var.set, min(progress, 100.0))

                    # Reset status to generic "In Lavorazione" if no specific message for next command (optional)
                    # Or just let the next loop update it. Let's do that.


        except OSError as e:
            self.log(f"System error: {e}", tag="ERROR")
            success = False
            final_message = "Installation failed due to a system error."
            final_tag = "ERROR"
        except Exception as e:
            self.log(f"Critical error in the installation process: {e}", tag="ERROR")
            import traceback
            self.log(f"Traceback:\n{traceback.format_exc()}", tag="ERROR")
            success = False
            final_message = "Failed installation due to an unexpected error."
            final_tag = "ERROR"

        # --- Final Logging & Status Update ---
        if not success and final_tag != "ERROR": # Catch cases where success is False but no specific message was set
             final_message = "Installation finished with errors."
             final_tag = "ERROR"

        self.log(f"\n=== {final_message} ===", tag=final_tag)
        # Update status label one last time from the thread
        self.master.after(0, self.update_status_text, final_message)

        final_progress_value = 100.0 if success else self.progress_var.get()
        self.master.after(0, self.progress_var.set, final_progress_value)


# ==================================
# BLOCCO PRINCIPALE
# QUESTA RIGA DEVE AVERE ZERO INDENTAZIONE (Nessuno spazio/tab prima)
# ==================================
if __name__ == "__main__":
    # Il codice qui sotto è indentato sotto l'if
    root = tk.Tk()
    try:
        style = ttk.Style(root)
        # Example theme setting (uncomment to try)
        # available_themes = style.theme_names()
        # print(available_themes)
        # if 'vista' in available_themes:
        #    style.theme_use('vista')
        # elif 'clam' in available_themes:
        #    style.theme_use('clam')
    except tk.TclError:
        print("ttk themes not available or failed to set.")

    app = K3U_Installer_GUI(root) # Crea l'istanza della classe definita sopra
    root.mainloop()
# ==================================
# FINE FILE
# ==================================
