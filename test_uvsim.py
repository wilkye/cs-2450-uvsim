# test_uvsim.py

import pytest
from cpu import CPU
from control_instructions import ControlInstructions
from math_instructions import MathInstructions
from memory import Memory

class FakeRoot:
    def after(self, delay, func):
        pass
        
class FakeGUI:
    def __init__(self):
        self.root = FakeRoot()

    def log_message(self, msg):
        pass

    def load_mem(self):
        pass
        
@pytest.fixture
def setup_uvsim(monkeypatch):
    memory = Memory()
    gui = FakeGUI()
    cpu = CPU(memory, gui)
    control = ControlInstructions(memory, cpu, gui)
    math_inst = MathInstructions(memory)
    cpu.set_instructions(control, math_inst)
    return cpu, control, math_inst, memory

def test_memory_read_write(setup_uvsim):
    _, _, _, memory = setup_uvsim
    memory.set_value(10, 1234)
    assert memory.get_value(10) == "+1234"

def test_memory_reset(setup_uvsim):
    _, _, _, memory = setup_uvsim
    memory.set_value(0, 1111)
    memory.reset()
    assert all(val == 0 for val in memory.mem)

def test_add_instruction(setup_uvsim):
    cpu, _, math_inst, memory = setup_uvsim
    memory.set_value(5, 10)
    cpu.accumulator = 5
    cpu.accumulator = math_inst.ADD(cpu.accumulator, 5)
    assert cpu.accumulator == 15

def test_subtract_instruction(setup_uvsim):
    cpu, _, math_inst, memory = setup_uvsim
    memory.set_value(6, 3)
    cpu.accumulator = 10
    cpu.accumulator = math_inst.SUBTRACT(cpu.accumulator, 6)
    assert cpu.accumulator == 7

def test_multiply_instruction(setup_uvsim):
    cpu, _, math_inst, memory = setup_uvsim
    memory.set_value(7, 4)
    cpu.accumulator = 5
    cpu.accumulator = math_inst.MULTIPLY(cpu.accumulator, 7)
    assert cpu.accumulator == 20

def test_divide_instruction(setup_uvsim):
    cpu, _, math_inst, memory = setup_uvsim
    memory.set_value(8, 2)
    cpu.accumulator = 8
    cpu.accumulator = math_inst.DIVIDE(cpu.accumulator, 8)
    assert cpu.accumulator == 4

def test_load_instruction(setup_uvsim):
    cpu, control, _, memory = setup_uvsim
    memory.set_value(9, 55)
    control.LOAD(9)
    assert cpu.accumulator == "+55"

def test_store_instruction(setup_uvsim):
    cpu, control, _, memory = setup_uvsim
    cpu.accumulator = 77
    control.STORE(10)
    assert memory.get_value(10) == "+77"

def test_branch_instruction(setup_uvsim):
    cpu, control, _, memory = setup_uvsim
    memory.set_value(20, 1234)
    control.BRANCH(20)
    assert cpu.programCounter == 20

def test_branchneg_instruction(setup_uvsim):
    cpu, control, _, memory = setup_uvsim
    cpu.accumulator = -5
    memory.set_value(30, 9999)
    control.BRANCHNEG(30)
    assert cpu.programCounter == 30

def test_branchzero_instruction(setup_uvsim):
    cpu, control, _, memory = setup_uvsim
    cpu.accumulator = 0
    memory.set_value(40, 2222)
    control.BRANCHZERO(40)
    assert cpu.programCounter == 40

def test_halt_instruction(setup_uvsim):
    cpu, control, _, _ = setup_uvsim
    control.HALT()
    assert cpu.done is True

@pytest.fixture
def math_and_memory():
    memory = Memory()
    math_inst = MathInstructions(memory)
    return memory, math_inst

def test_add(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(0, 10)
    result = math_inst.ADD(5, 0)
    assert result == 15

def test_subtract(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(1, 4)
    result = math_inst.SUBTRACT(10, 1)
    assert result == 6

def test_multiply(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(2, 3)
    result = math_inst.MULTIPLY(7, 2)
    assert result == 21

def test_divide(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(3, 2)
    result = math_inst.DIVIDE(8, 3)
    assert result == 4

def test_divide_by_zero_raises(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(4, 0)
    with pytest.raises(ZeroDivisionError):
        math_inst.DIVIDE(10, 4)

def test_add_negative_number(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(5, -7)
    result = math_inst.ADD(10, 5)
    assert result == 3

def test_subtract_to_zero(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(6, 8)
    result = math_inst.SUBTRACT(8, 6)
    assert result == 0

def test_multiply_by_zero(math_and_memory):
    memory, math_inst = math_and_memory
    memory.set_value(7, 0)
    result = math_inst.MULTIPLY(1234, 7)
    assert result == 0

def test_six_digit_memory_write_and_read(setup_uvsim):
    _, _, _, memory = setup_uvsim
    six_digit_word = "020012"
    memory.set_value(0, six_digit_word)
    assert memory.get_value(0) == "+020012"

def test_six_digit_zero_padding(setup_uvsim):
    _, _, _, memory = setup_uvsim
    memory.set_value(1, '000005')
    assert memory.get_value(1) == "+000005"

def test_six_digit_max_address_allowed(setup_uvsim):
    _, _, _, memory = setup_uvsim
    memory.set_value(249, '123456')
    assert memory.get_value(249) == "+123456"

def test_six_digit_opcode_and_address_format(setup_uvsim):
    _, control, _, memory = setup_uvsim
    memory.set_value(20, '010234')
    assert memory.get_value(20) == "+010234"
    control.LOAD(20)
    assert control.cpu.accumulator is not None

def test_six_digit_negative_values(setup_uvsim):
    _, _, _, memory = setup_uvsim
    memory.set_value(5, '-000042')
    assert memory.get_value(5) == "-000042"

def test_memory_size_is_250(setup_uvsim):
    _, _, _, memory = setup_uvsim
    assert len(memory.mem) == 250