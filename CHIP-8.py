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
        }

        self.currentKey = False
        self.delayTimer = 0
        self.soundTimer = 0

        # Load fontSet
        self.fontSet = np.array([
            # FontSet values here
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
