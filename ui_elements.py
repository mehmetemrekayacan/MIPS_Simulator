# ui_elements.py
import tkinter as tk
import tkinter.ttk as ttk
from typing import List
from register_data import register

class MIPSUI:
    def __init__(self, root: tk.Tk, data_memory_base: int, program_counter_callback):
        self.root = root
        # Set theme colors with new color scheme
        self.COLORS = {
            'bg_dark': '#222831',    # Darkest background
            'bg_light': '#393E46',   # Dark gray
            'accent': '#00ADB5',     # Cyan/Teal
            'text': '#EEEEEE',       # Light gray
            'success': '#00ADB5',    # Cyan/Teal
            'warning': '#00ADB5',    # Cyan/Teal
            'error': '#00ADB5'       # Cyan/Teal
        }
        
        # Configure root window
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        self.data_memory_base = data_memory_base
        self.program_counter_callback = program_counter_callback
        self.data_memory_values = [0] * (512 // 4)  # Initialize for 512 bytes / 4 bytes per word

        self._run_button_action = lambda: None
        self._step_button_action = lambda: None
        self._convert_button_action = lambda: None

        self._create_widgets()
        self._update_line_numbers()

    def _create_widgets(self):
        # Main frame styling
        self.main_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        self.main_frame.pack(fill="both", expand=True)

        # Top frame for buttons and PC
        top_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        top_frame.pack(side="top", fill="x", pady=(10,5))  # Üstten 10px, alttan 5px padding

        # Content frame - ana içerik için
        content_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        content_frame.pack(fill="both", expand=True, pady=10)  # Üst ve alttan padding

        # Sol taraf (editor ve console) için frame
        left_section = tk.Frame(content_frame, bg=self.COLORS['bg_dark'], width=350)  # 400px'den 350px'e düşür
        left_section.pack(side="left", fill="both", expand=True, padx=(5,15))  # Sağ padding arttır
        left_section.pack_propagate(False)  # Boyutu sabitle

        # Editor frame
        self.edit_frame = tk.Frame(left_section, bg=self.COLORS['bg_light'], height=300)  # Sabit yükseklik
        self.edit_frame.pack(fill="both", expand=True, pady=(0,10))
        self.edit_frame.pack_propagate(False)  # Boyutu sabitle

        # Console frame
        self.console_frame = tk.Frame(left_section, bg=self.COLORS['bg_light'], height=180)  # 120'den 180'e çıkar
        self.console_frame.pack(fill="x", expand=False, pady=(0,5))
        self.console_frame.pack_propagate(False)

        # Sağ üst kısım için frame
        right_top_section = tk.Frame(content_frame, bg=self.COLORS['bg_dark'])
        right_top_section.pack(side="right", fill="y", padx=15)  # padding'i 10'dan 15'e çıkar

        # Machine Code ve Register frame'leri arasına padding
        self.machine_code_frame = tk.Frame(right_top_section, bg=self.COLORS['bg_light'])
        self.machine_code_frame.pack(side="left", fill="both", padx=(0,5))  # Sağ padding

        self.register_frame = tk.Frame(right_top_section, bg=self.COLORS['bg_light'])
        self.register_frame.pack(side="right", fill="both", padx=(5,0))  # Sol padding

        # Alt kısım için frame
        bottom_section = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        bottom_section.pack(side="bottom", fill="x", pady=10)  # Üst ve alttan padding

        # Instruction Memory ve Data Memory arasına padding
        self.instruction_frame = tk.Frame(bottom_section, bg=self.COLORS['bg_light'])
        self.instruction_frame.pack(fill="x", pady=(0,5))  # Alt padding

        self.data_frame = tk.Frame(bottom_section, bg=self.COLORS['bg_light'])
        self.data_frame.pack(fill="x", pady=(5,0))  # Üst padding

        # Terminal title
        tk.Label(
            self.console_frame,
            text="Terminal",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor="w", padx=5, pady=2)

        # Console gradient frame
        console_gradient = tk.Canvas(
            self.console_frame,
            bg=self.COLORS['bg_dark'],
            highlightthickness=0,
            height=8
        )
        console_gradient.pack(fill='x', padx=5)

        # Create gradient effect
        for i in range(8):
            color = self._interpolate_color(
                self.COLORS['bg_dark'],
                self.COLORS['bg_light'],
                i/8
            )
            console_gradient.create_line(0, i, 10000, i, fill=color)
        
        # Console output
        self.console_output = tk.Text(
            self.console_frame, 
            height=8,
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['success'],
            font=('Consolas', 10),
            padx=10,
            pady=5
        )
        self.console_output.pack(fill='both', expand=True, padx=5, pady=(0,5))

        # Add labels for each section
        register_title_frame = tk.Frame(self.register_frame, bg=self.COLORS['bg_light'])
        register_title_frame.pack(fill='x', pady=(2,0))
        tk.Label(
            register_title_frame,
            text="Registers",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor="w", padx=5, pady=2)

        machine_code_title_frame = tk.Frame(self.machine_code_frame, bg=self.COLORS['bg_light'])
        machine_code_title_frame.pack(fill='x', pady=(2,0))
        tk.Label(
            machine_code_title_frame,
            text="Machine Code",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor="w", padx=5, pady=2)

        instruction_title_frame = tk.Frame(self.instruction_frame, bg=self.COLORS['bg_light'])
        instruction_title_frame.pack(fill='x', pady=(2,0))
        tk.Label(
            instruction_title_frame,
            text="Instruction Memory",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor="w", padx=5, pady=2)

        data_title_frame = tk.Frame(self.data_frame, bg=self.COLORS['bg_light'])
        data_title_frame.pack(fill='x', pady=(2,0))
        tk.Label(
            data_title_frame,
            text="Data Memory",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor="w", padx=5, pady=2)

        # Button styling
        button_style = {
            'bg': self.COLORS['accent'],
            'fg': self.COLORS['bg_dark'],
            'font': ('Arial', 10, 'bold'),
            'width': 12,
            'relief': 'flat',
            'padx': 10,
            'pady': 5
        }

        tk.Button(top_frame, text="Clear", command=self._clear_registers, **button_style).pack(side='left', padx=5)
        tk.Button(top_frame, text="Run", command=lambda: self._run_button_action(), **button_style).pack(side='left', padx=5)
        tk.Button(top_frame, text="Step", command=lambda: self._step_button_action(), **button_style).pack(side='left', padx=5)
        tk.Button(top_frame, text="Convert", command=lambda: self._convert_button_action(), **button_style).pack(side='left', padx=5)

        # PC Counter Label styling
        self.pc_label = tk.Label(
            top_frame, 
            text="PC: 0x00000000",
            font=("Consolas", 12, "bold"),
            fg=self.COLORS['accent'],
            bg=self.COLORS['bg_dark']
        )
        self.pc_label.pack(side="right", padx=15)

        # Line numbers styling
        self.line_numbers = tk.Text(
            self.edit_frame,
            width=4,
            padx=5,
            pady=5,
            takefocus=0,
            border=0,
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text'],
            font=('Consolas', 11)
        )
        self.line_numbers.pack(side='left', fill='y')

        # Editor text styling
        self.edit_text = tk.Text(
            self.edit_frame, 
            wrap='none', 
            undo=True,
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            font=('Consolas', 11),
            pady=5,
            padx=5
        )
        self.edit_text.pack(side='left', fill='both', expand=True)

        self.edit_text.bind('<KeyRelease>', self._update_line_numbers)
        self.edit_text.bind("<MouseWheel>", self._on_mouse_wheel)
        self.edit_text.bind("<Control-z>", self._undo)
        self.edit_text.bind("<Control-y>", self._redo)
        
        # Treeview style configuration
        style = ttk.Style()
        
        # Configure all frames to use bg_dark
        style.configure('TFrame', background=self.COLORS['bg_dark'])
        
        # Configure Treeview and its components
        style.configure(
            "Treeview",
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text'],
            fieldbackground=self.COLORS['bg_dark'],
            borderwidth=0
        )
        
        style.configure(
            "Treeview.Heading",
            background=self.COLORS['accent'],
            foreground=self.COLORS['bg_dark'],
            relief='flat',
            borderwidth=0,
            font=('Arial', 10, 'bold')
        )
        
        # Remove Treeview borders
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        # Configure selection color
        style.map('Treeview',
            background=[('selected', '#00ADB5')],
            foreground=[('selected', '#EEEEEE')]
        )

        # Custom style for all Treeviews
        style.configure(
            "Custom.Treeview",
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text'],
            fieldbackground=self.COLORS['bg_dark'],
            borderwidth=0,
            font=('Consolas', 10)
        )

        # Update frame configurations
        for frame in [self.register_frame, self.machine_code_frame, 
                     self.instruction_frame, self.data_frame]:
            frame.configure(
                bg=self.COLORS['bg_dark'],
                highlightthickness=0,  # Remove highlight border
                borderwidth=0  # Remove border
            )

        # Common Treeview configurations
        treeview_style = {
            'show': 'headings',
            'selectmode': 'browse'
        }

        # Register TreeView
        columns = ("Name", "Number", "Value")
        self.tree = ttk.Treeview(
            self.register_frame,
            columns=columns,
            height=8,
            **treeview_style
        )

        for col, width in zip(columns, [60, 60, 80]):  # Sütun genişliklerini küçült
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        self.tree.tag_configure('evenrow', background=self.COLORS['bg_light'])
        self.tree.tag_configure('oddrow', background=self.COLORS['bg_dark'])

        for index, reg in enumerate(register):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(
                reg["name"], 
                reg["number"], 
                reg["value"]
            ), tags=(tag,))

        self.tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Instruction Memory TreeView
        columns = ("Address", "Source Code")
        self.instruction_memory_tree = ttk.Treeview(
            self.instruction_frame, 
            columns=columns, 
            height=10,
            **treeview_style
        )

        for col in columns:
            self.instruction_memory_tree.heading(col, text=col)
            self.instruction_memory_tree.column(col, width=200, anchor='center')

        self.instruction_memory_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Data Memory TreeView
        columns = ["Address"] + [f"Value(+{i*4})" for i in range(16)]
        self.data_memory_tree = ttk.Treeview(
            self.data_frame, 
            columns=columns, 
            height=10,
            **treeview_style
        )

        for col in columns:
            self.data_memory_tree.heading(col, text=col)
            self.data_memory_tree.column(col, width=70, anchor='center')

        self.data_memory_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Machine Code TreeView
        columns = ("Instruction", "Machine Code")
        self.machine_code_tree = ttk.Treeview(
            self.machine_code_frame, 
            columns=columns, 
            height=10,
            **treeview_style
        )

        for col, width in zip(columns, [150, 200]):  # 100,100'den 150,200'e çıkarıldı
            self.machine_code_tree.heading(col, text=col)
            self.machine_code_tree.column(col, width=width, anchor='center')

        self.machine_code_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Add highlight tag for register changes
        self.tree.tag_configure('highlight', 
            background='#00ADB5',     # Cyan/Teal for highlight
            foreground='#EEEEEE'      # Light gray text
        )

        # Update evenrow/oddrow colors
        self.tree.tag_configure('evenrow', 
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text']
        )
        self.tree.tag_configure('oddrow', 
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text']
        )

        # Set background color for all treeviews
        for tree in [self.tree, self.instruction_memory_tree, 
                     self.data_memory_tree, self.machine_code_tree]:
            tree.configure(
                style='Custom.Treeview',
                height=6,
                show='headings',
                selectmode='browse'
            )
            
            # Configure tags for alternating row colors
            tree.tag_configure('evenrow', 
                background=self.COLORS['bg_light'],
                foreground=self.COLORS['text']
            )
            tree.tag_configure('oddrow', 
                background=self.COLORS['bg_dark'],
                foreground=self.COLORS['text']
            )

        # Sağ üst kısım için genişlik ayarı
        self.machine_code_frame.configure(width=370)  # 220'den 370'e çıkarıldı
        self.register_frame.configure(width=220)      # Bu aynı kalıyor
        self.machine_code_frame.pack_propagate(False)
        self.register_frame.pack_propagate(False)

        # Console yükseklik ayarı
        self.console_frame.pack_propagate(False)  # Console yüksekliğini sabitle

    def _update_line_numbers(self, event=None):
        lines = self.edit_text.get('1.0', 'end-1c').split('\n')
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert(
            '1.0', 
            "\n".join(str(i + 1) for i in range(len(lines)))
        )
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.edit_text.yview()[0])

    def _on_mouse_wheel(self, event):
        scroll_amount = -1 * (event.delta // 120)
        self.edit_text.yview_scroll(scroll_amount, "units")
        self.line_numbers.yview_scroll(scroll_amount, "units")
        return "break"

    def _undo(self, event=None):
        try:
            self.edit_text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def _redo(self, event=None):
        try:
            self.edit_text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def _clear_registers(self):
        self.console_output.delete('1.0', 'end')
        for item in self.instruction_memory_tree.get_children():
            self.instruction_memory_tree.delete(item)

        for item in self.machine_code_tree.get_children():
            self.machine_code_tree.delete(item)
        
        initial_values = ["0x00000000"] * 16
        for i in self.data_memory_tree.get_children():
            self.data_memory_tree.delete(i)
        
        addresses = [f"0x{self.data_memory_base + (i*64):08X}" for i in range(8)]

        for addr in addresses:
            self.data_memory_tree.insert("", "end", values=[addr] + initial_values)
    
        for item in self.tree.get_children():
            self.tree.set(item, column="Value", value="0x00000000")
        self.update_program_counter_display(0)
        self.program_counter_callback(0)

    def update_program_counter_display(self, pc: int):
        hex_pc = f"0x{pc:08X}"
        self.pc_label.config(text=f"PC: {hex_pc}")

    def update_data_memory_display(self, data_memory_values: List[int]):
      for i in self.data_memory_tree.get_children():
          self.data_memory_tree.delete(i)
            
      addresses = [f"0x{self.data_memory_base + (i*64):08X}" for i in range(8)]
      
      for addr_idx, addr in enumerate(addresses):
            row_values = [addr]
            for val_idx in range(16):
                mem_index = addr_idx * 16 + val_idx
                if mem_index < len(data_memory_values):
                    val = data_memory_values[mem_index]
                    hex_val = f"0x{val:08X}" if val is not None else "0x00000000"
                    row_values.append(hex_val)
                else:
                    row_values.append("0x00000000")

            self.data_memory_tree.insert("", "end", values=row_values)

    def get_mips_code(self):
        return self.edit_text.get('1.0', 'end-1c')

    def log_to_console(self, message):
        self.console_output.insert('end', f"{message}\n")
        self.console_output.see('end')  # Automatically scroll to the bottom

    def set_instruction_memory(self, instructions: List[dict]):
        for item in self.instruction_memory_tree.get_children():
             self.instruction_memory_tree.delete(item)
        
        for instr in instructions:
            self.instruction_memory_tree.insert("", "end", values=(
                instr['address'],
                instr['source']
            ))

    
    def set_machine_code_output(self, machine_code_pairs: List[tuple]):
        for item in self.machine_code_tree.get_children():
            self.machine_code_tree.delete(item)
            
        for instruction, code in machine_code_pairs:
            self.machine_code_tree.insert("", "end", values=(
                instruction,
                code
            ))
          
    def get_register_tree(self) -> ttk.Treeview:
      return self.tree

    def _interpolate_color(self, color1, color2, fraction):
        """Create a color that is between color1 and color2"""
        def hex_to_rgb(color):
            return tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        def rgb_to_hex(rgb):
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        
        c1 = hex_to_rgb(color1)
        c2 = hex_to_rgb(color2)
        
        rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * fraction) for i in range(3))
        return rgb_to_hex(rgb)