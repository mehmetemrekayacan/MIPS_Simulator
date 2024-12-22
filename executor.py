# executor.py
from typing import List, Dict, Optional
from mips_commands import MIPSCommands
from memory import Memory
import re

class Executor:
    def __init__(self, commands: MIPSCommands, memory: Memory, labels: Dict[str, int], pc_update_callback, ui_log_callback):
        self.commands = commands
        self.memory = memory
        self.labels = labels
        self.program_counter = 0
        self.current_line = 0
        self.pc_update_callback = pc_update_callback
        self.ui_log_callback = ui_log_callback
        self.instructions = []

    def set_instructions(self, instructions:List[dict]):
        self.instructions = instructions

    def execute_instruction(self, instruction: dict):
        line = instruction["source"]
        address = instruction["address"]
        parts = [part.strip() for part in line.replace(",", " ").split()]
        command = parts[0]
        
        self.pc_update_callback(self.program_counter) # changed to current program counter
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

        self.program_counter += 4  # Now it increment after the instruction is executed.
        self.pc_update_callback(self.program_counter)
        self.current_line += 1
    
    def _get_instruction_handler(self, command):
      instruction_map = {
        # R-Format
        "add": self._handle_arithmetic,
        "sub": self._handle_arithmetic,
        "and": self._handle_logical,
        "or": self._handle_logical,
        "sll": self._handle_shift,
        "srl": self._handle_shift,
        "slt": self._handle_slt,
        # I-Format
        "lw": self._handle_lw,
        "sw": self._handle_sw,
        "addi": self._handle_immediate_arithmetic,
        "beq": self._handle_branch,
        "bne": self._handle_branch,
        # J-Format
        "j": self._handle_jump,
        "jal": self._handle_jump,
        "jr": self._handle_jr,
      }
      return instruction_map.get(command)
    
    def _handle_arithmetic(self, command, parts):
        dest, src1, src2 = parts
        method_map = {
            "add": self.commands.execute_add_command,
            "sub": self.commands.execute_sub_command,
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

    def _handle_shift(self, command, parts):
      dest, src1, shift_amount = parts
      method_map = {
          "sll": self.commands.execute_sll_command,
          "srl": self.commands.execute_srl_command
      }
      method = method_map[command]

      if isinstance(shift_amount, str) and shift_amount.startswith("$"):
          shift_value = self.commands.get_register_value(shift_amount)
      else:
          try:
              shift_value = int(shift_amount)
          except ValueError:
              self.ui_log_callback(f"Error: Invalid shift amount: {shift_amount}")
              return None
      method(dest, src1, shift_value)

    def _handle_lw(self, _, parts):
      register, memory_address = parts
      if memory_address in self.memory.data_section:
        value = self.memory.data_section[memory_address]
        self.commands.update_register_value(register, value)
        self.memory.update_data_memory(memory_address, value)
        return f"Loaded {value} from {memory_address} into {register}"
      else:
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

            else:
              return f"Invalid memory address: {memory_address}"
        except ValueError as e:
          return f"Error in load word: {str(e)}"

    def _handle_sw(self, _, parts):
        if len(parts) == 2:
            src_reg, memory_address = parts
            if memory_address in self.memory.data_section:
                value = self.commands.get_register_value(src_reg)
                self.memory.update_data_memory(memory_address, value)
                self.memory.data_section[memory_address] = value
                return f"Stored {value} in {memory_address}"
            else:
              try:
                  match = re.match(r'(-?\d+)\((\$\w+)\)', memory_address)
                  if match:
                    offset = int(match.group(1))
                    base_reg = match.group(2)
                    base_value = self.commands.get_register_value(base_reg)
                    memory_loc = base_value + offset
                    value = self.commands.get_register_value(src_reg)

                    try:
                        self.memory.write_word(memory_loc,value)
                        return f"Stored {value} at memory location {memory_loc}"
                    except ValueError as e:
                        return f"Error writing to memory: {str(e)}"
                  else:
                      return f"Invalid memory address format: {memory_address}"
              except ValueError as e:
                 return f"Error in store word: {str(e)}"
        else:
            return f"Invalid sw instruction: {parts}"

    def _handle_slt(self, _, parts):
        dest, src1, src2 = parts
        self.commands.execute_slt_command(dest, src1, src2)

    def _handle_branch(self, command, parts):
        reg1, reg2, label = parts
        val1 = self.commands.get_register_value(reg1)
        val2 = self.commands.get_register_value(reg2)
        
        if command == "beq" and val1 == val2:
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self.pc_update_callback(self.program_counter)
            return f"Branching to {label} (PC={self.program_counter})"
        elif command == "bne" and val1 != val2:
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self.pc_update_callback(self.program_counter)
            return f"Branching to {label} (PC={self.program_counter})"

    def _handle_jump(self, command, parts):
        label = parts[0]
        if command == "j":
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self.pc_update_callback(self.program_counter)
            return f"Jumping to {label} (PC={self.program_counter})"
        elif command == "jal":
            self.commands.update_register_value("$ra", self.program_counter + 4) # güncellendi + 4 eklendi
            self.program_counter = self.labels[label] * 4
            self.current_line = self.labels[label]
            self.pc_update_callback(self.program_counter)
            return f"Jumping to {label} and storing return address (PC={self.program_counter})"

    def _handle_immediate_arithmetic(self, command, parts):
        dest, src1, immediate = parts
        self.commands.execute_addi_command(dest, src1, int(immediate))

    def _handle_jr(self, _, parts):
      register = parts[0]
      return_address = self.commands.get_register_value(register)
      
      self.ui_log_callback(f"Jr instruction: Register {register}, Value: {return_address}")
        
      if return_address == 0 or return_address >= len(self.instructions) * 4:
          self.ui_log_callback("Program execution completed.")
          self.current_line = len(self.instructions)
          self.program_counter = len(self.instructions) * 4
          self.pc_update_callback(self.program_counter)
          return "Program end: Jumped to invalid/termination address"
      
      target_line = return_address // 4
      
      #  Important :  We don't want to advance the pc on a jump instruction
      self.program_counter = return_address 
      self.current_line = target_line
      self.pc_update_callback(self.program_counter)
      
      self.ui_log_callback(f"Jumping to line {target_line} (PC={self.program_counter})")
      return f"Jumping to line {target_line} (PC={self.program_counter})".data