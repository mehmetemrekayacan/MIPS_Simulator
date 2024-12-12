# IDE Main File (MIPSIDE.py)
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict
from register_data import register
from mips_commands import MIPSCommands
from typing import Dict, List

class MIPSIDE:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MIPS IDE - Python")
        self.root.geometry("1200x900")

        self.program_counter = 0

        self.data_section: Dict[str, str] = {}
        self.current_line = 0
        self.instructions = []
        
        # Add new data memory attributes
        self.data_memory_base = 0x10010000  # Base address for data memory
        self.data_memory_values: List[int] = [0] * 8  # 8 slots for memory values
        
        self._create_widgets()
        self.commands = MIPSCommands(self.tree)

    def _create_widgets(self):
        # Left editing frame
        self.edit_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.edit_frame.place(x=0, y=0, width=900, height=450)

        # Line numbers
        self.line_numbers = tk.Text(self.edit_frame, width=4, padx=3, 
                                    takefocus=0, border=0,
                                    background='lightgray', state='disabled')
        self.line_numbers.pack(side='left', fill='y')

        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.edit_frame, 
            command=lambda *args: (
                self.edit_text.yview(*args), 
                self.line_numbers.yview(*args)
            )
        )
        self.scrollbar.pack(side='right', fill='y')

        # Edit text area
        self.edit_text = tk.Text(
            self.edit_frame, 
            wrap='none', 
            yscrollcommand=self.scrollbar.set,
            undo=True  # Undo özelliğini etkinleştir
        )
        self.edit_text.pack(side='right', fill='both', expand=True)

        self.edit_text.bind('<KeyRelease>', self._update_line_numbers)
        self.edit_text.bind("<MouseWheel>", self._on_mouse_wheel)
        self.edit_text.bind("<Control-z>", self._undo)  # Ctrl+Z için bağlama
        self.edit_text.bind("<Control-y>", self._redo)  # Ctrl+Y için bağlama

        # Register frame
        self.register_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.register_frame.place(x=900, y=0, width=300, height=700)

        # Register table
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

        # Console frame
        self.console_frame = tk.Frame(self.root, relief='solid', borderwidth=1)
        self.console_frame.place(x=0, y=450, width=900, height=250)

        self.console_output = tk.Text(
            self.console_frame, 
            height=8, 
            bg='black', 
            fg='white'
        )
        self.console_output.pack(fill='both', expand=True)

        self.pc_label = tk.Label(self.console_frame, text=f"PC: {self.program_counter}", font=("Arial", 12), anchor="w")
        self.pc_label.pack(side="top", fill="x")

        btn_frame = tk.Frame(self.console_frame)
        btn_frame.pack(side='top', fill='x')

        tk.Button(btn_frame, text="Clear", command=self._clear_registers).pack(side='left')
        tk.Button(btn_frame, text="Run", command=self._read_mips_code).pack(side='left')
        tk.Button(btn_frame, text="Step", command=self._step_execution).pack(side='left')

        # Instruction memory (Text Segment)
        self.instruction_frame = tk.Frame(self.root, relief='solid', borderwidth=1, bg='lightblue')
        self.instruction_frame.place(x=0, y=700, width=600, height=200)

        tk.Label(self.instruction_frame, text="Instruction Memory (Text Segment)", font=("Arial", 12), bg='lightblue').pack(anchor="w")

        self.instruction_memory = tk.Text(self.instruction_frame, height=10, bg="white", fg="black")
        self.instruction_memory.pack(fill="both", expand=True)

        # Modify the data memory frame to use a Treeview instead of Text
        self.data_frame = tk.Frame(self.root, relief='solid', borderwidth=1, bg='lightgreen')
        self.data_frame.place(x=600, y=700, width=600, height=200)

        tk.Label(self.data_frame, text="Data Memory (Data Segment)", font=("Arial", 12), bg='lightgreen').pack(anchor="w")

        # Create Treeview for data memory
        columns = ["Address", "Value(+0)", "Value(+4)", "Value(+8)", "Value(+12)", 
                   "Value(+16)", "Value(+20)", "Value(+24)"]
        
        self.data_memory_tree = ttk.Treeview(
            self.data_frame, 
            columns=columns, 
            show='headings'
        )

        # Configure columns
        for col in columns:
            self.data_memory_tree.heading(col, text=col)
            self.data_memory_tree.column(col, width=70, anchor='center')

        # Insert initial row with base address
        addresses = [f"0x{self.data_memory_base + (i*4):08X}" for i in range(8)]
        initial_values = ["0x00000000"] * 8
        
        self.data_memory_tree.insert("", "end", values=[addresses[0]] + initial_values)

        self.data_memory_tree.pack(fill="both", expand=True)

    def _update_program_counter_display(self):
        self.pc_label.config(text=f"PC: {self._to_hex(self.program_counter)}")

    def _update_data_memory_display(self):
        """Update the data memory display with current values."""
        # Clear existing rows
        for i in self.data_memory_tree.get_children():
            self.data_memory_tree.delete(i)

        # Recreate addresses
        addresses = [f"0x{self.data_memory_base + (i*4):08X}" for i in range(8)]
        
        # Convert values to hex strings, padding with zeros
        hex_values = [f"0x{val:08X}" if val is not None else "0x00000000" 
                      for val in self.data_memory_values]
        
        # Insert updated row
        self.data_memory_tree.insert("", "end", values=[addresses[0]] + hex_values)

    def _handle_data_memory_write(self, variable_name: str, value: int):
        """Handle writing values to data memory."""
        # Find the index of the variable in data_section
        variable_index = list(self.data_section.keys()).index(variable_name)
        
        # Update the value in data_memory_values
        self.data_memory_values[variable_index] = value
        
        # Update the display
        self._update_data_memory_display()

    def _undo(self, event=None):
        """Handle Ctrl+Z (undo)."""
        try:
            self.edit_text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def _redo(self, event=None):
        """Handle Ctrl+Y (redo)."""
        try:
            self.edit_text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def _clear_registers(self):
        self.commands.clear_registers()  # Clear the registers
        self.program_counter = 0  # Reset the program counter
        self._update_program_counter_display()  # Update the display with the reset PC
        self._log_to_console("Registers cleared and PC reset.")

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

    def _to_hex(self, value: int) -> str:
        """Convert integer to hexadecimal format."""
        return f"0x{int(value):08X}"

    def _parse_data_section(self, lines):
        """Parse .data section more robustly."""
        data_section = {}
        
        try:
            # Find .data section if it exists
            data_start = next((i for i, line in enumerate(lines) if line.strip() == ".data"), None)
            
            if data_start is not None:
                # Try to find .text section or end of lines
                try:
                    data_end = next(i for i, line in enumerate(lines[data_start+1:], start=data_start+1) 
                                    if line.strip() == ".text" or not line.strip())
                except StopIteration:
                    data_end = len(lines)

                for line in lines[data_start+1:data_end]:
                    line = line.strip()
                    if ":" in line and ".word" in line:
                        parts = line.split(":")
                        var_name = parts[0].strip()
                        value_part = parts[1].strip().split()
                        
                        if len(value_part) > 1 and value_part[0] == ".word":
                            try:
                                # Store as integer
                                var_value = int(value_part[1])
                                data_section[var_name] = var_value
                            except ValueError:
                                pass
        except Exception:
            # If no .data section found, return an empty dictionary
            pass
        
        return data_section

    def _parse_text_section(self, lines):
        """Parse .text section more robustly, handling inline comments and optional main label."""
        instructions = []
        address = 0x00400000  # Start address for instructions

        try:
            # Try to find main label, but don't fail if it's not there
            main_start = next((i for i, line in enumerate(lines) if line.strip() == "main:"), 0)
            
            for line in lines[main_start+1:]:
                line = line.strip()
                if not line or line.startswith(('.', ':')):
                    continue
                if '#' in line:
                    line = line.split('#')[0].strip()

                if line:
                    instructions.append({
                        "address": f"0x{address:08X}",
                        "source": line
                    })
                    address += 4
                
            return instructions
        except Exception:
            # If parsing fails, return an empty instruction list
            return []
    
    def _read_mips_code(self):
        """Load MIPS code, parse sections, and map labels."""
        self.console_output.delete('1.0', 'end')
        code = self.edit_text.get('1.0', 'end-1c')
        lines = [line.strip() for line in code.split('\n') if line.strip()]

        self.data_section = self._parse_data_section(lines)
        self._log_to_console(f"Data Section: {self.data_section}")

        # Parse and store instructions with address and source line
        self.instructions = self._parse_text_section(lines)
        self.labels = self._map_labels([instr["source"] for instr in self.instructions])
        self.current_line = 0

        # Display instructions with address and source
        self.instruction_memory.delete('1.0', 'end')
        for instr in self.instructions:
            self.instruction_memory.insert(
                'end', 
                f"{instr['address']}: {instr['source']}\n"
            )

        self._log_to_console("Loaded instructions. Ready to step through.")

        self.program_counter = 0  # Reset the program counter
        self._update_program_counter_display()

        # Set $ra to point to a termination point
        self.commands.update_register_value("$ra", len(self.instructions) * 4)
        self._log_to_console(f"Set $ra to {len(self.instructions) * 4}")

    def _map_labels(self, instructions):
        """Etiketlerin koddaki sırasını belirler."""
        labels = {}
        for index, instruction in enumerate(instructions):
            if ':' in instruction:  # Etiket var mı?
                label, _ = instruction.split(':', 1)
                labels[label.strip()] = index
        return labels

    def _log_to_console(self, message: str):
        """Convenience method to log messages to console."""
        self.console_output.insert('end', f"{message}\n")

    def _step_execution(self):
        if self.current_line >= len(self.instructions):
            self._log_to_console("No more instructions to execute.")
            return

        instruction = self.instructions[self.current_line]
        line = instruction["source"]  # Kaynak MIPS kodunu al
        address = instruction["address"]  # Adres bilgisini al

        parts = [part.strip() for part in line.replace(",", " ").split()]
        command = parts[0]

        self.program_counter += 4
        self._update_program_counter_display()

        self._log_to_console(f"Executing at {address}: {line}")

        instruction_map = {
            "lw": self._handle_lw,
            "sw": self._handle_sw,
            "add": self._handle_arithmetic,
            "sub": self._handle_arithmetic,
            "mul": self._handle_arithmetic,
            "div": self._handle_arithmetic,
            "and": self._handle_logical,
            "or": self._handle_logical,
            "andi": self._handle_immediate_logical,
            "ori": self._handle_immediate_logical,
            "sll": self._handle_shift,
            "srl": self._handle_shift,
            "slt": self._handle_slt,
            "beq": self._handle_branch,
            "bne": self._handle_branch,
            "j": self._handle_jump,
            "jal": self._handle_jump,
            "addi": self._handle_immediate_arithmetic,
            "jr": self._handle_jr,
        }

        handler = instruction_map.get(command)
        if handler:
            result = handler(command, parts[1:])
            if result:
                self._log_to_console(result)
            else:
                self._log_to_console(f"Executed: {line}")
        else:
            self._log_to_console(f"Unsupported instruction: {command}")

        self.current_line += 1

    def _handle_arithmetic(self, command, parts):
        dest, src1, src2 = parts
        method_map = {
            "add": self.commands.execute_add_command,
            "sub": self.commands.execute_sub_command,
            "mul": self.commands.execute_mul_command,
            "div": self.commands.execute_div_command
        }
        method = method_map[command]
        return method(dest, src1, src2)

    def _handle_logical(self, command, parts):
        dest, src1, src2 = parts
        method_map = {
            "and": self.commands.execute_and_command,
            "or": self.commands.execute_or_command
        }
        method = method_map[command]
        method(dest, src1, src2)

    def _handle_immediate_logical(self, command, parts):
        dest, src1, immediate = parts
        method_map = {
            "andi": self.commands.execute_andi_command,
            "ori": self.commands.execute_ori_command
        }
        method = method_map[command]
        method(dest, src1, int(immediate))

    def _handle_shift(self, command, parts):
        dest, src1, shift_amount = parts
        method_map = {
            "sll": self.commands.execute_sll_command,
            "srl": self.commands.execute_srl_command
        }
        method = method_map[command]
        method(dest, src1, int(shift_amount))

    def _handle_lw(self, _, parts):
        """Enhanced load word to update data memory display."""
        register, var_name = parts
        if var_name in self.data_section:
            # Load value into register
            value = self.data_section[var_name]
            self.commands.update_register_value(register, value)
            
            # Update data memory display
            self._handle_data_memory_write(var_name, value)

    def _handle_sw(self, _, parts):
        """Enhanced store word to update data memory display."""
        if len(parts) == 2:
            src_reg, memory_address = parts
            
            # If memory_address is a variable name in data section
            if memory_address in self.data_section:
                # Get value from source register
                value = self.commands.get_register_value(src_reg)
                
                # Update data section
                self.data_section[memory_address] = value
                
                # Update data memory display
                self._handle_data_memory_write(memory_address, value)
                
                self._log_to_console(f"Stored {value} in {memory_address}")
            else:
                # Fallback to existing sw command handling
                result = self.commands.execute_sw_command(src_reg, memory_address)
                if result:
                    self._log_to_console(result)
        else:
            self._log_to_console(f"Invalid sw instruction: {parts}")

    def _handle_slt(self, _, parts):
        """Handle set less than instruction"""
        dest, src1, src2 = parts
        self.commands.execute_slt_command(dest, src1, src2)

    def _handle_branch(self, command, parts):
        """Branch talimatlarını işler."""
        reg1, reg2, label = parts
        val1 = self.commands.get_register_value(reg1)
        val2 = self.commands.get_register_value(reg2)
        
        if command == "beq" and val1 == val2:
            self.program_counter = self.labels[label] * 4  # Dallanma hedefine atla
            self.current_line = self.labels[label]
            self._update_program_counter_display()
            return f"Branching to {label} (PC={self.program_counter})"
        elif command == "bne" and val1 != val2:
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self._update_program_counter_display()
            return f"Branching to {label} (PC={self.program_counter})"

    def _handle_jump(self, command, parts):
        """Jump talimatlarını işler."""
        label = parts[0]
        if command == "j":
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self._update_program_counter_display()
            return f"Jumping to {label} (PC={self.program_counter})"
        elif command == "jal":
            self.commands.update_register_value("$ra", self.program_counter + 4)  # Return adresini kaydet
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self._update_program_counter_display()
            return f"Jumping to {label} and storing return address (PC={self.program_counter})"
        
    def _handle_immediate_arithmetic(self, command, parts):
        dest, src1, immediate = parts
        self.commands.execute_addi_command(dest, src1, int(immediate))

    def _handle_jr(self, _, parts):
        """Handle jump register instruction with improved logic"""
        register = parts[0]
        return_address = self.commands.get_register_value(register)
        
        self._log_to_console(f"Jr instruction: Register {register}, Value: {return_address}")
        
        # If $ra is 0 or beyond instructions, consider it a program termination
        if return_address == 0 or return_address >= len(self.instructions) * 4:
            self._log_to_console("Program execution completed.")
            # Reset or stop execution
            self.current_line = len(self.instructions)
            self.program_counter = len(self.instructions) * 4
            self._update_program_counter_display()
            return "Program end: Jumped to invalid/termination address"
        
        # Calculate the line number based on the address
        target_line = return_address // 4
        
        self.program_counter = return_address
        self.current_line = target_line
        self._update_program_counter_display()
        
        self._log_to_console(f"Jumping to line {target_line} (PC={self.program_counter})")
        return f"Jumping to line {target_line} (PC={self.program_counter})"

if __name__ == "__main__":
    root = tk.Tk()
    MIPSIDE(root)
    root.mainloop()