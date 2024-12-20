# ui_elements.py
import tkinter as tk
import tkinter.ttk as ttk
from typing import List
from register_data import register

class UIElements:
    def __init__(self, root: tk.Tk, data_memory_base: int, program_counter_callback):
        self.root = root
        self.data_memory_base = data_memory_base
        self.program_counter_callback = program_counter_callback
        self.data_memory_values = [0] * (512 // 4)  # Initialize for 512 bytes / 4 bytes per word

        self._run_button_action = lambda: None
        self._step_button_action = lambda: None
        self._convert_button_action = lambda: None

        self._create_widgets()
        self._update_line_numbers()

    def _create_widgets(self):
        self.edit_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.edit_frame.place(x=0, y=0, width=900, height=450)

        self.line_numbers = tk.Text(self.edit_frame, width=4, padx=3, 
                                    takefocus=0, border=0,
                                    background='lightgray', state='disabled')
        self.line_numbers.pack(side='left', fill='y')

        self.scrollbar = tk.Scrollbar(
            self.edit_frame, 
            command=lambda *args: (
                self.edit_text.yview(*args), 
                self.line_numbers.yview(*args)
            )
        )
        self.scrollbar.pack(side='right', fill='y')

        self.edit_text = tk.Text(
            self.edit_frame, 
            wrap='none', 
            yscrollcommand=self.scrollbar.set,
            undo=True
        )
        self.edit_text.pack(side='right', fill='both', expand=True)

        self.edit_text.bind('<KeyRelease>', self._update_line_numbers)
        self.edit_text.bind("<MouseWheel>", self._on_mouse_wheel)
        self.edit_text.bind("<Control-z>", self._undo)
        self.edit_text.bind("<Control-y>", self._redo)

        self.register_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.register_frame.place(x=900, y=0, width=300, height=700)

        columns = ("Name", "Number", "Value")
        self.tree = ttk.Treeview(self.register_frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor='center')

        self.tree.tag_configure('evenrow', background='lightgray')
        self.tree.tag_configure('oddrow', background='white')

        for index, reg in enumerate(register):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(
                reg["name"], 
                reg["number"], 
                reg["value"]
            ), tags=(tag,))

        self.tree.pack(fill='both', expand=True)

        self.console_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.console_frame.place(x=0, y=450, width=900, height=250)

        self.console_output = tk.Text(
            self.console_frame, 
            height=8, 
            bg='black', 
            fg='white'
        )
        self.console_output.pack(fill='both', expand=True)

        self.pc_label = tk.Label(self.console_frame, text="PC: 0x00000000", font=("Arial", 12), anchor="w")
        self.pc_label.pack(side="top", fill="x")

        btn_frame = tk.Frame(self.console_frame)
        btn_frame.pack(side='top', fill='x')

        tk.Button(btn_frame, text="Clear", command=self._clear_registers).pack(side='left')
        tk.Button(btn_frame, text="Run", command=lambda: self._run_button_action()).pack(side='left')
        tk.Button(btn_frame, text="Step", command=lambda: self._step_button_action()).pack(side='left')
        tk.Button(btn_frame, text="Convert Machine Code", command=lambda: self._convert_button_action()).pack(side='left')

        self.instruction_frame = tk.Frame(self.root, relief='solid', borderwidth=1, bg='lightblue')
        self.instruction_frame.place(x=0, y=700, width=600, height=200)

        tk.Label(self.instruction_frame, text="Instruction Memory (Text Segment)", font=("Arial", 12), bg='lightblue').pack(anchor="w")

        columns = ("Address", "Source Code")
        self.instruction_memory_tree = ttk.Treeview(
            self.instruction_frame, 
            columns=columns, 
            show='headings'
        )

        for col in columns:
            self.instruction_memory_tree.heading(col, text=col)
            self.instruction_memory_tree.column(col, width=200, anchor='center')

        self.instruction_memory_tree.pack(fill="both", expand=True)

        self.machine_code_frame = tk.Frame(self.root, relief='solid', borderwidth=1, bg='lightyellow')
        self.machine_code_frame.place(x=600, y=700, width=600, height=200)

        tk.Label(self.machine_code_frame, text="Machine Code", font=("Arial", 12), bg='lightyellow').pack(anchor="w")

        columns = ("Instruction", "Machine Code")
        self.machine_code_tree = ttk.Treeview(
            self.machine_code_frame, 
            columns=columns, 
            show='headings'
        )

        for col in columns:
            self.machine_code_tree.heading(col, text=col)
            self.machine_code_tree.column(col, width=200, anchor='center')

        self.machine_code_tree.pack(fill="both", expand=True)
        
        self.data_frame = tk.Frame(self.root, relief='solid', borderwidth=1, bg='lightgreen')
        self.data_frame.place(x=0, y=900, width=1200, height=200)

        tk.Label(self.data_frame, text="Data Memory (Data Segment)", font=("Arial", 12), bg='lightgreen').pack(anchor="w")

        columns = ["Address"] + [f"Value(+{i*4})" for i in range(16)]
        
        self.data_memory_tree = ttk.Treeview(
            self.data_frame, 
            columns=columns, 
            show='headings'
        )

        for col in columns:
            self.data_memory_tree.heading(col, text=col)
            self.data_memory_tree.column(col, width=70, anchor='center')

        addresses = [f"0x{self.data_memory_base + (i*64):08X}" for i in range(8)]
        initial_values = ["0x00000000"] * 16
        
        for addr in addresses:
            self.data_memory_tree.insert("", "end", values=[addr] + initial_values)

        self.data_memory_tree.pack(fill="both", expand=True)

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