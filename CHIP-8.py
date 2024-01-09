# Based on Jason/ loktar00's CHIP-8 Javascript code- https://github.com/loktar00/chip8/blob/master/chip8.js 
# Along with Tobias V. Langhoff's "Guide to making a CHIP-8 emulator" - https://tobiasvl.github.io/blog/write-a-chip-8-emulator/ 
#
# screen, pixelsize, width, and height still need to be defined (along with graphics engine that is)

import numpy as np
import keyboard

class Processor:
    def __init__(self, name):
        # Initialization code here
        self.width = 64  # Define appropriate values for width and height
        self.height = 32
        self.memory = np.zeros((1, 4096))
        self.register = np.zeros((1, 16))
        self.stack = np.zeros((1, 16))
        self.i = None
        self.display = np.zeros((64, 32))
        self.displayFlag = False
        self.step = 0

        # program counter, should get incremented by 2 after reading an opcode
        self.pc = 0x200
        # stack pointer;
        self.sp = None

        self.opcode = None
        self.keys = []
        self.keyMap = {
            # Key mapping here
              49: 0x1,  # 1
              50: 0x2,  # 2
              51: 0x3,  # 3
              52: 0x4,  # 4
              81: 0x5,  # Q
              87: 0x6,  # W
              69: 0x7,  # E
              82: 0x8,  # R
              65: 0x9,  # A
              83: 0xA,  # S
              68: 0xB,  # D
              70: 0xC,  # F
              90: 0xD,  # Z
              88: 0xE,  # X
              67: 0xF,  # C
              86: 0x10  # V
        }

        self.currentKey = False
        self.delayTimer = 0
        self.soundTimer = 0

        # Load fontSet
        self.fontSet = np.array([
            # FontSet values here
           0xF0, 0x90, 0x90, 0x90, 0xF0, ##0
           0x20, 0x60, 0x20, 0x20, 0x70, ##1
           0xF0, 0x10, 0xF0, 0x80, 0xF0, ##2
           0xF0, 0x10, 0xF0, 0x10, 0xF0, ##3
           0x90, 0x90, 0xF0, 0x10, 0x10, ##4
           0xF0, 0x80, 0xF0, 0x10, 0xF0, ##5
           0xF0, 0x80, 0xF0, 0x90, 0xF0, ##6
           0xF0, 0x10, 0x20, 0x40, 0x40, ##7
           0xF0, 0x90, 0xF0, 0x90, 0xF0, ##8
           0xF0, 0x90, 0xF0, 0x10, 0xF0, ##9
           0xF0, 0x90, 0xF0, 0x90, 0x90, ##A
           0xE0, 0x90, 0xE0, 0x90, 0xE0, ##B
           0xF0, 0x80, 0x80, 0x80, 0xF0, ##C
           0xE0, 0x90, 0x90, 0x90, 0xE0, ##D
           0xF0, 0x80, 0xF0, 0x80, 0xF0, ##E
           0xF0, 0x80, 0xF0, 0x80, 0x80  ##F

        ])
        self.memory[0:self.fontSet.size] = self.fontSet[0:]

    def loadROM(self, rom):
        ROM = np.array(rom)
        self.memory[0x200:ROM.size] = ROM[0:]
        self.cycle()

    def cycle(self):
        self.opCode()

        self.step += 1
        if self.step % 2:
            if self.delayTimer > 0:
                self.delayTimer -= 1

        # Draw to the screen
        if self.displayFlag:
            x, y = np.meshgrid(range(self.width), range(self.height))
            x = x.flatten()
            y = y.flatten()

            black_pixels = self.display.flatten() == 1
            gray_pixels = ~black_pixels

            self.display[x[black_pixels], y[black_pixels]] = 1
            self.display[x[gray_pixels], y[gray_pixels]] = 0

            self.displayFlag = False

    def opCode(self):
        pc = self.pc
        opcode = (self.memory[pc] << 8) | self.memory[pc + 1]
        vX = (opcode & 0x0F00) >> 8
        vY = (opcode & 0x00F0) >> 4
        self.pc += 2

        opcode_type = (opcode & 0xF000) >> 12

        if opcode_type == 0x0:
            sub_type = opcode & 0x00FF
            if sub_type == 0x00E0:
                # Clear the display
                self.display.fill(0)
                self.displayFlag = True
            elif sub_type == 0x00EE:
                # Return from a subroutine
                self.pc = self.stack[self.sp]
                self.sp -= 1
        elif opcode_type == 0x1:
            # Jump to location nnn
            self.pc = opcode & 0x0FFF
        elif opcode_type == 0x2:
            # Call subroutine at location nnn
            self.sp += 1
            self.stack[self.sp] = self.pc
            self.pc = opcode & 0x0FFF
        elif opcode_type == 0x3:
            # Skip next instruction if Vx == kk
            if self.register[vX] == (opcode & 0x00FF):
                self.pc += 2
        elif opcode_type == 0x4:
            if self.register[vX] != (opcode & 0x00FF):
                self.pc += 2
        elif opcode_type == 0x5:
            if self.register[vX] == self.register[vY]:
                self.pc += 2
        elif opcode_type == 0x9:
            if self.register[vX] != self.register[vY]:
                self.pc += 2
        elif opcode_type == 0x6:
            self.register[vX] = (opcode & 0x00FF)
        elif opcode_type == 0x7:
            self.register[vX] = ((opcode & 0x00FF) + self.register[vX])

chip8 =  Processor(name="CHIP-8")

# Define a sample ROM (replace this with a real ROM file or data)
sample_rom = [0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF]

chip8.loadROM(sample_rom)

for _ in range(100):
    chip8.cycle()
