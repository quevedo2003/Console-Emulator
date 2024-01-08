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
  #

    
  def say_hi(self):
    print('Hello, my name is', self.name)
