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
  
  	# program counter
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
    
  def say_hi(self):
    print('Hello, my name is', self.name)
