# memory.py
from typing import Dict, List

class Memory:
    def __init__(self, base_address: int, size: int):
        self.base_address = base_address
        self.memory: List[int] = [0] * size
        self.data_section: Dict[str, int] = {}

    def read_word(self, address: int) -> int:
        """Reads a word from memory."""
        if not self.is_valid_address(address):
            raise ValueError("Invalid memory address")
        offset = address - self.base_address
        return self.memory[offset // 4]

    def write_word(self, address: int, value: int):
        """Writes a word to memory."""
        if not self.is_valid_address(address):
            raise ValueError("Invalid memory address")
        offset = address - self.base_address
        self.memory[offset // 4] = value

    def is_valid_address(self, address: int) -> bool:
      """Check if the address is within the memory bounds."""
      return self.base_address <= address < (self.base_address + len(self.memory) * 4)

    def allocate_data(self, data_section: Dict[str, int]):
        """Allocates space in memory for data variables."""
        self.data_section = data_section
        
        # Do not initialize the memory with data section values here

    def update_data_memory(self, var_name: str, value: int):
        """Updates the data memory with the given value."""
        # Find the index of the variable in data_section
        try:
            variable_index = list(self.data_section.keys()).index(var_name)
            self.memory[variable_index] = value
        except ValueError:
            pass

    def get_data_memory_values(self) -> List[int]:
      """Get the current values in the data memory."""
      return self.memory[:]