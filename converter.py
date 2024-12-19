# converter.py
class Converter:
    def __init__(self):
        self.register_map = {
            "$zero": "00000", "$at": "00001", "$v0": "00010", "$v1": "00011",
            "$a0": "00100", "$a1": "00101", "$a2": "00110", "$a3": "00111",
            "$t0": "01000", "$t1": "01001", "$t2": "01010", "$t3": "01011",
            "$t4": "01100", "$t5": "01101", "$t6": "01110", "$t7": "01111",
            "$s0": "10000", "$s1": "10001", "$s2": "10010", "$s3": "10011",
            "$s4": "10100", "$s5": "10101", "$s6": "10110", "$s7": "10111",
            "$t8": "11000", "$t9": "11001", "$k0": "11010", "$k1": "11011",
            "$gp": "11100", "$sp": "11101", "$fp": "11110", "$ra": "11111"
        }
        self.opcode_map = {
            "add": "100000", "sub": "100010", "mul": "011000", "div": "011010",
            "and": "100100", "or": "100101", "sll": "000000", "srl": "000010",
            "addi": "001000", "andi": "001100", "ori": "001101", "lw": "100011",
            "sw": "101011", "beq": "000100", "bne": "000101", "j": "000010",
            "jal": "000011", "slt": "101010", "jr": "001000"
        }
        self.function_map = {
            "add": "100000", "sub": "100010", "mul": "011000", "div": "011010",
            "and": "100100", "or": "100101", "sll": "000000", "srl": "000010",
            "slt": "101010", "jr": "001000"
        }
    
    def _get_register_binary(self, register):
        """Get binary representation of a register."""
        if register in self.register_map:
            return self.register_map[register]
        return None

    def _get_immediate_binary(self, immediate):
        """Convert immediate value to binary, handling negative values."""
        try:
            imm_int = int(immediate)
            if imm_int < 0:
              imm_int = imm_int & 0xFFFF  # Keep only the lower 16 bits
            return format(imm_int, '016b')
        except ValueError:
            return None

    def _get_opcode_binary(self, command):
        """Get binary representation of the opcode."""
        if command in self.opcode_map:
            return self.opcode_map[command]
        return None
    
    def _get_function_code(self, command):
        """Get binary representation of the function code."""
        if command in self.function_map:
          return self.function_map[command]
        return None

    def _handle_r_type(self, command, parts):
      """Handles R-type instructions."""
      rd, rs, rt = parts
      rd_bin = self._get_register_binary(rd)
      rs_bin = self._get_register_binary(rs)
      rt_bin = self._get_register_binary(rt)
      func_code = self._get_function_code(command)

      if rd_bin and rs_bin and rt_bin and func_code:
        return f"000000{rs_bin}{rt_bin}{rd_bin}00000{func_code}"
      return None
    
    def _handle_i_type(self, command, parts):
      """Handles I-type instructions."""
      if command in ["lw", "sw"]:
        rt, address = parts

        match = None
        offset = None
        base = None

        import re
        match = re.match(r'(-?\d+)\((\$\w+)\)', address)
        if match:
            offset = match.group(1)
            base = match.group(2)
        else:
            # Handle direct address (label)
            # Replace the label with a 0 offset to the $gp register
            offset = "0"
            base = "$gp"


        rt_bin = self._get_register_binary(rt)
        offset_bin = self._get_immediate_binary(offset)
        base_bin = self._get_register_binary(base)

        if rt_bin and offset_bin and base_bin:
          opcode_bin = self._get_opcode_binary(command)
          return f"{opcode_bin}{base_bin}{rt_bin}{offset_bin}"
        return None

      elif command in ["beq", "bne"]:
          rs, rt, offset = parts
          rs_bin = self._get_register_binary(rs)
          rt_bin = self._get_register_binary(rt)
          offset_bin = self._get_immediate_binary(offset)
          opcode_bin = self._get_opcode_binary(command)
          
          if rs_bin and rt_bin and offset_bin and opcode_bin:
              return f"{opcode_bin}{rs_bin}{rt_bin}{offset_bin}"
          return None
          
      elif command in ["addi", "andi", "ori"]:
        rt, rs, immediate = parts
        rt_bin = self._get_register_binary(rt)
        rs_bin = self._get_register_binary(rs)
        immediate_bin = self._get_immediate_binary(immediate)
        opcode_bin = self._get_opcode_binary(command)

        if rt_bin and rs_bin and immediate_bin and opcode_bin:
          return f"{opcode_bin}{rs_bin}{rt_bin}{immediate_bin}"
        return None
      
      return None

    def _handle_j_type(self, command, parts):
      """Handles J-type instructions."""
      target = parts[0]
      opcode_bin = self._get_opcode_binary(command)
      try:
        target_int = int(target)
        target_bin = format(target_int, "026b")
        return f"{opcode_bin}{target_bin}"
      except ValueError:
          return None

    def convert_to_machine_code(self, instruction):
        """Convert MIPS instruction to machine code."""
        parts = [part.strip() for part in instruction.replace(",", " ").split()]
        command = parts[0]
        
        if command in ["add", "sub", "mul", "div", "and", "or", "sll", "srl", "slt"]:
            return self._handle_r_type(command, parts[1:])
        elif command in ["lw", "sw", "beq", "bne", "addi", "andi", "ori"]:
            return self._handle_i_type(command, parts[1:])
        elif command in ["j", "jal"]:
            return self._handle_j_type(command, parts[1:])
        elif command in ["jr"]:
          rs = parts[1]
          rs_bin = self._get_register_binary(rs)
          func_code = self._get_function_code(command)
          if rs_bin and func_code:
              return f"000000{rs_bin}00000000000{func_code}"
          return None
        return f"Unsupported instruction: {command}"