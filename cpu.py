#cpu.py
from time import sleep

class CPU:
    def __init__(self, memory, gui):
        self.controlInstruct = None
        self.mathInstruct = None
        self.memory = memory
        self.gui = gui
        self.accumulator = 0
        self.programCounter = 0
        self.instructionReg = 0
        self.done = False

    def reset(self):
        self.accumulator = 0
        self.programCounter = 0
        self.instructionReg = 0
        self.done = False

    def set_instructions(self, conInstruct, mathInstruct):
        self.controlInstruct = conInstruct
        self.mathInstruct = mathInstruct

    def fetch(self):
        instruction = self.memory.mem[self.programCounter]
        self.programCounter += 1
        return instruction
    
    def decode_execute(self, instruction):
        instruction = instruction.lstrip("+-")
        print(instruction)
        if len(instruction) == 4:
            opcode = int(instruction) // 100
            memoryLoc = int(instruction) % 100
        elif len(instruction) == 6:
            opcode = int(instruction) // 1000
            memoryLoc = int(instruction) % 1000

        if opcode in [30, 31, 32, 33]:
            self.accumulator = self.mathInstruct.execute(opcode, self.accumulator, memoryLoc)
        elif opcode in [10, 11, 20, 21, 40, 41, 42, 43]:
            self.controlInstruct.execute(opcode, memoryLoc)
        else:
            self.gui.log_message(f"Skipping 'word' - CPU")

    def run(self):
        if self.done:
            return

        self.gui.load_mem()
        instruction = self.fetch()
        self.decode_execute(instruction)
        if self.programCounter > 99:
            self.controlInstruct.HALT()
            return

        self.gui.root.after(500, self.run)
