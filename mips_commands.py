# mips_commands.py
import tkinter.ttk as ttk
from typing import Optional, Union, Callable, Dict

class MIPSProcessor:
    def __init__(self, tree: ttk.Treeview):
        self.tree = tree
        self.last_highlighted_item = None  # Track last highlighted item
        self._operation_map: Dict[str, Callable[[int, int], int]] = {
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'and': lambda x, y: x & y,
            'or': lambda x, y: x | y,
            'xor': lambda x, y: x ^ y,
            'sll': lambda x, y: x << y,
            'srl': lambda x, y: x >> y,
            'andi': lambda x, y: x & y,
            'ori': lambda x, y: x | y,
            'bkm':lambda x,y:(x*2)*(y*-1)
        }

    def _find_register_item(self, register_name: str) -> Optional[str]:
        """Find register item in treeview."""
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == register_name:
                return item
        return None

    def get_register_value(self, register_name: str) -> int:
        """Get register value as integer."""
        item = self._find_register_item(register_name)
        if not item:
            raise ValueError(f"Register {register_name} not found")
            
        hex_value = self.tree.item(item)['values'][2]
        try:
            return int(hex_value, 16) if not hex_value.startswith('-') else -int(hex_value[1:], 16)
        except ValueError:
            return 0

    def update_register_value(self, register_name: str, new_value: Union[int, str]) -> None:
        """Update register with new value and highlight the change."""
        item = self._find_register_item(register_name)
        if not item:
            raise ValueError(f"Register {register_name} not found")
            
        if register_name == "$zero":
            return  # $zero register cannot be modified

        # Remove previous highlight if exists
        if self.last_highlighted_item:
            self.tree.item(self.last_highlighted_item, tags=())

        value = (int(new_value, 16) if isinstance(new_value, str) else new_value) & 0xFFFFFFFF
        hex_value = f"0x{value:08X}"
        self.tree.set(item, column="Value", value=hex_value)
        
        # Add highlight to changed register
        self.tree.item(item, tags=('highlight',))
        self.last_highlighted_item = item
        
        # Ensure the highlighted item is visible
        self.tree.see(item)

    def clear_registers(self) -> None:
        """Reset all registers to zero."""
        # Clear highlight first
        if self.last_highlighted_item:
            index = self.tree.index(self.last_highlighted_item)
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.item(self.last_highlighted_item, tags=(tag,))
            self.last_highlighted_item = None

        for item in self.tree.get_children():
            register_name = self.tree.item(item)['values'][0]
            if register_name != "$zero":  # Don't modify $zero
                self.tree.set(item, column="Value", value="0x00000000")

    def clear_highlight(self) -> None:
        """Clear the highlight from the last modified register."""
        if self.last_highlighted_item:
            index = self.tree.index(self.last_highlighted_item)
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.item(self.last_highlighted_item, tags=(tag,))
            self.last_highlighted_item = None

    def execute_arithmetic(self, dest: str, src1: str, src2: str, operation: str) -> None:
        """Execute arithmetic operations."""
        if operation not in self._operation_map:
            raise ValueError(f"Unknown operation: {operation}")
            
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = self._operation_map[operation](val1, val2)
        self.update_register_value(dest, result)

    def execute_logical(self, dest: str, src1: str, src2: str, operation):
      val1 = self.get_register_value(src1)
      val2 = self.get_register_value(src2)
      result = operation(val1, val2)
      self.update_register_value(dest, result)

    def execute_shift(self, dest: str, src1: str, shift_amount: int, operation):
        val1 = self.get_register_value(src1)
        result = operation(val1, shift_amount)
        self.update_register_value(dest, result)

    def execute_slt(self, dest: str, src1: str, src2: str):
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = 1 if val1 < val2 else 0
        self.update_register_value(dest, result)

    def execute_addi(self, dest: str, src1: str, immediate: int):
        val1 = self.get_register_value(src1)
        result = val1 + immediate
        self.update_register_value(dest, result)

    def execute_logical_immediate(self, dest: str, src1: str, immediate: int, operation: str) -> None:
        """Execute logical immediate operations (andi, ori)."""
        val1 = self.get_register_value(src1)
        result = self._operation_map[operation](val1, immediate)
        self.update_register_value(dest, result)

    def execute_bkm(self, dest: str, src1: str, src2: str):
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = self._operation_map["bkm"](val1, val2)
        self.update_register_value(dest, result)
