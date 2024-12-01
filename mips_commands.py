# mips_commands.py
import tkinter.ttk as ttk
from typing import Optional, Union

class MIPSCommands:
    def __init__(self, tree: ttk.Treeview):
        self.tree = tree

    def _find_register_item(self, register_name: str) -> Optional[str]:
        """Find the tree item for a specific register."""
        for item in self.tree.get_children():
            if self.tree.item(item, 'values')[0] == register_name:
                return item
        return None

    def get_register_value(self, register_name: str) -> int:
        """Get register value as integer."""
        item = self._find_register_item(register_name)
        return int(self.tree.item(item, 'values')[2], 16) if item else 0

    def update_register_value(self, register_name: str, new_value: Union[int, str]):
        """Update register value in the tree."""
        item = self._find_register_item(register_name)
        if item:
            hex_value = f"0x{int(new_value):08X}"
            self.tree.set(item, column="Value", value=hex_value)

    def clear_registers(self):
        """Reset all registers to zero."""
        for item in self.tree.get_children():
            self.tree.set(item, column="Value", value="0x00000000")

    def _binary_arithmetic(self, dest: str, src1: str, src2: str, operation):
        """Generic method for binary arithmetic operations."""
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = operation(val1, val2)
        self.update_register_value(dest, result)

    def execute_add_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x + y)

    def execute_sub_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x - y)

    def execute_mul_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x * y)

    def execute_div_command(self, dest: str, src1: str, src2: str) -> Optional[str]:
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        
        if val2 == 0:
            return "Error: Division by zero!"
        
        result = val1 // val2
        self.update_register_value(dest, result)
        return None

    def execute_and_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x & y)

    def execute_or_command(self, dest: str, src1: str, src2: str):
        self._binary_arithmetic(dest, src1, src2, lambda x, y: x | y)

    def execute_andi_command(self, dest: str, src1: str, immediate: int):
        val1 = self.get_register_value(src1)
        result = val1 & immediate
        self.update_register_value(dest, result)

    def execute_ori_command(self, dest: str, src1: str, immediate: int):
        val1 = self.get_register_value(src1)
        result = val1 | immediate
        self.update_register_value(dest, result)

    def execute_sll_command(self, dest: str, src1: str, shift_amount: int):
        val1 = self.get_register_value(src1)
        result = val1 << shift_amount
        self.update_register_value(dest, result)

    def execute_srl_command(self, dest: str, src1: str, shift_amount: int):
        val1 = self.get_register_value(src1)
        result = val1 >> shift_amount
        self.update_register_value(dest, result)