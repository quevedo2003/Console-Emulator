"""The almighty Hello World! example"""
# We'll use sys to properly exit with an error code.
import os
import sys
import sdl2
import sdl2.ext
import numpy as np
import random as rand
import keyboard

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)

filepath = os.path.abspath(os.path.dirname(__file__))
RESOURCES = sdl2.ext.Resources(filepath, "resources")

class Processor:
    def __init__(self, name):
        # Initialization code here
        self.width = 640  # Define appropriate values for width and height
        self.height = 320
        self.memory = np.zeros(4096, dtype=np.uint8)
        self.register = np.zeros(16, dtype=np.uint8)
        self.stack = np.zeros((1, 16), dtype=np.uint8)
        self.i = 0
        self.display = np.zeros((640, 320), dtype=np.uint8)
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
        self.memory[0:len(self.fontSet)] = self.fontSet


    def loadROM(self, rom):
        ROM = np.array(rom)
        self.memory[0x200:0x200 + ROM.size] = ROM[:]
        self.cycle()

    def cycle(self):
        self.opCode()

        self.step += 1
        if self.step % 2:
            if self.delayTimer > 0:
                self.delayTimer -= 1
        # Draw to the screen
        if self.displayFlag:
            self.render()
            self.displayFlag = False

    def render(self):
        x, y = np.meshgrid(range(self.width), range(self.height))
        x = x.flatten()
        y = y.flatten()

        black_pixels = self.display.flatten() == 1
        gray_pixels = ~black_pixels

        self.display[x[black_pixels], y[black_pixels]] = 1
        self.display[x[gray_pixels], y[gray_pixels]] = 0

    def opCode(self):
        pc = self.pc
        # Check if pc and pc + 1 are within the valid range
        if pc >= 0 and pc + 1 < len(self.memory):
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
                vX = (opcode & 0x0F00) >> 8
                vY = (opcode & 0x00F0) >> 4

                # Check if vX and vY are within the valid range
                if 0 <= vX < 16:
                    self.register[vX] = (opcode & 0x00FF)
                else:
                    # Handle the error or log a message
                    print("Invalid register index:", vX, vY)
            elif opcode_type == 0x7:
                # Make vX == NNN + vX
                self.register[vX] = ((opcode & 0x00FF) + self.register[vX])
            elif opcode_type == 0x8: 
                # Logical operations
                lastnib = opcode & 0x000F #only need the last 4 bits
                if lastnib == 0:
                    # Make vX == vY
                    self.register[vX] = vY
                elif lastnib == 1:
                    # Preform bitwise OR between vX and vY
                    self.register[vX] = self.register[vX] | self.register[vY]
                elif lastnib == 2:
                    # Preform bitwise AND between vX and vY
                    self.register[vX] = self.register[vX] & self.register[vY]
                elif lastnib == 3:
                    # Preform bitwise XOR between vX and vY
                    self.register[vX] = self.register[vY] ^ self.register[vX]
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
                print(self.i)
            elif opcode_type == 0xB:
                ## have to choose which method to do with this, this is about jumping with either usings v0 or vN
                ## do first method
                self.pc = self.register[0] + (opcode & 0x0FFF)
            elif opcode_type == 0xC:
                #generate a random number and do bitwise AND and put that into vX
                randomnum = rand.random()
                self.register[vX] = randomnum & (opcode & 0x00FF)
            elif opcode_type == 0xD:
                x_coord = self.register[vX]
                print("X_COORD:", x_coord)
                y_coord = self.register[vY]
                print("Y_COORD:", y_coord)
                height = opcode & 0x000F
                print("HEIGHT:", height)

                self.displayFlag = True  # Set the flag to update the display

                for y_line in range(height):
                    sprite_byte = self.memory[self.i + y_line]
                    for x_line in range(8):
                        pixel_value = (sprite_byte >> (7 - x_line)) & 0x01
                        x_pixel = (x_coord + x_line) % self.width
                        y_pixel = (y_coord + y_line) % self.height

                        # XOR the pixel value with the current display value using the Python XOR operator
                        self.display[x_pixel, y_pixel] = self.display[x_pixel, y_pixel] ^ pixel_value
                        print(display[x_pixel, y_pixel])


                self.displayFlag = True  # Set the flag to update the display

            elif opcode_type == 0xE:
                if(opcode & 0x00FF) == 0x9E:
                    #if the key equals to corresponding value in vX, skip instruction
                    if self.register[vX] == self.keys[0]: #needs to get fixed
                        self.pc += 2
                elif (opcode & 0x00FF) == 0xA1:
                    #if the key is not equal to corresponding value in vX, skip instruction
                    if self.register[vY] != self.keys[0]: #also needs to get fixed
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
                    # add the value in vX to the index register
                    self.i += self.register[vX]
                elif lastbyte == 0x0A:
                    # stop execution and wait for key press, store key value in vX
                    key_pressed = False
                    for key, value in self.keyMap.items():
                        if keyboard.is_pressed(str(key)):
                            self.register[vX] = value
                            key_pressed = True
                            break
                    if not key_pressed:
                        # Skip the current cycle if no key is pressed
                        self.pc -= 2
                elif lastbyte == 0x29:
                    # set index to the address of the sprite for the character in vX
                    self.i = self.register[vX] * 5  # Assuming each character is 5 bytes long
                elif lastbyte == 0x33:
                    # takes the number in vX and converts it into 3 decimal digits, then stores them in memory starting at idx
                    value = self.register[vX]
                    self.memory[self.i] = value // 100
                    value %= 100
                    self.memory[self.i + 1] = value // 10
                    value %= 10
                    self.memory[self.i + 2] = value
                elif lastbyte == 0x55:
                    #takes the values from v0 to vX and will store them in memory starting at index til index + vX
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
        else:
            # Handle the case when the program counter is out of bounds
            raise IndexError("Program counter out of bounds")

if __name__ == "__main__":
    ### ROM ###
    ROM = [
        0xA2, 0x1E,  # Set I to the address 0x21E
        0x62, 0x00,  # Set V2 to 0x00
        0x63, 0x00,  # Set V3 to 0x00
        0xF2, 0x29,  # Set I to the address of 'H' in the font
        0xD2, 0x3F,  # Draw 'H' at position (V2, V3)
        0xF2, 0x25,  # Set I to the address of 'E' in the font
        0xD2, 0x3F,  # Draw 'E'
        0xF2, 0x21,  # Set I to the address of 'L' in the font
        0xD2, 0x3F,  # Draw 'L'
        0xF2, 0x27,  # Set I to the address of 'O' in the font
        0xD2, 0x3F,  # Draw 'O'
        0x00, 0xE0   # Clear the screen
    ]
    ###########
    chip8 = Processor(name="CHIP-8")
    chip8.loadROM(ROM)

    sdl2.ext.init()

    # Set the window size as a tuple
    window_size = (640, 320)
    
    window = sdl2.ext.Window("CHIP-8 Emulator", size=window_size)
    window.show()

    # Get the window's surface
    window_surface = window.get_surface()

    running = True
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        chip8.cycle()

        # Draw directly on the window surface
        sdl2.ext.fill(window_surface, BLACK)
        pixelview = sdl2.ext.PixelView(window_surface)

        # Access the display array from the processor
        display = chip8.display

        # Draw to the window surface directly
        for x in range(display.shape[0]):
            for y in range(display.shape[1]):
                if display[x, y] == 1:
                    pixelview[y][x] = WHITE
        window.refresh()

        sdl2.SDL_Delay(10)

    sdl2.ext.quit()
