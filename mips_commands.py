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

    def get_register_value(self, register_name):
        """Return the value of the register by name."""
        item = self._find_register_item(register_name)
        if item:
            hex_value = self.tree.item(item, 'values')[2]  # Get the hex value
            try:
                # Handle negative numbers correctly
                if hex_value.startswith('-0x'):
                    return int(hex_value, 16)  # Negative hex value in two's complement format
                return int(hex_value, 16)  # Standard case for positive hex values
            except ValueError:
                return 0  # Default value for malformed hex formats
        return 0

    def update_register_value(self, register_name: str, new_value: Union[int, str]):
        """Update register value in the tree."""
        item = self._find_register_item(register_name)
        if item:
            if isinstance(new_value, int):
                hex_value = f"0x{new_value & 0xFFFFFFFF:08X}"  # Ensure 32-bit representation
            else:
                hex_value = f"0x{int(new_value, 16) & 0xFFFFFFFF:08X}"  # Convert string to hex and mask to 32-bit
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

    def execute_slt_command(self, dest: str, src1: str, src2: str):
        """Set Less Than komutunu uygular"""
        val1 = self.get_register_value(src1)
        val2 = self.get_register_value(src2)
        result = 1 if val1 < val2 else 0
        self.update_register_value(dest, result)

    def execute_beq_command(self, reg1: str, reg2: str, label: str):
        """Equal ise branch yapar"""
        val1 = self.get_register_value(reg1)
        val2 = self.get_register_value(reg2)
        
        if val1 == val2:
            return f"Branching to {label}"
        return None

    def execute_bne_command(self, reg1: str, reg2: str, label: str):
        """Not Equal ise branch yapar"""
        val1 = self.get_register_value(reg1)
        val2 = self.get_register_value(reg2)
        
        if val1 != val2:
            return f"Branching to {label}"
        return None

    def execute_j_command(self, label: str):
        """Unconditional Jump komutunu uygular"""
        return f"Jumping to {label}"

    def execute_jal_command(self, label: str):
        """Jump and Link komutunu uygular"""
        # $ra (return address) register'ını güncelle
        self.update_register_value("$ra", self.current_line + 1)
        return f"Jumping to {label} and storing return address"

    def execute_sw_command(self, src_reg: str, memory_address: str):
        """Store Word komutunu daha esnek şekilde uygular"""
        value = self.get_register_value(src_reg)
        
        try:
            # Parantezli formatı parse etme
            import re
            match = re.match(r'(-?\d+)\((\$\w+)\)', memory_address)
            if match:
                offset = int(match.group(1))
                base_reg = match.group(2)
                base_value = self.get_register_value(base_reg)
                
                # Basit bir bellek simülasyonu
                memory_loc = base_value + offset
                return f"Stored {value} at memory location {memory_loc}"
            else:
                return f"Invalid memory address format: {memory_address}"
        except Exception as e:
            return f"Error in store word: {str(e)}"
        
    def execute_addi_command(self, dest: str, src1: str, immediate: int):
        """Add immediate value to register."""
        val1 = self.get_register_value(src1)
        result = val1 + immediate
        self.update_register_value(dest, result)

    def execute_jr_command(self, register: str):
        """Jump to address stored in register."""
        # In a real simulator, this would set the program counter to the value in the register
        # However, in the current design, the program counter setting is handled in main.py
        return f"Jumping to address in {register}"