# Based on Jason/ loktar00's CHIP-8 Javascript code- https://github.com/loktar00/chip8/blob/master/chip8.js 
# Along with Tobias V. Langhoff's "Guide to making a CHIP-8 emulator" - https://tobiasvl.github.io/blog/write-a-chip-8-emulator/ 
#
# screen, pixelsize, width, and height still need to be defined (along with graphics engine that is)

import numpy as np
import random as rand
import keyboard

class Processor:
    def __init__(self, name):
        # Initialization code here
        self.width = 64  # Define appropriate values for width and height
        self.height = 32
        self.memory = np.zeros((1, 4096))
        self.register = np.zeros((1, 16))
        self.stack = np.zeros((1, 16))
        self.i = 0
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
            # Skip next instruction if Vx != kk
            if self.register[vX] != (opcode & 0x00FF):
                self.pc += 2
        elif opcode_type == 0x5:
            # Skip next instruction if Vx == Vy
            if self.register[vX] == self.register[vY]:
                self.pc += 2
        elif opcode_type == 0x6:
            # Make vX == NNN
            self.register[vX] = (opcode & 0x00FF)
        elif opcode_type == 0x7:
            # Make vX == NNN + vX
            self.register[vX] = ((opcode & 0x00FF) + self.register[vX])
        elif opcode_type == 0x8: 
            # Logical operations
            lastnib = opcode & 0x000F #only need the last 4 bits
            if lastnib == 0:
                # Make vX == vY
                self.register[vX] = vY;
            elif lastnib == 1:
                # Preform bitwise OR between vX and vY
                self.register[vX] = self.register[vX] | self.register[vY]
            elif lastnib == 2:
                # Preform bitwise AND between vX and vY
                self.register[vX] = self.register[vX] & self.register[vY]
            elif lastnib == 3:
                # Preform bitwise XOR between vX and vY
                self.register[vX] = self.register[vX] ^ self.register[vY]
            elif lastnib == 4:
                # Add whatever is in vX with whatever is in vY
                self.register[vX] = self.register[vX] + self.register[vY]
                if self.register[vX] > 255:
                    self.displayFlag = True
            elif lastnib == 5:
                # Subtract vX = vY
                self.register[vX] = self.register[vX] - self.register[vY]
            elif lastnib == 6:
                ## bit wise right shift
                self.register[vX] = self.register[vY]
                bitshifted = self.register[vX] & 0x8000
                self.register[vX] = self.register[vX]>>1
                self.displayFlag = bitshifted
            elif lastnib == 7:
                #substract vY - vX
                self.register[vX] = self.register[vY] - self.register[vX]
            elif lastnib == 0xE:
                ## bitwise left shift
                self.register[vX] = self.register[vY]
                bitshifted = self.register[vX] & 0x0001
                self.register[vX] = self.register[vX]<<1
                self.displayFlag = bitshifted
        elif opcode_type == 0x9:
            # Skip next instructiom  if Vx != Vy
            if self.register[vX] != self.register[vY]:
                self.pc += 2
        elif opcode_type == 0xA:
            self.i = (opcode & 0x0FFF)
        elif opcode_type == 0xB:
            ## have to choose which method to do with this, this is about jumping with either usings v0 or vN
            ## do first method
            self.pc = self.register[0] + (opcode & 0x0FFF)
        elif opcode_type == 0xC:
            #generate a random number and do bitwise AND and put that into vX
            randomnum = rand.random()
            self.register[vX] = randomnum & (opcode & 0x00FF)
        elif opcode_type == 0xD:
            #need help with this one, draw N pixel tall sprite from a mem location that the indesx register has on and x,y coordinate x being the value in vX and y being the value in vY
        elif opcode_type == 0xE:
            if(opcode & 0x00FF) == 0x9E:
                #if the key equals to corresponding value in vX, skip instruction
                if self.register[vX] == self.key[0]: #needs to get fixed
                    self.pc += 2
            elif (opcode & 0x00FF) == 0xA1:
                #if the key is not equal to corresponding value in vX, skip instruction
                if self.register[vY] != self.key[0]: #also needs to get fixed
                    self.pc += 2
        elif opcode_type == 0xF:
            lastbyte = (opcode & 0x00FF)
            if lastbyte == 0x07:
                #make vX == to delay timer
                self.register[vX] = self.delayTimer
            elif lastbyte == 0x15:
                # make delay == to vX
                self.delayTimer = self.register[vX]
            elif lastbyte == 0x18:
                #make sound == to vX
                self.soundTimer = self.register[vX]
            elif lastbyte == 0x1E:
                # add vX to index
                self.i += self.register[vX]
            elif lastbyte == 0x0A:
                #stop excecution (help on this)
            elif lastbyte == 0x29:
                self.i = 1 #just a place holder, need help with this
            elif lastbyte == 0x33:
                #takes the number in vX and converts it into 3 decimal digit then stores them in memory address starting at idx
                self.memory[self.i] = self.register[vX] / 100
                temp = self.register[vX]%10
                self.memory[self.i+1] = temp/10
                temp %= 10
                self.memory[self.i+2] = temp
                #needs to get fixed 
            elif lastbyte == 0x55:
                #takes the values from v0 to vX and will store them into memory starting at index til index + vX
                count = 0
                while count <= vX:
                   self.memory[self.i + count] =  self.register[count]
                   count += 1
            elif lastbyte == 0x65:
                #will load v0 to vX from mem locations index to index+vX
                count = 0
                while count <= vX:
                    self.register[count] = self.memory[self.i + count]
                    count += 1


chip8 =  Processor(name="CHIP-8")

# Define a sample ROM (replace this with a real ROM file or data)
sample_rom = [0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF]

chip8.loadROM(sample_rom)

for _ in range(100):
    chip8.cycle()
