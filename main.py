# main.py
import tkinter as tk
from ui_elements import UIElements
from mips_commands import MIPSCommands
from parser import Parser
from memory import Memory
from executor import Executor

class MIPSIDE:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MIPS IDE - Python")
        self.root.geometry("1200x900")

        self.data_memory_base = 0x10010000
        self.memory = Memory(self.data_memory_base, 8)
        self.parser = Parser()
        self.ui = UIElements(root, self.data_memory_base, self._update_program_counter)
        self.commands = MIPSCommands(self.ui.get_register_tree())
        self.executor = None
        self.instructions = []
        self.labels = {}
        self.text_section_loaded = False
        
        self.ui._run_button_action = self._run_button_action
        self.ui._step_button_action = self._step_button_action

    def _update_program_counter(self, pc):
        """Update the program counter and display."""
        self.ui.update_program_counter_display(pc)

    def _load_data_section(self):
        """Loads only data section."""
        code = self.ui.get_mips_code()
        lines = [line.strip() for line in code.split('\n') if line.strip()]

        data_section = self.parser.parse_data_section(lines)
        self.memory.allocate_data(data_section)
        self.ui.log_to_console(f"Data Section: {data_section}")
        self.ui.update_data_memory_display(self.memory.get_data_memory_values())

    def _load_text_section(self):
      """Loads and sets up text section."""
      code = self.ui.get_mips_code()
      lines = [line.strip() for line in code.split('\n') if line.strip()]

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
      self.ui.log_to_console("Loaded instructions. Ready to step through.")
      self.text_section_loaded = True

    def _run_button_action(self):
        """Run all instructions."""
        self._load_data_section()
        self.commands.clear_registers()
        self.executor = None # reset the executor
        self.ui.log_to_console("Data section processed. Ready to step through text segment.")
        self.text_section_loaded = False # clear the flag

    def _step_button_action(self):
        """Step through instructions in text segment."""
        if not self.text_section_loaded:
          self._load_text_section()
        if self.executor and self.executor.current_line < len(self.instructions):
            instruction = self.instructions[self.executor.current_line]
            self.executor.execute_instruction(instruction)
            self.ui.update_data_memory_display(self.memory.get_data_memory_values())
        else:
            if self.executor:
               self.ui.log_to_console("No more instructions to execute.")
            else:
               self.ui.log_to_console("No code loaded.")


if __name__ == "__main__":
    root = tk.Tk()
    MIPSIDE(root)
    root.mainloop()