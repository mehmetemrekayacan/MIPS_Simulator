# memory.py
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MemoryConfig:
    base_address: int
    size: int
    word_size: int = 4  # 4 bytes per word

class MemoryError(Exception):
    """Custom exception for memory-related errors."""
    pass

class MIPSMemory:
    def __init__(self, base_address: int, size: int):
        self.config = MemoryConfig(base_address, size)
        self.memory: List[int] = [0] * (size // self.config.word_size)
        self.data_section: Dict[str, int] = {}

    def _validate_address(self, address: int) -> None:
        """Validate memory address."""
        if address % self.config.word_size != 0:
            raise MemoryError(f"Unaligned memory access at address: 0x{address:08X}")

    def read_word(self, address: int) -> int:
        """Read a word from memory."""
        self._validate_address(address)  # Validate alignment first
        
        # Check if address is within data memory range
        if self.config.base_address <= address < self.config.base_address + (len(self.memory) * self.config.word_size):
            index = (address - self.config.base_address) // self.config.word_size
            return self.memory[index]
        elif 0 <= address < self.config.base_address:
            # Handle absolute memory access below data memory range
            index = address // self.config.word_size
            if 0 <= index < len(self.memory):
                return self.memory[index]
            else:
               raise MemoryError(f"Memory access out of bounds at address: 0x{address:08X}")
        else:
            raise MemoryError(f"Memory access out of bounds at address: 0x{address:08X}")
            
    def write_word(self, address: int, value: int):
         # Validate alignment first
        self._validate_address(address)  
        
        # Check if address is within data memory range
        if self.config.base_address <= address < self.config.base_address + (len(self.memory) * self.config.word_size):
            index = (address - self.config.base_address) // self.config.word_size
            self.memory[index] = value & 0xFFFFFFFF  # Ensure 32-bit value
        elif 0 <= address < self.config.base_address:
            # Handle absolute memory access below data memory range
            index = address // self.config.word_size
            if 0 <= index < len(self.memory):
                 self.memory[index] = value & 0xFFFFFFFF
            else:
                raise MemoryError(f"Memory access out of bounds at address: 0x{address:08X}")
        else:
              raise MemoryError(f"Memory access out of bounds at address: 0x{address:08X}")


    def is_valid_address(self, address: int) -> bool:
        """Check if address is a valid memory address."""
        if address % self.config.word_size != 0:
            return False
        
        # Check if address is within data memory range
        if self.config.base_address <= address < self.config.base_address + (len(self.memory) * self.config.word_size):
            return True
        
        # Check if address is in the absolute range below data memory range
        if 0 <= address < self.config.base_address:
            index = address // self.config.word_size
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