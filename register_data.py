#register_data.py
from typing import List, Dict, TypedDict

class Register(TypedDict):
    name: str
    number: int
    value: str

class MIPSRegisters:
    # Register types
    ZERO_REG = "$zero"
    RETURN_ADDR_REG = "$ra"
    TEMP_REGS = ["$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$t8", "$t9"]
    SAVED_REGS = ["$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7"]
    
    @staticmethod
    def create_register(name: str, number: int) -> Register:
        return {
            "name": name,
            "number": number,
            "value": "0x00000000"
        }

    @classmethod
    def get_registers(cls) -> List[Register]:
        register_definitions = [
            ("$zero", 0), ("$at", 1),
            ("$v0", 2), ("$v1", 3),
            ("$a0", 4), ("$a1", 5), ("$a2", 6), ("$a3", 7),
            *[(f"$t{i}", i+8) for i in range(8)],
            *[(f"$s{i}", i+16) for i in range(8)],
            ("$t8", 24), ("$t9", 25),
            ("$k0", 26), ("$k1", 27),
            ("$gp", 28), ("$sp", 29), ("$fp", 30), ("$ra", 31)
        ]
        
        return [cls.create_register(name, number) for name, number in register_definitions]

register = MIPSRegisters.get_registers()