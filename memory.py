# memory.py
from typing import Dict, List

class Memory:
    def __init__(self, base_address: int, size: int):
        self.base_address = base_address
        self.memory: List[int] = [0] * size
        self.data_section: Dict[str, int] = {}

    def read_word(self, address: int) -> int:
        # Calculate relative address
        relative_address = address - self.base_address
        
        # Check if address is word-aligned
        if relative_address % 4 != 0:
            raise ValueError(f"Unaligned memory access at address: {address:08X}")
            
        # Convert to array index
        index = relative_address // 4
        
        # Check bounds
        if 0 <= index < len(self.memory):
            return self.memory[index]
        else:
            # For addresses below base_address, treat as regular memory access
            if 0 <= address < self.base_address:
                index = address // 4
                if 0 <= index < len(self.memory):
                    return self.memory[index]
            raise ValueError(f"Memory access out of bounds at address: {address:08X}")

    def write_word(self, address: int, value: int):
        # Calculate relative address
        relative_address = address - self.base_address
        
        # Check if address is word-aligned
        if relative_address % 4 != 0:
            raise ValueError(f"Unaligned memory access at address: {address:08X}")
            
        # Convert to array index
        index = relative_address // 4
        
        # Check bounds
        if 0 <= index < len(self.memory):
            self.memory[index] = value & 0xFFFFFFFF  # Ensure 32-bit value
        else:
            # For addresses below base_address, treat as regular memory access
            if 0 <= address < self.base_address:
                index = address // 4
                if 0 <= index < len(self.memory):
                    self.memory[index] = value & 0xFFFFFFFF
                    return
            raise ValueError(f"Memory access out of bounds at address: {address:08X}")

    def is_valid_address(self, address: int) -> bool:
        # Check if address is within valid ranges
        relative_address = address - self.base_address
        
        # Check if address is word-aligned
        if relative_address % 4 != 0:
            return False
            
        # Convert to array index
        index = relative_address // 4
        
        # Check primary range (relative to base address)
        if 0 <= index < len(self.memory):
            return True
            
        # Check secondary range (absolute addresses below base_address)
        if 0 <= address < self.base_address:
            index = address // 4
            return 0 <= index < len(self.memory)
            
        return False

    def allocate_data(self, data_section: Dict[str, int]):
        self.data_section = data_section
        # Initialize memory locations for data section
        for i, value in enumerate(data_section.values()):
            if i < len(self.memory):
                self.memory[i] = value

    def update_data_memory(self, var_name: str, value: int):
        if var_name in self.data_section:
            variable_index = list(self.data_section.keys()).index(var_name)
            if 0 <= variable_index < len(self.memory):
                self.memory[variable_index] = value
                self.data_section[var_name] = value

    def get_data_memory_values(self) -> List[int]:
        return self.memory[:]