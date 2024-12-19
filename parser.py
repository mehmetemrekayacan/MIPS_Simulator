# parser.py
from typing import Dict, List
import re

class Parser:
    def parse_data_section(self, lines: List[str]) -> Dict[str, int]:
        """Parse .data section more robustly, handling hex and decimal."""
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
                                # Handle hexadecimal numbers (e.g., 0xFFFF0000 or -0x10000)
                                if value_str.lower().startswith("0x") or value_str.lower().startswith("-0x"):
                                    var_value = int(value_str, 16)
                                # Handle negative decimal numbers
                                elif value_str.startswith("-"):
                                  var_value = int(value_str)
                                # Handle regular decimal numbers
                                else:
                                  var_value = int(value_str)
                                data_section[var_name] = var_value
                            except ValueError:
                                pass  # Ignore invalid entries
        except Exception:
            pass  # Return empty dict if no data section
        
        return data_section

    def parse_text_section(self, lines: List[str]) -> List[dict]:
        """Parse .text section more robustly, handling inline comments and optional main label."""
        instructions = []
        address = 0x00400000  # Start address for instructions

        try:
            main_start = next((i for i, line in enumerate(lines) if line.strip() == "main:"), 0)
            
            for line in lines[main_start+1:]:
                line = line.strip()
                if not line or line.startswith(('.', ':')):
                    continue
                if '#' in line:
                    line = line.split('#')[0].strip()

                if line:
                    parts = [part.strip() for part in line.replace(",", " ").split()]
                    
                    # Handle immediate values for instructions like 'li'
                    for i, part in enumerate(parts):
                        if part.lower().startswith("0x") or part.lower().startswith("-0x") or part.startswith("-") and not part[1:].isalpha(): #Negative hex check
                            try:
                                if part.lower().startswith("0x") or part.lower().startswith("-0x"):
                                    parts[i] = int(part, 16)
                                else:
                                    parts[i] = int(part)
                            except ValueError:
                                pass  # If conversion fails ignore it
                    
                    instructions.append({
                        "address": f"0x{address:08X}",
                        "source": " ".join(str(part) for part in parts)  # Rejoin parts after processing
                    })
                    address += 4
                
            return instructions
        except Exception:
            return []

    def map_labels(self, instructions: List[str]) -> Dict[str, int]:
        """Determines the line number for each label in the code."""
        labels = {}
        for index, instruction in enumerate(instructions):
            if ':' in instruction:
                label, _ = instruction.split(':', 1)
                labels[label.strip()] = index
        return labels