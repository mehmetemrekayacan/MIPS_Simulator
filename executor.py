# executor.py
from typing import List, Dict, Optional, Callable
from mips_commands import MIPSProcessor
from memory import MIPSMemory
import re

class MIPSExecutor:
    def __init__(self, commands: MIPSProcessor, memory: MIPSMemory, labels: Dict[str, int], pc_update_callback: Callable[[int], None], ui_log_callback: Callable[[str], None]):
        self.commands = commands
        self.memory = memory
        self.labels = labels
        self.program_counter = 0
        self.current_line = 0
        self.pc_update_callback = pc_update_callback
        self.ui_log_callback = ui_log_callback
        self.instructions = []

    def set_instructions(self, instructions: List[dict]):
        self.instructions = instructions

    def execute_instruction(self, instruction: dict):
        # Clear previous register highlight
        self.commands.clear_highlight()

        while True:
            line = instruction["source"]
            address = instruction["address"]
            parts = [part.strip() for part in line.replace(",", " ").split()]
            command = parts[0]
            
            if command.endswith(":"):
                self._increment_pc_and_line()
                if self.current_line < len(self.instructions):
                    instruction = self.instructions[self.current_line]
                    continue
                else:
                    self.ui_log_callback("\n=== Program execution completed ===")
                    return
            break
        
        self.pc_update_callback(self.program_counter)
        self.ui_log_callback(f"Executing at {address}: {line}")

        handler = self._get_instruction_handler(command)
        if handler:
            result = handler(command, parts[1:])
            if result:
                self.ui_log_callback(result)
            else:
                self.ui_log_callback(f"Executed: {line}")
        else:
            self.ui_log_callback(f"Unsupported instruction: {command}")
        
        self._increment_pc_and_line()
        
        # Check if this was the last instruction
        if self.current_line >= len(self.instructions):
            self.ui_log_callback("\n=== Program execution completed ===")
    
    def _increment_pc_and_line(self):
        self.program_counter += 4
        self.pc_update_callback(self.program_counter)
        self.current_line += 1
        
    def _get_instruction_handler(self, command):
        instruction_map = {
            # R-Format
            "add": self._handle_r_type_arithmetic,
            "sub": self._handle_r_type_arithmetic,
            "and": self._handle_r_type_logical,
            "or": self._handle_r_type_logical,
            "xor": self._handle_r_type_logical,
            "sll": self._handle_shift,
            "srl": self._handle_shift,
            "slt": self._handle_slt,
            # I-Format
            "lw": self._handle_lw,
            "sw": self._handle_sw,
            "addi": self._handle_addi,
            "beq": self._handle_branch,
            "bne": self._handle_branch,
            "li": self._handle_li,
            "andi": self._handle_logical_immediate,
            "ori": self._handle_logical_immediate,
            # J-Format
            "j": self._handle_jump,
            "jal": self._handle_jump,
            "jr": self._handle_jr,
            # System
            "syscall": self._handle_syscall,
        }
        return instruction_map.get(command)
    
    def _handle_r_type_arithmetic(self, command, parts):
        dest, src1, src2 = parts
        self.commands.execute_arithmetic(dest, src1, src2, command)

    def _handle_r_type_logical(self, command, parts):
        dest, src1, src2 = parts
        operation_map = {
            "and": lambda x, y: x & y,
            "or": lambda x, y: x | y,
            "xor": lambda x, y: x ^ y
        }
        operation = operation_map.get(command)
        if operation:
            self.commands.execute_logical(dest, src1, src2, operation)
        else:
            self.ui_log_callback(f"Error: Invalid R-type logical operation: {command}")
    
    def _handle_shift(self, command, parts):
      dest, src1, shift_amount = parts
      
      if isinstance(shift_amount, str) and shift_amount.startswith("$"):
          shift_value = self.commands.get_register_value(shift_amount)
      else:
          try:
              shift_value = int(shift_amount)
          except ValueError:
              self.ui_log_callback(f"Error: Invalid shift amount: {shift_amount}")
              return None
      
      operation_map = {
          "sll": lambda x, y: x << y,
          "srl": lambda x, y: x >> y
      }

      operation = operation_map.get(command)
      if operation:
        self.commands.execute_shift(dest, src1, shift_value, operation)
      else:
        self.ui_log_callback(f"Error: Invalid shift operation: {command}")

    def _handle_lw(self, _, parts):
        register, memory_address = parts
        
        try:
            match = re.match(r'(-?\d+)\((\$\w+)\)', memory_address)
            if match:
                offset = int(match.group(1))
                base_reg = match.group(2)
                base_value = self.commands.get_register_value(base_reg)
                memory_loc = base_value + offset
                
                try:
                    value = self.memory.read_word(memory_loc)
                    self.commands.update_register_value(register, value)
                    return f"Loaded {value} from memory location {memory_loc} into {register}"
                except ValueError as e:
                    return f"Error reading from memory: {str(e)}"
            elif memory_address in self.memory.data_section:
                value = self.memory.data_section[memory_address]
                self.commands.update_register_value(register, value)
                self.memory.update_data_memory(memory_address, value)
                return f"Loaded {value} from {memory_address} into {register}"
            else:
              return f"Invalid memory address: {memory_address}"
        except ValueError as e:
            return f"Error in load word: {str(e)}"

    def _handle_sw(self, _, parts):
        src_reg, memory_address = parts
        try:
            match = re.match(r'(-?\d+)\((\$\w+)\)', memory_address)
            if match:
                offset = int(match.group(1))
                base_reg = match.group(2)
                base_value = self.commands.get_register_value(base_reg)
                memory_loc = base_value + offset
                value = self.commands.get_register_value(src_reg)
                
                try:
                    self.memory.write_word(memory_loc, value)
                    return f"Stored {value} at memory location {memory_loc}"
                except ValueError as e:
                    return f"Error writing to memory: {str(e)}"
            elif memory_address in self.memory.data_section:
                value = self.commands.get_register_value(src_reg)
                self.memory.update_data_memory(memory_address, value)
                self.memory.data_section[memory_address] = value
                return f"Stored {value} in {memory_address}"
            else:
                return f"Invalid memory address format: {memory_address}"
        except ValueError as e:
            return f"Error in store word: {str(e)}"

    def _handle_slt(self, _, parts):
        dest, src1, src2 = parts
        self.commands.execute_slt(dest, src1, src2)

    def _handle_branch(self, command, parts):
        reg1, reg2, label = parts
        val1 = self.commands.get_register_value(reg1)
        val2 = self.commands.get_register_value(reg2)
        
        if command == "beq" and val1 == val2:
            self._jump_to_label(label, f"Branching to {label} (PC={self.program_counter})")
        elif command == "bne" and val1 != val2:
            self._jump_to_label(label, f"Branching to {label} (PC={self.program_counter})")
    
    def _handle_jump(self, command, parts):
        label = parts[0]
        if command == "j":
           self._jump_to_label(label, f"Jumping to {label} (PC={self.program_counter})")
        elif command == "jal":
            next_instruction = self.program_counter + 4
            self.commands.update_register_value("$ra", next_instruction)
            self._jump_to_label(label, f"Jumping to {label} and storing return address (PC={self.program_counter})")

    def _jump_to_label(self, label, log_message):
      self.program_counter = self.labels[label] * 4
      self.current_line = self.labels[label]
      self.pc_update_callback(self.program_counter)
      self.ui_log_callback(log_message)

    def _handle_addi(self, _, parts):
        dest, src1, immediate = parts
        self.commands.execute_addi(dest, src1, int(immediate))
    
    def _handle_jr(self, _, parts):
        register = parts[0]
        return_address = self.commands.get_register_value(register)
        
        # Set PC to return address
        self.program_counter = return_address - 4  # Subtract 4 because PC will be incremented after this
        self.current_line = (return_address - 4) // 4
        self.pc_update_callback(self.program_counter)
        
        self.ui_log_callback(f"Returning to address {return_address:08X}")

    def _handle_li(self, _, parts):
        dest, immediate = parts
        try:
            value = int(immediate)
            self.commands.update_register_value(dest, value)
            return f"Loaded {value} into {dest}"
        except ValueError:
            return f"Error: Invalid immediate value {immediate}"

    def _handle_syscall(self, _, parts):
        service = self.commands.get_register_value("$v0")
        if service == 10:  # Exit program
            return "Program exit requested"
        return f"Syscall service {service} executed"

    def _handle_logical_immediate(self, command, parts):
        dest, src1, immediate = parts
        try:
            imm_value = int(immediate)
            self.commands.execute_logical_immediate(dest, src1, imm_value, command)
            return f"Executed {command} {dest}, {src1}, {immediate}"
        except ValueError:
            return f"Error: Invalid immediate value {immediate}"