# parser.py
from typing import Dict, List
import re

class MIPSParser:
    def parse_data_section(self, lines: List[str]) -> Dict[str, int]:
        data_section = {}
        try:
            data_start = next((i for i, line in enumerate(lines) if line.strip() == ".data"), None)
            if data_start is not None:
                try:
                    data_end = next(i for i, line in enumerate(lines[data_start+1:], start=data_start+1) 
                                    if line.strip() == ".text" or not line.strip())
                except StopIteration:
                    data_end = len(lines)

                for line in lines[data_start+1:data_end]:
                    line = line.strip()
                    if ":" in line and ".word" in line:
                        parts = line.split(":")
                        var_name = parts[0].strip()
                        value_part = parts[1].strip().split()

                        if len(value_part) > 1 and value_part[0] == ".word":
                            value_str = value_part[1]
                            try:
                                if value_str.lower().startswith("0x") or value_str.lower().startswith("-0x"):
                                    var_value = int(value_str, 16)
                                elif value_str.startswith("-"):
                                  var_value = int(value_str)
                                else:
                                  var_value = int(value_str)
                                data_section[var_name] = var_value
                            except ValueError:
                                pass
        except Exception:
            pass
        
        return data_section

    def parse_text_section(self, lines: List[str]) -> List[dict]:
        instructions = []
        address = 0x00400000
        
        text_start = next((i for i, line in enumerate(lines) if line.strip() == ".text"), None)

        if text_start is None:
            main_start = 0
        else:
            main_start = next((i for i, line in enumerate(lines[text_start+1:], start=text_start+1) if line.strip() == "main:"), text_start+1)
        
        for line in lines[main_start:]:
            line = line.strip()
            if not line or line.startswith(('.', ':')):
                continue
            if '#' in line:
                line = line.split('#')[0].strip()
                
            if line:
                parts = [part.strip() for part in line.replace(",", " ").split()]
                for i, part in enumerate(parts):
                    if part.lower().startswith("0x") or part.lower().startswith("-0x") or part.startswith("-") and not part[1:].isalpha():
                        try:
                            if part.lower().startswith("0x") or part.lower().startswith("-0x"):
                                parts[i] = int(part, 16)
                            else:
                                parts[i] = int(part)
                        except ValueError:
                            pass
                instructions.append({
                    "address": f"0x{address:08X}",
                    "source": " ".join(str(part) for part in parts)
                })
                address += 4
        return instructions

    def map_labels(self, instructions: List[str]) -> Dict[str, int]:
        labels = {}
        for index, instruction in enumerate(instructions):
            if ':' in instruction:
                label, _ = instruction.split(':', 1)
                labels[label.strip()] = index
        return labels