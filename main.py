# main.py
import tkinter as tk
from ui_elements import UIElements
from mips_commands import MIPSCommands
from parser import Parser
from memory import Memory
from executor import Executor
from converter import Converter

class MIPSIDE:
    DATA_SECTION_PROCESSED = "Data section processed. Ready to step through text segment."
    TEXT_SECTION_LOADED = "Loaded instructions. Ready to step through."
    NO_INSTRUCTIONS_TO_EXECUTE = "No more instructions to execute."
    NO_CODE_LOADED = "No code loaded."
    MIPS_CONVERTED = "MIPS code converted to machine code."

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MIPS IDE - Python")
        self.root.geometry("1200x1100")

        self.data_memory_base = 0x10010000
        self.memory = Memory(self.data_memory_base, 8)
        self.parser = Parser()
        self.ui = UIElements(root, self.data_memory_base, self._update_program_counter)
        self.commands = MIPSCommands(self.ui.get_register_tree())
        self.executor = None
        self.instructions = []
        self.labels = {}
        self.text_section_loaded = False
        self.converter = Converter()

        self.ui._run_button_action = self._run_button_action
        self.ui._step_button_action = self._step_button_action
        self.ui._convert_button_action = self._convert_button_action

    def _update_program_counter(self, pc):
        self.ui.update_program_counter_display(pc)
    
    def _load_sections(self):
      code = self.ui.get_mips_code()
      lines = [line.strip() for line in code.split('\n') if line.strip()]

      data_section = self.parser.parse_data_section(lines)
      self.memory.allocate_data(data_section)
      self.ui.log_to_console(f"Data Section: {data_section}")
      self.ui.update_data_memory_display(self.memory.get_data_memory_values())
      
      self.instructions = self.parser.parse_text_section(lines)
      self.labels = self.parser.map_labels([instr["source"] for instr in self.instructions])
      self.ui.set_instruction_memory(self.instructions)
      
      self.executor = Executor(
          self.commands,
          self.memory,
          self.labels,
          self._update_program_counter,
          self.ui.log_to_console
      )
      self.commands.update_register_value("$ra", len(self.instructions) * 4)
      self.ui.log_to_console(f"Set $ra to {len(self.instructions) * 4}")
      self.ui.log_to_console(self.TEXT_SECTION_LOADED)
      self.executor.set_instructions(self.instructions)
      self.text_section_loaded = True


    def _run_button_action(self):
        self.memory = Memory(self.data_memory_base, 8)  # Clear data memory
        self.commands.clear_registers() # Clear registers
        self._load_sections()
        self.executor = None # reset the executor
        self.ui.log_to_console(self.DATA_SECTION_PROCESSED)
        self.text_section_loaded = False # clear the flag

    def _step_button_action(self):
        if not self.text_section_loaded:
          self._load_sections()
        if self.executor and self.executor.current_line < len(self.instructions):
            instruction = self.instructions[self.executor.current_line]
            self.executor.execute_instruction(instruction)
            self.ui.update_data_memory_display(self.memory.get_data_memory_values())
        else:
            if self.executor:
               self.ui.log_to_console(self.NO_INSTRUCTIONS_TO_EXECUTE)
            else:
               self.ui.log_to_console(self.NO_CODE_LOADED)

    def _convert_button_action(self):
        code = self.ui.get_mips_code()
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        text_instructions = self.parser.parse_text_section(lines)
        machine_code_pairs = []

        for instruction in text_instructions:
            try:
                machine_code_instr = self.converter.convert_to_machine_code(instruction['source'])
                machine_code_pairs.append((instruction['source'], machine_code_instr))
            except Exception as e:
                machine_code_pairs.append((instruction['source'],f"Error: {str(e)}"))

        self.ui.set_machine_code_output(machine_code_pairs)
        self.ui.log_to_console(self.MIPS_CONVERTED)


if __name__ == "__main__":
    root = tk.Tk()
    MIPSIDE(root)
    root.mainloop()