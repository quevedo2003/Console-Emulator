import numpy as np

class Processor:

  def __init__(self,name):
    self.memory = ndarray[4096];
  	self.register = [16];
  	self.stack = [16];
  	self.i = null;
  	self.display = new Array(64*32);
  	self.displayFlag = false;
  	self.step = 0;
  
  	# program counter, should get incremented by 2 after reading an opcode
  	self.pc = 0x200;
  	# stack pointer;
  	self.sp = null;
  
  	self.opcode = null;
  	self.keys = [];
  	self.keyMap = {
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
          };
  
    self.currentKey = false;
  	self.delayTimer = 0;
  	self.soundTimer = 0;

  #BASIC INSTRUCTIONS (first nibble -- four bits)
  #00E0 clear screen (set display array to all 0) 
  #1NNN = Jump, set PC to whatever NNN is
  #2NNN = Will call the subroutine in location NNN, pop the last address in the stack and make that the PC
  #00EE will return back to the opcodes (like RET in assembly)
  #3XNN will skip one instruction if the value in VX (variable X) is equal to NN
  #4XNN will do the same as 3XNN but if they are not equal
  #the ones above are compared to immediate values
  #5XY0 will skip one instruction if VX (variable X) and VY (variable Y) are equal
  #9XY0 will do the same  as 5XY0 but if they are not equal
  #these are comparing variables in registers
  #6XNN will set the value in variable X to whatever NN is
  #7XNN will add the value of variable X to whatever NN is

  #LOGICAL INSTRUCTIONS (after the first nibble, last nibble of the opcode)
  #8XY0 will set the value in variable X to the value variable Y
  #8XY1 will perform binary OR between variable X and variable Y and place it into variable X
  #8XY2 will perform binary AND between variables X and Y and place it into X
  #8XY3 will perform binary XOR between variables X and Y and place it into X
  #8XY4 will add the value for variable X with variable Y and put it into X, this affects the flag register, if the sum is >255 then flag = 1 for overflow, if not then it stays at 0
  #8XY5 will subtract: X - Y and put it into X
  #8XY7 will subtract: Y - x and put it into X
  #8XY6 set X to the value Y, shift X one bit to the right, and set flag to the bit that was shifted out (1 or 0)
  #8XYE same as before, but will shift one bit to the left (do the same thing with the flag)
  #ANNN set the index regsiter to NNN
  #BNNN ambiguous but either choose to jump the value in register 0 with the offset of NNN, or do XNN which is the value in the register plus the offset so B220 = R2 + 220
  #CXNN will generate a random number, will do a binary AND with the value NN, and then will put into the variable X
  #DXYN will draw N pixel tall sprite from a mem location that the index register has on the screen at the (X,Y) coordinate with the values in variable X and variable Y (talk about wrapping)
  #EX9E will skip one instruction if the key corresponding to the value in variable X is pressed
  #EXA1 will skip one instruction if the key corresponding toe the value in variable X is not pressed
  #FX07 sets variable X to the current value of the delay timer
  #FX15 sets the delay timer to the value in variable X
  #FX18 sets the sound timer to the value in variable X
  #FX1E will have the index register get the value in variable x added to it
  #FX0A will stop execution and wait for key input
  #FX29 index register is set to the address of the hex character in variable X
  #FX33 takes the number in variable X and converts it into 3 decimal digits, and thens tore these digits in memory at the address of the index register (one value), so 156 would be 1 in address index, 5 in idext+1 , 6 in index+2
  #FX55 the values from variable 0 to variable X will be stored in memmory addresses starting at index I and ending at index I+x
  #FX65 does something similar but it will load values in those memory addresses into those variables

    
  def say_hi(self):
    print('Hello, my name is', self.name)
