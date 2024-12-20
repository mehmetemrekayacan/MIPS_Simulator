# mips_commands.py
import tkinter.ttk as ttk
from typing import Optional, Union

class MIPSCommands:
    def __init__(self, tree: ttk.Treeview):
        self.tree = tree

    def _find_register_item(self, register_name: str) -> Optional[str]:
        for item in self.tree.get_children():
            if self.tree.item(item, 'values')[0] == register_name:
                return item
        return None

    def get_register_value(self, register_name):
        item = self._find_register_item(register_name)
        if item:
            hex_value = self.tree.item(item, 'values')[2]
            try:
                if hex_value.startswith('-0x'):
                    return int(hex_value, 16)
                return int(hex_value, 16)
            except ValueError:
                return 0
        return 0

    def update_register_value(self, register_name: str, new_value: Union[int, str]):
        item = self._find_register_item(register_name)
        if item:
            if isinstance(new_value, int):
                hex_value = f"0x{new_value & 0xFFFFFFFF:08X}"
            else:
                hex_value = f"0x{int(new_value, 16) & 0xFFFFFFFF:08X}"
            self.tree.set(item, column="Value", value=hex_value)

    def clear_registers(self):
        for item in self.tree.get_children():
            self.tree.set(item, column="Value", value="0x00000000")

    def _binary_arithmetic(self, dest: str, src1: str, src2: str, operation):
      val1 = self.get_register_value(src1)
      val2 = self.get_register_value(src2)
      result = operation(val1, val2)
      self.update_register_value(dest, result)

    def execute_add_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x + y)

    def execute_sub_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x - y)
    
    def execute_and_command(self, dest: str, src1: str, src2: str):
      self._binary_arithmetic(dest, src1, src2, lambda x, y: x & y)

    def execute_or_command(self, dest: str, src1: str, src2: str):
      self._binary_arithmetic(dest, src1, src2, lambda x, y: x | y)

    def execute_sll_command(self, dest: str, src1: str, shift_amount: int):
        val1 = self.get_register_value(src1)
        result = val1 << shift_amount
        self.update_register_value(dest, result)

    def execute_srl_command(self, dest: str, src1: str, shift_amount: int):
        val1 = self.get_register_value(src1)
        result = val1 >> shift_amount
        self.update_register_value(dest, result)

    def execute_slt_command(self, dest: str, src1: str, src2: str):
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = 1 if val1 < val2 else 0
        self.update_register_value(dest, result)

    def execute_beq_command(self, reg1: str, reg2: str, label: str):
        val1 = self.get_register_value(reg1)
        val2 = self.get_register_value(reg2)
        
        if val1 == val2:
            return f"Branching to {label}"
        return None

    def execute_bne_command(self, reg1: str, reg2: str, label: str):
        val1 = self.get_register_value(reg1)
        val2 = self.get_register_value(reg2)
        
        if val1 != val2:
            return f"Branching to {label}"
        return None

    def execute_j_command(self, label: str):
        return f"Jumping to {label}"

    def execute_jal_command(self, label: str):
        self.update_register_value("$ra", self.current_line + 1)
        return f"Jumping to {label} and storing return address"

    def execute_sw_command(self, src_reg: str, memory_address: str):
        value = self.get_register_value(src_reg)
        
        try:
            import re
            match = re.match(r'(-?\d+)\((\$\w+)\)', memory_address)
            if match:
                offset = int(match.group(1))
                base_reg = match.group(2)
                base_value = self.get_register_value(base_reg)
                
                memory_loc = base_value + offset
                return f"Stored {value} at memory location {memory_loc}"
            else:
                return f"Invalid memory address format: {memory_address}"
        except Exception as e:
            return f"Error in store word: {str(e)}"
        
    def execute_addi_command(self, dest: str, src1: str, immediate: int):
        val1 = self.get_register_value(src1)
        result = val1 + immediate
        self.update_register_value(dest, result)

    def execute_jr_command(self, register: str):
        return f"Jumping to address in {register}"