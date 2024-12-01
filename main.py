# IDE Main File (MIPSIDE.py)
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict
from register_data import register
from mips_commands import MIPSCommands

class MIPSIDE:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MIPS IDE - Python")
        self.root.geometry("1200x700")

        self.data_section: Dict[str, str] = {}
        self.current_line = 0
        self.instructions = []
        
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
            yscrollcommand=self.scrollbar.set
        )
        self.edit_text.pack(side='right', fill='both', expand=True)

        self.edit_text.bind('<KeyRelease>', self._update_line_numbers)
        self.edit_text.bind("<MouseWheel>", self._on_mouse_wheel)

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

        btn_frame = tk.Frame(self.console_frame)
        btn_frame.pack(side='top', fill='x')

        tk.Button(btn_frame, text="Clear", command=self._clear_registers).pack(side='left')
        tk.Button(btn_frame, text="Run", command=self._read_mips_code).pack(side='left')
        tk.Button(btn_frame, text="Step", command=self._step_execution).pack(side='left')

    def _clear_registers(self):
        self.commands.clear_registers()
        self._log_to_console("Registers cleared.")

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
            data_start = next(i for i, line in enumerate(lines) if line.strip() == ".data")
            data_end = next(i for i, line in enumerate(lines[data_start+1:], start=data_start+1) if line.strip() == ".text")
        except StopIteration:
            return data_section

        for line in lines[data_start+1:data_end]:
            line = line.strip().replace(",", " ")
            parts = line.split()
            if len(parts) >= 2 and ":" in parts[0]:
                var_name = parts[0].replace(":", "")
                try:
                    var_value = self._to_hex(int(parts[-1]))
                    data_section[var_name] = var_value
                except ValueError:
                    pass
        return data_section

    def _parse_text_section(self, lines):
        """Parse .text section more robustly."""
        try:
            main_start = next(i for i, line in enumerate(lines) if line.strip() == "main:")
            instructions = [
                line.strip() for line in lines[main_start+1:] 
                if line.strip() and not line.strip().startswith(('.', ':'))
            ]
            return instructions
        except StopIteration:
            return []

    def _read_mips_code(self):
        self.console_output.delete('1.0', 'end')
        code = self.edit_text.get('1.0', 'end-1c')
        lines = [line.strip() for line in code.split('\n') if line.strip()]

        self.data_section = self._parse_data_section(lines)
        self._log_to_console(f"Data Section: {self.data_section}")

        self.instructions = self._parse_text_section(lines)
        self.current_line = 0
        self._log_to_console("Loaded instructions. Ready to step through.")

    def _log_to_console(self, message: str):
        """Convenience method to log messages to console."""
        self.console_output.insert('end', f"{message}\n")

    def _step_execution(self):
        """Execute next instruction with improved parsing."""
        if self.current_line >= len(self.instructions):
            self._log_to_console("No more instructions to execute.")
            return

        line = self.instructions[self.current_line]
        parts = [part.strip() for part in line.replace(",", " ").split()]
        command = parts[0]

        instruction_map = {
            "lw": self._handle_lw,
            "add": self._handle_arithmetic,
            "sub": self._handle_arithmetic,
            "mul": self._handle_arithmetic,
            "div": self._handle_arithmetic,
            "and": self._handle_logical,
            "or": self._handle_logical,
            "andi": self._handle_immediate_logical,
            "ori": self._handle_immediate_logical,
            "sll": self._handle_shift,
            "srl": self._handle_shift
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

    def _handle_lw(self, _, parts):
        register, var_name = parts
        if var_name in self.data_section:
            self.commands.update_register_value(
                register, 
                int(self.data_section[var_name], 16)
            )

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

if __name__ == "__main__":
    root = tk.Tk()
    MIPSIDE(root)
    root.mainloop()