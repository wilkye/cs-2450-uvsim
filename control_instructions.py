# control_instructions.py

class ControlInstructions:
    def __init__(self, memory, cpu, gui):
        self.memory = memory
        self.cpu = cpu
        self.gui = gui

        self.temp_address = None

    # READ instruction
    def READ(self, address):
        if self.temp_address is not None:
            # Use the GUI-provided, validated, padded input
            value = int(self.input_buffer)

            # Store into memory
            self.memory.set_value(address, value)

            # Clear temp state
            self.temp_address = None

    # WRITE instruction
    def WRITE(self, address):
        value = self.memory.get_value(address)
        self.gui.log_message(f"WRITE Output: {value}")

    # LOAD instruction
    def LOAD(self, address):
        self.cpu.accumulator = self.memory.mem[address]
        self.gui.log_message(f"Accumulator set to {self.cpu.accumulator}")

    # STORE instruction
    def STORE(self, address):
        self.memory.set_value(address, self.cpu.accumulator)
        self.gui.log_message("\n\n\nNewly")
        self.gui.log_message(str(self.memory))

    # BRANCH instruction
    def BRANCH(self, address):
        self.cpu.programCounter = (int(address))
        self.cpu.instructionReg = self.memory.mem[int(address)]

    # BRANCHNEG instruction
    def BRANCHNEG(self, address):
        if int(self.cpu.accumulator) < 0:
            self.cpu.programCounter = (int(address))
            self.cpu.instructionReg = self.memory.mem[address]
        else:
            self.gui.log_message("Not negative to branch")

    # BRANCHZERO instruction
    def BRANCHZERO(self, address):
        if self.cpu.accumulator == 0:
            self.cpu.programCounter = (int(address))
            self.cpu.instructionReg = self.memory.mem[address]
        else:
            self.gui.log_message("Not zero to branch")

    # HALT instruction
    def HALT(self):
        self.cpu.done = True
        self.gui.log_message("HALT")

    OPCODE_DICT = {
        "10": 'READ',
        "11": 'WRITE',
        "20": 'LOAD',
        "21": 'STORE',
        "40": 'BRANCH',
        "41": 'BRANCHNEG',
        "42": 'BRANCHZERO',
        "43": 'HALT'
    }

    def execute(self, opcode, memoryLoc):
        operation = self.OPCODE_DICT.get(str(opcode))

        if not operation:
            raise ValueError(f"Unknown control operation: {opcode}")

        if operation == "READ":
            self.temp_address = memoryLoc
            self.gui.log_message("Submit a 4-digit number...")
            self.cpu.done = True
        elif operation == "WRITE":
            self.WRITE(memoryLoc)
        elif operation == "LOAD":
            self.LOAD(memoryLoc)
        elif operation == "STORE":
            self.STORE(memoryLoc)
        elif operation == "BRANCH":
            self.BRANCH(memoryLoc)
        elif operation == "BRANCHNEG":
            self.BRANCHNEG(memoryLoc)
        elif operation == "BRANCHZERO":
            self.BRANCHZERO(memoryLoc)
        elif operation == "HALT":
            self.HALT()
