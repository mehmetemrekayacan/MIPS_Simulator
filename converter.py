# converter.py
from typing import Optional, Dict, Match
import re
from dataclasses import dataclass

@dataclass
class InstructionFormat:
    opcode: str
    rs: str = "00000"
    rt: str = "00000"
    rd: str = "00000"
    shamt: str = "00000"
    funct: str = "000000"
    immediate: str = "0000000000000000"
    address: str = "00000000000000000000000000"

class MIPSConverter:
    def __init__(self):
        self._load_instruction_maps()
        self._compile_regex_patterns()

    def _load_instruction_maps(self) -> None:
        """Load instruction mapping dictionaries."""
        self.REGISTER_MAP = {
            "$zero": "00000", "$at": "00001", "$v0": "00010", "$v1": "00011",
            "$a0": "00100", "$a1": "00101", "$a2": "00110", "$a3": "00111",
            "$t0": "01000", "$t1": "01001", "$t2": "01010", "$t3": "01011",
            "$t4": "01100", "$t5": "01101", "$t6": "01110", "$t7": "01111",
            "$s0": "10000", "$s1": "10001", "$s2": "10010", "$s3": "10011",
            "$s4": "10100", "$s5": "10101", "$s6": "10110", "$s7": "10111",
            "$t8": "11000", "$t9": "11001", "$k0": "11010", "$k1": "11011",
            "$gp": "11100", "$sp": "11101", "$fp": "11110", "$ra": "11111"
        }
        
        self.OPCODE_MAP = {
            "add": "000000", "sub": "000000", "mul": "011000", "div": "011010",
            "and": "100100", "or": "100101", "xor": "000000",
            "sll": "000000", "srl": "000010",
            "addi": "001000", "lw": "100011", "sw": "101011", "beq": "000100", 
            "bne": "000101", "j": "000010", "jal": "000011", "slt": "101010", 
            "jr": "001000"
        }
        
        self.FUNCTION_MAP = {
            "add": "100000", "sub": "100010", "mul": "011000", "div": "011010",
            "and": "100100", "or": "100101", "xor": "100110",
            "sll": "000000", "srl": "000010",
            "slt": "101010", "jr": "001000"
        }

    def _compile_regex_patterns(self) -> None:
        """Compile regex patterns used in parsing."""
        self.MEMORY_ACCESS_PATTERN = re.compile(r'(-?\d+)\((\$\w+)\)')

    def convert_to_machine_code(self, instruction: str) -> str:
        """Convert MIPS instruction to machine code."""
        try:
            parts = [part.strip() for part in instruction.replace(",", " ").split()]
            command = parts[0]
            
            if command.endswith(":"):  # Skip labels
                return None
                
            handlers = {
                'r': self._handle_r_type,
                'i': self._handle_i_type,
                'j': self._handle_j_type
            }
            
            instruction_type = self._get_instruction_type(command)
            handler = handlers.get(instruction_type)
            
            if handler:
                return handler(command, parts[1:])
            
            raise ValueError(f"Unsupported instruction: {command}")
            
        except Exception as e:
            return f"Error: {str(e)}"

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

    def _get_instruction_type(self, command: str) -> str:
        """Determine instruction type (r, i, or j)."""
        r_type = {'add', 'sub', 'and', 'or', 'xor', 'sll', 'srl', 'slt'}
        i_type = {'addi', 'lw', 'sw', 'beq', 'bne', 'li'}
        j_type = {'j', 'jal', 'jr'}

        if command in r_type:
            return 'r'
        elif command in i_type:
            return 'i'
        elif command in j_type:
            return 'j'
        else:
            raise ValueError(f"Unknown instruction type for command: {command}")