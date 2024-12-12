# parser.py
from typing import Dict, List

class Parser:
    def parse_data_section(self, lines: List[str]) -> Dict[str, int]:
        """Parse .data section more robustly."""
        data_section = {}
        
        try:
            # Find .data section if it exists
            data_start = next((i for i, line in enumerate(lines) if line.strip() == ".data"), None)
            
            if data_start is not None:
                # Try to find .text section or end of lines
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
                            try:
                                # Store as integer
                                var_value = int(value_part[1])
                                data_section[var_name] = var_value
                            except ValueError:
                                pass
        except Exception:
            # If no .data section found, return an empty dictionary
            pass
        
        return data_section

    def parse_text_section(self, lines: List[str]) -> List[dict]:
        """Parse .text section more robustly, handling inline comments and optional main label."""
        instructions = []
        address = 0x00400000  # Start address for instructions

        try:
            # Try to find main label, but don't fail if it's not there
            main_start = next((i for i, line in enumerate(lines) if line.strip() == "main:"), 0)
            
            for line in lines[main_start+1:]:
                line = line.strip()
                if not line or line.startswith(('.', ':')):
                    continue
                if '#' in line:
                    line = line.split('#')[0].strip()

                if line:
                    instructions.append({
                        "address": f"0x{address:08X}",
                        "source": line
                    })
                    address += 4
                
            return instructions
        except Exception:
            # If parsing fails, return an empty instruction list
            return []

    def map_labels(self, instructions: List[str]) -> Dict[str, int]:
        """Etiketlerin koddaki sırasını belirler."""
        labels = {}
        for index, instruction in enumerate(instructions):
            if ':' in instruction:  # Etiket var mı?
                label, _ = instruction.split(':', 1)
                labels[label.strip()] = index
        return labels