# memory.py
from typing import Dict, List

class Memory:
    def __init__(self, base_address: int, size: int):
        self.base_address = base_address
        self.memory: List[int] = [0] * size
        self.data_section: Dict[str, int] = {}

    def read_word(self, address: int) -> int:
        if not self.is_valid_address(address):
            raise ValueError("Invalid memory address")
        offset = address - self.base_address
        return self.memory[offset // 4]

    def write_word(self, address: int, value: int):
        if not self.is_valid_address(address):
            raise ValueError("Invalid memory address")
        offset = address - self.base_address
        self.memory[offset // 4] = value

    def is_valid_address(self, address: int) -> bool:
        return self.base_address <= address < (self.base_address + len(self.memory) * 4)

    def allocate_data(self, data_section: Dict[str, int]):
        self.data_section = data_section

    def update_data_memory(self, var_name: str, value: int):
        try:
            variable_index = list(self.data_section.keys()).index(var_name)
            self.memory[variable_index] = value
        except ValueError:
            pass

    def get_data_memory_values(self) -> List[int]:
        return self.memory[:]