# MIPS Simulator IDE 🖥️📝

## Overview

This is a comprehensive MIPS Assembly Language Simulator built with Python and Tkinter, providing an interactive development environment for MIPS assembly programming. The simulator allows users to write, load, and execute MIPS assembly code with step-by-step execution and real-time register and memory tracking.

## 🌟 Features

### Code Editor
- Line numbering
- Syntax highlighting (basic)
- Undo/Redo functionality
- Scrollable text area

### Execution Environment
- Step-by-step code execution
- Real-time program counter tracking
- Comprehensive instruction support

### Register and Memory Management
- Interactive register view
- Data memory tracking
- Memory address visualization

### Supported Instructions
- Arithmetic: `add`, `sub`, `mul`, `div`, `addi`
- Logical: `and`, `or`, `andi`, `ori`
- Shift: `sll`, `srl`
- Memory: `lw`, `sw`
- Comparison: `slt`
- Control Flow: `beq`, `bne`, `j`, `jal`, `jr`

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Tkinter (usually comes pre-installed with Python)

### Clone the Repository
```bash
git clone https://github.com/yourusername/mips-simulator.git
cd mips-simulator
```

### Dependencies
No external dependencies required beyond standard Python libraries.

## 📋 Usage

### Running the Simulator
```bash
python MIPSIDE.py
```

### Writing MIPS Code
1. Use the text editor to write your MIPS assembly code
2. Include `.data` and `.text` sections
3. Define labels for branching and jumping

### Example Code
```assembly
.data
    result: .word 0

.text
main:
    addi $t0, $zero, 5     # Load 5 into $t0
    addi $t1, $zero, 3     # Load 3 into $t1
    add $t2, $t0, $t1      # Add $t0 and $t1, store in $t2
    sw $t2, result         # Store result in memory
```

## 🕹️ User Interface

### Left Panel: Code Editor
- Write and edit MIPS assembly code
- Line numbers for easy reference

### Right Panel: Registers
- Shows register names, numbers, and current values
- Real-time updates during execution

### Bottom Left: Console
- Execution logs
- Program counter tracking
- Step-by-step execution messages

### Bottom Center: Instruction Memory
- Displays loaded instructions with addresses
- Shows current execution state

### Bottom Right: Data Memory
- Visualizes data segment memory
- Tracks memory address and values

## 🛠️ Control Buttons

- **Clear**: Reset all registers to zero
- **Run**: Load and prepare code for execution
- **Step**: Execute one instruction at a time

## 🚧 Limitations
- Basic memory simulation
- No floating-point instruction support
- Limited pseudo-instruction handling

## 📄 License
[Choose an appropriate license, e.g., MIT License]

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact
Your Name - emremehmet32@hotmail.com | emremehmet2032@gmail.com

Project Link: [https://github.com/mehmetemrekayacan/mips-simulator](https://github.com/yourusername/mips-simulator)
