import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import sys
from six_digit_handler import Memory6, CPU6, ControlInstructions6, MathInstructions6


class UvsimGUI:
    def __init__(self, window):
        self.window = window
        self.root = window
        self.window.title("UVSim Simulator")
        self.window.geometry("900x675")
        self.window.configure(padx=10, pady=10)
        self.current_entry = None
        self.program_lines = []
        self.create_widgets()
        self.change_theme("default mode")

    def reset(self):       
        self.cpu.reset()
        self.memory.reset()
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.DISABLED)
        self.log_message("---PROGRAM RESET---")
        self.load_file()

    def check_run(self):
        can_run = False
        for x in self.memory.mem:
            s = str(x).lstrip("+-")
            if not s.isdigit() or len(s) not in (4, 6):
                if x == 0 or x == "+0000" or x == "+000000":
                    can_run = True
                    break
                can_run = False
                self.log_message(f"{x} : Invalid memory value. Must be signed 4 or 6 digits.")
                break
            else:
                can_run = True
        if can_run:
            self.cpu.run()

    def resume_cpu(self):
        self.cpu.done = False
        self.load_mem()
        self.cpu.run()

    def submit_input(self):
        content = self.input_entry.get("1.0", tk.END).strip()
        digits = content.lstrip("+-")
        # Accept 4- or 6-digit input depending on CPU version
        expected_len = 6 if hasattr(self.memory, "WORD_SIZE") and self.memory.WORD_SIZE == 6 else 4

        if digits.isdigit() and len(digits) == expected_len:
            self.conInstruct.READ(self.conInstruct.temp_address)
            self.log_message(f"Submitted input: {content}")
            self.resume_cpu()
        else:
            self.log_message(f"Invalid input — must be a signed {expected_len}-digit number "
                             f"(e.g. +{'0'*(expected_len-1)}1).")
        self.input_entry.delete("1.0", tk.END)
        self.btn_submit.configure(state=tk.DISABLED)

    def load_file(self):
        try:
            loaded = self.loader.load_from_file(self.selected_file)
            if loaded:
                self.load_mem()
        except Exception as e:
            self.log_message(f"Error loading file: {e}")

    def edit_memory_cell(self, event):
        if hasattr(self, "current_entry") and self.current_entry is not None:
            self.current_entry.destroy()
            self.current_entry = None

        selected_item = self.memory_tree.identify_row(event.y)
        selected_column = self.memory_tree.identify_column(event.x)

        if selected_item and selected_column == "#2":
            x, y, width, height = self.memory_tree.bbox(selected_item, selected_column)
            old_value = self.memory_tree.item(selected_item, "values")[1]

            entry = ttk.Entry(self.memory_tree)
            entry.place(x=x, y=y-2, width=width+4, height=height+4)
            entry.insert(0, old_value)
            entry.focus()
            entry.selection_range(0, tk.END)
            self.current_entry = entry

            def save_edit(event=None):
                new_value = entry.get().strip()
                try:
                    digits = new_value.lstrip("+-")
                    if digits.isdigit() and len(digits) in (4, 6):
                        address = int(self.memory_tree.item(selected_item, "values")[0])
                        self.memory.set_value(address, int(new_value))
                        self.memory_tree.item(selected_item, values=(f"{address:02}", self.memory.mem[address]))
                        self.log_message(f"Memory[{address}] updated to {self.memory.mem[address]}")
                        self._ensure_capacity(address)
                        self.program_lines[address] = self.memory.mem[address]
                        if hasattr(self, "program_lines"):
                            if address < len(self.program_lines):
                                self.program_lines[address] = self.memory.mem[address]
                            else:
                                self.program_lines.append(self.memory.mem[address])
                    else:
                        self.log_message("Invalid input. Must be a signed 4- or 6-digit number.")
                except Exception as e:
                    self.log_message(f"Error updating memory: {e}")
                finally:
                    entry.destroy()
                    self.current_entry = None

            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", lambda e: (entry.destroy(), setattr(self, "current_entry", None)))


    # --------------------------------------------------------------
    # All memory registers are alraedy loaded into the GUI
    # Commenting out ability to add lines beyond defined memory size
    # --------------------------------------------------------------

    """def add_memory_cell(self):
        filler = self._filler()
        selected_item = self.memory_tree.selection()

        # --- Determine insert index ---
        if selected_item:
            # If a row is selected, add *after* that row
            selected_item = selected_item[0]
            address = int(self.memory_tree.item(selected_item, "values")[0])
            insert_index = address + 1
        else:
            # No selection — add after the last non-empty line
            insert_index = len(self.memory.mem)
            # But trim trailing zeros first (for cleaner placement)
            while insert_index > 0 and self.memory.mem[insert_index - 1] in (0, "+0000", "+000000"):
                insert_index -= 1
            insert_index = len(self.memory.mem) if insert_index == 0 else insert_index

        # --- Ensure capacity and insert new filler cell ---
        self._ensure_capacity(insert_index)
        if insert_index < len(self.memory.mem):
            self.memory.mem.insert(insert_index, filler)
        else:
            self.memory.mem.append(filler)

        self.program_lines.insert(insert_index, filler)

        # --- Refresh the GUI ---
        self.load_mem()
        self.log_message(f"Added new memory cell at address {insert_index}")
    """
    def remove_memory_cell(self):
        selected_item = self.memory_tree.selection()
        if not selected_item:
            self.log_message("No memory cell selected to remove.")
            return

        address = int(self.memory_tree.item(selected_item[0], "values")[0])
        filler = self._filler()

        # --- Clear from memory ---
        if address < len(self.memory.mem):
            self.memory.mem[address] = filler

        # --- Keep program_lines aligned (replace, don't delete) ---
        self._ensure_capacity(address)
        self.program_lines[address] = filler

        # --- Refresh display ---
        self.load_mem()
        self.log_message(f"Cleared memory cell at address {address}")

    def load_mem(self):
        # Clear the current tree
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)

        # Filler for empty cells
        filler = self._filler()

        # Populate the tree with all memory cells
        for index in range(len(self.memory.mem)):
            val = self.memory.mem[index]
            # Normalize blank or 0 cells to filler for display
            if val in (0, "0", "", "+0000", "+000000"):
                val = filler
            self.memory_tree.insert("", tk.END, values=(f"{index:02}", f"{val}"))

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open Program File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        self.selected_file = filepath
        self.log_message(f"Opened file: {filepath}")

        # ----------------------------------------------------------
        # Detect whether the program uses 6-digit words
        # ----------------------------------------------------------
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                has_six_digit = any(len(ln.lstrip("+-")) == 6 for ln in lines)
        except Exception as e:
            self.log_message(f"Error reading file for detection: {e}")
            has_six_digit = False
            lines = []

        # ----------------------------------------------------------
        # Import correct version of CPU/Memory/etc based on format
        # ----------------------------------------------------------
        try:
            if has_six_digit:
                from six_digit_handler import Memory6, CPU6, ControlInstructions6, MathInstructions6
                from program_loader import ProgramLoader

                self.memory = Memory6()
                self.cpu = CPU6(self.memory, self)
                self.conInstruct = ControlInstructions6(self.memory, self.cpu, self)
                self.mathInstruct = MathInstructions6(self.memory)
                self.loader = ProgramLoader(self.memory, self)
                self.memory.WORD_SIZE = 6
                self.log_message("Detected 6-digit program — initialized 6-digit CPU.")
            else:
                from memory import Memory
                from cpu import CPU
                from control_instructions import ControlInstructions
                from math_instructions import MathInstructions
                from program_loader import ProgramLoader

                self.memory = Memory()
                self.cpu = CPU(self.memory, self)
                self.conInstruct = ControlInstructions(self.memory, self.cpu, self)
                self.mathInstruct = MathInstructions(self.memory)
                self.loader = ProgramLoader(self.memory, self)
                self.memory.WORD_SIZE = 4
                self.log_message("Detected 4-digit program — using legacy CPU.")

            self.cpu.set_instructions(self.conInstruct, self.mathInstruct)
        except Exception as e:
            self.log_message(f"Error initializing CPU/Memory: {e}")
            return

        # Enable Run/Reset buttons if it's a valid text file

        if filepath.lower().endswith(".txt"):
            self.btn_run.configure(state=tk.NORMAL)
            self.btn_reset.configure(state=tk.NORMAL)

        # Initialize editable program_lines and memory

        try:
            self.program_lines = []
            total_size = getattr(self.memory, "size", len(self.memory.mem))
            filler = self._filler()

            for i in range(total_size):
                if i < len(lines) and lines[i]:
                    raw = lines[i].strip()
                    if raw in ("0", "+0", "-0", "0000", "+0000", "-0000"):
                        normalized = filler
                    else:
                        # Ensure signed format
                        if not raw.startswith(("+", "-")):
                            raw = "+" + raw
                        normalized = raw.zfill(self.memory.WORD_SIZE + 1)  # sign + digits

                    self.program_lines.append(normalized)
                    self.memory.mem[i] = normalized
                else:
                    self.program_lines.append(filler)
                    self.memory.mem[i] = filler

            self.log_message(f"Loaded {len(lines)} lines into memory and editable buffer.")
        except Exception as e:
            self.log_message(f"Error initializing program lines: {e}")

        # Load GUI display

        self.load_mem()
    def open_theme_menu(self, event=None):
        # Popup position (under the mouse)
        x = self.window.winfo_pointerx()
        y = self.window.winfo_pointery()

 
        self.theme_menu.tk_popup(x, y)
        self.theme_menu.grab_release()

    def choose_custom_colors(self):
        bg_color = colorchooser.askcolor(title="Choose Background Color")
        if not bg_color or not bg_color[1]:
            return  
    
        fg_color = colorchooser.askcolor(title="Choose Text (Foreground) Color")
        if not fg_color or not fg_color[1]:
            return  


        self.themes["custom"] = {
            "bg": bg_color[1],
            "fg": fg_color[1],
            "text_bg": bg_color[1],
            "text_fg": fg_color[1],
            "button_bg": fg_color[1],
            "button_fg": bg_color[1],
        }

        self.change_theme("custom")
        style = ttk.Style()
        style.configure("TFrame", background=bg_color[1])
        style.configure("TLabelFrame", background=bg_color[1], foreground=fg_color[1])
        style.configure("TLabelFrame.Label", background=bg_color[1], foreground=fg_color[1])
        style.configure("TButton", background=fg_color[1], foreground=bg_color[1])
        style.map("TButton",
                background=[("active", fg_color[1])],
                foreground=[("active", bg_color[1])])
        
        style.configure("Treeview", 
                        background=bg_color[1],
                        fieldbackground=bg_color[1],
                        foreground=fg_color[1])
        style.configure("Treeview.Heading", background=fg_color[1], foreground=bg_color[1])
    
        
    def change_theme(self, theme="default"):
        theme_key = theme.lower()
        if theme_key not in self.themes:
            print(f"Theme '{theme}' not found. Using Default Mode.")
            theme_key = "default mode"
        colors = self.themes[theme_key]

        self.window.configure(bg=colors['bg'])

        style = ttk.Style()
        style.theme_use('default')

        style.configure("TFrame", background=colors['bg'])
        style.configure("TLabelFrame", background=colors['bg'], foreground=colors['fg'])
        style.configure("TLabelFrame.Label", background=colors['bg'], foreground=colors['fg'])
        style.configure("TLabel", background=colors['bg'], foreground=colors['fg'])

        style.configure("TButton", background=colors['button_bg'], foreground=colors['button_fg'])
        style.map("TButton",
              foreground=[('active', colors['button_fg'])],
              background=[('active', colors['button_bg'])])
        style.configure("Treeview",
                    background=colors['text_bg'],
                    fieldbackground=colors['text_bg'],
                    foreground=colors['text_fg'])
        style.configure("Treeview.Heading",
                        background=colors['button_bg'],
                        foreground=colors['button_fg'])

        self.output_text.configure(
            background=colors['text_bg'],
            foreground=colors['text_fg'],
            insertbackground=colors['text_fg']
        )
        self.input_entry.configure(
            background=colors['text_bg'],
            foreground=colors['text_fg'],
            insertbackground=colors['text_fg']
        )

        self.apply_widget_theme(self.window, colors)

    def apply_widget_theme(self, widget, colors):
        # Apply colors based on widget type
        cls = widget.__class__.__name__
        if cls in ['Label', 'LabelFrame']:
            try:
                widget.configure(background=colors['bg'], foreground=colors['fg'])
            except:
                pass
        elif cls == 'Button':
            try:
                widget.configure(background=colors['button_bg'], foreground=colors['button_fg'], activebackground=colors['button_bg'])
            except:
                pass
        elif cls == 'Text':
            try:
                widget.configure(background=colors['text_bg'], foreground=colors['text_fg'], insertbackground=colors['text_fg'])
            except:
                pass
        elif cls == 'Frame':
            try:
                widget.configure(background=colors['bg'])
            except:
                pass
        elif cls == 'TFrame':
            try:
                widget.configure(style="TFrame")
            except:
                pass
        # Recurse for children
        for child in widget.winfo_children():
            self.apply_widget_theme(child, colors)

    def open_new_instance(self):
        new_window = tk.Toplevel()
        UvsimGUI(new_window)

    def create_widgets(self):
        # The Dictionary of Themes
        self.themes = {
            "default mode": {
                "bg": "#4C721D",          # Dark Green background
                "fg": "#FFFFFF",          # White text
                "text_bg": "#FFFFFF",     # White text background
                "text_fg": "#000000",     # Black text
                "button_bg": "#4C721D",   # Dark Green button background
                "button_fg": "#FFFFFF"    # White button text
            },
            "dark mode": {
                "bg": "#121212",          # Very dark gray background
                "fg": "#E0E0E0",          # Light gray text
                "text_bg": "#1E1E1E",     # Dark gray text background
                "text_fg": "#FFFFFF",     # White text
                "button_bg": "#333333",   # Dark gray button background
                "button_fg": "#FFFFFF"    # White button text
            },
            "light mode": {
                "bg": "#F0F0F0",          # Light gray background
                "fg": "#000000",          # Black text
                "text_bg": "#FFFFFF",     # White text background
                "text_fg": "#000000",     # Black text
                "button_bg": "#E0E0E0",   # Light gray button background
                "button_fg": "#000000"    # Black button text
            }
        }

        # Themes
        self.theme_menu = tk.Menu(self.window, tearoff=0)
        self.theme_menu.add_command(label="Default Mode", command=lambda: self.change_theme("Default Mode")) #RGB (76,114,29) / Hex# 4C721D (Dark Green) & (White) RGB (255,255,255 / #FFFFFF)
        self.theme_menu.add_command(label="Dark Mode", command=lambda: self.change_theme("Dark Mode"))
        self.theme_menu.add_command(label="Light Mode", command=lambda: self.change_theme("Light Mode"))
        self.theme_menu.add_separator()
        self.theme_menu.add_command(label="Custom Theme...", command=self.choose_custom_colors)
        # Button colors
        style = ttk.Style()
        style.configure("Enabled.TButton", foreground="white")  # Enabled state
        style.configure("Disabled.TButton", foreground="gray")  # Disabled state

        # Menu Bar
        menubar = tk.Menu(self.window)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Open New Window", command=self.open_new_instance)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_command(label="Themes", command=self.open_theme_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: None)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.window.config(menu=menubar)

        

        # Main layout frames
        main_frame = ttk.Frame(self.window, padding=(5, 5, 5, 5))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for controls and output
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        lower_frame = ttk.Frame(main_frame)
        lower_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Program controls
        controls_frame = ttk.LabelFrame(left_frame, text="Program Controls", padding=(10, 10))
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_run = ttk.Button(controls_frame, text="Run", command=lambda: self.check_run(), state=tk.DISABLED) # Starts the program from the beginning of the input file.
        # self.btn_step = ttk.Button(controls_frame, text="Step", command=lambda: None, style="Disabled.TButton", state=tk.DISABLED) # Steps through the program
        self.btn_reset = ttk.Button(controls_frame, text="Reset", command=lambda: self.reset(), state=tk.DISABLED) # Could reset the accumulator to its default value and reset the pointer looking at the input file to run through the program from the beginning of the file.
        self.btn_exit = ttk.Button(controls_frame, text="Exit", command=self.window.destroy) # Closes the window and stops the program

        self.btn_run.grid(row=0, column=1, padx=5, pady=5)
        # self.btn_step.grid(row=0, column=2, padx=5, pady=5)
        self.btn_reset.grid(row=0, column=3, padx=5, pady=5)
        self.btn_exit.grid(row=0, column=4, padx=5, pady=5)
        

        # Output/log display
        output_frame = ttk.LabelFrame(left_frame, text="Output / Log", padding=(10, 10))
        output_frame.pack(fill=tk.BOTH, expand=True)
        self.output_text = tk.Text(output_frame, height=20, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Right frame for memory/registers
        right_frame = ttk.LabelFrame(main_frame, text="Memory / Registers", padding=(10, 10))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # Text input box
        text_input_frame = ttk.LabelFrame(left_frame, text="Input Text Here:", padding=(10, 10))
        text_input_frame.pack(fill=tk.BOTH, expand=True)
        self.input_entry = tk.Text(text_input_frame, height=1, wrap=tk.WORD, state=tk.NORMAL)
        self.input_entry.pack(fill=tk.BOTH, expand=True)

        # Memory Tree
        columns = ("Address", "Value")
        self.memory_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=25)

        style = ttk.Style()
        style.configure("Treeview", rowheight=20)

        for col in columns:
            self.memory_tree.heading(col, text=col)
            self.memory_tree.column(col, width=80, anchor=tk.CENTER)
        self.memory_tree.pack(fill=tk.BOTH, expand=True)

        # Add "+" and "–" buttons below memory tree
        mem_button_frame = ttk.Frame(right_frame)
        mem_button_frame.pack(fill=tk.X, pady=(5, 0))


        # --------------------------------------------------------------
        # All memory registers are alraedy loaded into the GUI
        # Removing ability to add lines beyond defined memory size
        # --------------------------------------------------------------

        #btn_add = ttk.Button(mem_button_frame, text="+", width=3, command=self.add_memory_cell)
        #btn_add.pack(side=tk.LEFT, padx=5) 

        btn_remove = ttk.Button(mem_button_frame, text="Clear", width=10, command=self.remove_memory_cell)
        btn_remove.pack(anchor="center", pady=5)

        submit_frame = ttk.Frame(self.window)
        submit_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
        self.btn_submit = ttk.Button(submit_frame, text="Submit", command=self.submit_input, state=tk.DISABLED)
        self.btn_submit.pack(side=tk.LEFT)

        # Bindings
        self.input_entry.bind("<KeyRelease>", self.on_input_change)
        self.input_entry.bind("<<Modified>>", self.on_input_change)
        self.input_entry.bind("<FocusIn>", self.on_input_change)
        self.input_entry.bind("<FocusOut>", self.on_input_change)
        self.memory_tree.bind("<Double-1>", self.edit_memory_cell)


    def on_input_change(self, event=None):
        content = self.input_entry.get("1.0", tk.END).strip()

        if content:
            self.btn_submit.configure(state=tk.NORMAL)
        else:
            self.btn_submit.configure(state=tk.DISABLED)

        # Reset the modified flag so the <<Modified>> event keeps firing
        if event and hasattr(self.input_entry, "edit_modified"):
            self.input_entry.edit_modified(False)

    def log_message(self, message: str):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)                  # auto scroller :)
        self.output_text.configure(state=tk.DISABLED)

    def save_file(self):
        try:
            if not hasattr(self, "selected_file") or not self.selected_file:
                return self.save_file_as()

            # --- Used to store only original and user-edited lines---
            if not hasattr(self, "program_lines") or not self.program_lines:
                self.program_lines = []

            editable_lines = self.program_lines.copy()
            filler = "+000000" if getattr(self.memory, "WORD_SIZE", 4) == 6 else "+0000"
            total_size = getattr(self.memory, "size", len(self.memory.mem))

            # --- Write to memory sequentially ---
            output_lines = []
            for addr in range(total_size):
                if addr < len(editable_lines) and editable_lines[addr].strip():
                    line = editable_lines[addr].strip()
                else:
                    line = filler
                output_lines.append(line)

            content = "\n".join(output_lines)
            with open(self.selected_file, "w", encoding="utf-8") as f:
                f.write(content)

            self.log_message(f"Saved full program memory ({len(output_lines)} lines) to {self.selected_file}")
            messagebox.showinfo("Saved", f"Program saved:\n{self.selected_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
            self.log_message(f"Save error: {e}")

    def _filler(self): # Helper to get filler line based on word size
        return "+000000" if getattr(self.memory, "WORD_SIZE", 4) == 6 else "+0000"

    def _ensure_capacity(self, addr: int):
        if not hasattr(self, "program_lines"):
            self.program_lines = []
        while len(self.program_lines) <= addr:
            self.program_lines.append(self._filler())



    def save_file_as(self):
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Program As",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not file_path:
                self.log_message("Save As cancelled.")
                return

            if not hasattr(self, "program_lines") or not self.program_lines:
                self.program_lines = []

            editable_lines = self.program_lines.copy()
            filler = "+000000" if getattr(self.memory, "WORD_SIZE", 4) == 6 else "+0000"
            total_size = getattr(self.memory, "size", len(self.memory.mem))

            output_lines = []
            for addr in range(total_size):
                if addr < len(editable_lines) and editable_lines[addr].strip():
                    line = editable_lines[addr].strip()
                else:
                    line = filler
                output_lines.append(line)

            content = "\n".join(output_lines)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.selected_file = file_path
            self.log_message(f"Saved full program memory ({len(output_lines)} lines) as: {file_path}")
            messagebox.showinfo("Saved", f"Program saved:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
            self.log_message(f"Save As error: {e}")


