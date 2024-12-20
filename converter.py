# converter.py
class Converter:
    REGISTER_MAP = {
        "$zero": "00000", "$at": "00001", "$v0": "00010", "$v1": "00011",
        "$a0": "00100", "$a1": "00101", "$a2": "00110", "$a3": "00111",
        "$t0": "01000", "$t1": "01001", "$t2": "01010", "$t3": "01011",
        "$t4": "01100", "$t5": "01101", "$t6": "01110", "$t7": "01111",
        "$s0": "10000", "$s1": "10001", "$s2": "10010", "$s3": "10011",
        "$s4": "10100", "$s5": "10101", "$s6": "10110", "$s7": "10111",
        "$t8": "11000", "$t9": "11001", "$k0": "11010", "$k1": "11011",
        "$gp": "11100", "$sp": "11101", "$fp": "11110", "$ra": "11111"
    }
    OPCODE_MAP = {
        "add": "100000", "sub": "100010", "mul": "011000", "div": "011010",
        "and": "100100", "or": "100101", "sll": "000000", "srl": "000010",
        "addi": "001000", "lw": "100011", "sw": "101011", "beq": "000100", 
        "bne": "000101", "j": "000010", "jal": "000011", "slt": "101010", 
        "jr": "001000"
    }
    FUNCTION_MAP = {
        "add": "100000", "sub": "100010", "mul": "011000", "div": "011010",
        "and": "100100", "or": "100101", "sll": "000000", "srl": "000010",
        "slt": "101010", "jr": "001000"
    }

    def _convert_operand(self, operand, type):
      if type == "register":
        if operand in self.REGISTER_MAP:
          return self.REGISTER_MAP[operand]
      elif type == "immediate":
        try:
          imm_int = int(operand)
          if imm_int < 0:
            imm_int = imm_int & 0xFFFF  # Keep only the lower 16 bits
          return format(imm_int, '016b')
        except ValueError:
            return None
      elif type == "opcode":
        if operand in self.OPCODE_MAP:
          return self.OPCODE_MAP[operand]
      elif type == "function":
        if operand in self.FUNCTION_MAP:
            return self.FUNCTION_MAP[operand]

      return None
    
    def _handle_r_type(self, command, parts):
      rd, rs, rt = parts
      rd_bin = self._convert_operand(rd, "register")
      rs_bin = self._convert_operand(rs, "register")
      rt_bin = self._convert_operand(rt, "register")
      func_code = self._convert_operand(command, "function")

      if rd_bin and rs_bin and rt_bin and func_code:
        return f"000000{rs_bin}{rt_bin}{rd_bin}00000{func_code}"
      return None
    
    def _handle_i_type(self, command, parts):
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
            offset = "0"
            base = "$gp"

        rt_bin = self._convert_operand(rt, "register")
        offset_bin = self._convert_operand(offset, "immediate")
        base_bin = self._convert_operand(base, "register")

        if rt_bin and offset_bin and base_bin:
          opcode_bin = self._convert_operand(command, "opcode")
          return f"{opcode_bin}{base_bin}{rt_bin}{offset_bin}"
        return None

      elif command in ["beq", "bne"]:
          rs, rt, offset = parts
          rs_bin = self._convert_operand(rs, "register")
          rt_bin = self._convert_operand(rt, "register")
          offset_bin = self._convert_operand(offset, "immediate")
          opcode_bin = self._convert_operand(command, "opcode")
          
          if rs_bin and rt_bin and offset_bin and opcode_bin:
              return f"{opcode_bin}{rs_bin}{rt_bin}{offset_bin}"
          return None
          
      elif command in ["addi"]:
        rt, rs, immediate = parts
        rt_bin = self._convert_operand(rt, "register")
        rs_bin = self._convert_operand(rs, "register")
        immediate_bin = self._convert_operand(immediate, "immediate")
        opcode_bin = self._convert_operand(command, "opcode")

        if rt_bin and rs_bin and immediate_bin and opcode_bin:
          return f"{opcode_bin}{rs_bin}{rt_bin}{immediate_bin}"
        return None
      
      return None

    def _handle_j_type(self, command, parts):
      target = parts[0]
      opcode_bin = self._convert_operand(command, "opcode")
      try:
        target_int = int(target)
        target_bin = format(target_int, "026b")
        return f"{opcode_bin}{target_bin}"
      except ValueError:
          return None

    def convert_to_machine_code(self, instruction):
        parts = [part.strip() for part in instruction.replace(",", " ").split()]
        command = parts[0]
        
        if command in ["add", "sub", "and", "or", "sll", "srl", "slt"]:
            return self._handle_r_type(command, parts[1:])
        elif command in ["lw", "sw", "beq", "bne", "addi"]:
            return self._handle_i_type(command, parts[1:])
        elif command in ["j", "jal"]:
            return self._handle_j_type(command, parts[1:])
        elif command in ["jr"]:
          rs = parts[1]
          rs_bin = self._convert_operand(rs, "register")
          func_code = self._convert_operand(command, "function")
          if rs_bin and func_code:
              return f"000000{rs_bin}00000000000{func_code}"
          return None
        return f"Unsupported instruction: {command}"