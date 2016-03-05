#
# The MIT License (MIT)
# 
# Copyright (c) 2016 Robert Hammelrath
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Class supporting the resisitve touchpad of TFT LC-displays
# First example: Controller XPT2046
# It uses Y5..Y8 of PyBoard
#
import pyb, stm

# define constants
#
T_CLOCK = const(1 << 15)  ## Y8 = B15
T_DOUT  = const(1 << 14)  ## Y7 = B14
T_DIN   = const(1 << 13)  ## Y6 = B13
T_IRQ   = const(1 << 12)  ## Y5 = B12
## T_CS is not used and must be hard tied to GND

T_GETX  = const(0xd0)  ## 12 bit resolution
T_GETY  = const(0x90)  ## 12 bit resolution
T_GETZ1 = const(0xb8)  ## 8 bit resolution
T_GETZ2 = const(0xc8)  ## 8 bit resolution
#
X_LOW  = const(10)     ## lowest reasonable X value from the touchpad
Y_HIGH = const(4090)   ## highest reasonable Y value 

class TOUCH:
#
# Init just sets the PIN's to In / out as required
#    
    def __init__(self, controller = "XPT2046", calibration = None):
        self.pin_clock = pyb.Pin("Y8", pyb.Pin.OUT_PP)
        self.pin_clock.value(0)
        self.pin_d_out = pyb.Pin("Y7", pyb.Pin.OUT_PP)
        self.pin_d_in  = pyb.Pin("Y6", pyb.Pin.IN)
        self.pin_irq   = pyb.Pin("Y5", pyb.Pin.IN)
# set default values
        self.confidence = 5 
        self.delay = 10 # 10 ms between touch samples
        self.margin = 10 # tolerance margin
        if calibration:
            self.calibration = calibration
        else: # default values for my tft
            self.calibration = (-3917,-0.127,-3923,-0.1267,-3799,-0.07572,-3738,-0.07814)
#
# Now I'm up to get my touches
#
#
# set parameters for get_touch()
# res: Resolution in bits of the returned values, default = 10
# confidence: confidence level - number of consecutive touches with a margin smaller than the given level
#       which the function will sample until it accepts it as a valid touch
# margin: Difference at which touches are considered at the same position 
# delay: Delay between samples in ms.
#
    def touch_parameter(self, confidence = 5, margin = 10, delay = 10, calibration = None):
        if confidence > 25: 
            confidence = 25
        self.confidence = confidence
        if delay > 100:
            delay = 100
        self.delay = delay
        if margin > 100:
            margin = 100
        if margin < 1:
            margin = 1
        self.margin = margin
        if calibration:
            self.calibration = calibration
#
# get_touch(): get a touch value; Parameters:
#
# initital: Wait for a non-touch state before getting a sample. 
#           True = Initial wait for a non-touch state
#           False = Do not wait for a release
# wait: Wait for a touch or not?
#       False: Do not wait for a touch and return immediately
#       True: Wait until a touch is pressed. 
# raw: Setting whether raw touch coordinates (True) or normalized ones (False) are returned
#      setting the calibration vector to (0, 1, 0, 1, 0, 1, 0, 1) result in a identity mapping
# timeout: Longest time (ms, or None = 1 hr) to wait for a touch or release
#
# Return (x,y) or None
#
    def get_touch(self, initial = True, wait = True, raw = False, timeout = None):
        if timeout == None: 
            timeout = 3600000 # set timeout to 1 hour
# 
        if initial:  ## wait for a non-touch state
            sample = True
            while sample and timeout > 0:
                sample = self.raw_touch()
                pyb.delay(self.delay)
                timeout -= self.delay
            if timeout <= 0: # after timeout, return None
                return None
#
        stack = []  # build up value stack, exit early if not touch
        while len(stack) < self.confidence: # need at least confidence values in stack.
            sample = self.raw_touch()
            if sample : 
                stack.append(sample)
            else: 
                if wait:
                    stack.append((-1, -1)) # replace None by (-1, -1) here
                else:
                    return None ## leave early if no touch/dont't wait
            pyb.delay(self.delay)
            timeout -= self.delay
#
        stackptr = 0
        while timeout > 0: 
            dx = dy = True # check the stack for consistent values
            sx = sy = 0
            for i in range(self.confidence): # calculate average
                sx += stack[i][0]
                sy += stack[i][1]
            sx //= self.confidence
            sy //= self.confidence
            for i in range(self.confidence):
                dx &= abs(stack[i][0] - sx) <= self.margin
                dy &= abs(stack[i][1] - sy) <= self.margin 
            if dx and dy: # got one
                if (sx < 0 or sy < 0): # no touch is also consistent
                    if not wait: # 
                        return None
                else: 
                    if raw:
                        return (sx, sy)
                    else: 
                        return self.do_normalize((sx, sy))
# get a new value 
            sample = self.raw_touch()  # get a touch
            if sample == None: 
                sample = (-1, -1)
            stack[stackptr] = sample # add to stack
            stackptr = (stackptr + 1) % self.confidence
            pyb.delay(self.delay)
            timeout -= self.delay
        return None
# 
# do_normalize(touch)
# calculate the screen coordinates from the touch values, using the calibration values
# touch must be the tuple return by get_touch
#
    def do_normalize(self, touch):
        xmul = self.calibration[3] + (self.calibration[1] - self.calibration[3]) * (touch[1] / 4096)
        xadd = self.calibration[2] + (self.calibration[0] - self.calibration[2]) * (touch[1] / 4096)
        ymul = self.calibration[7] + (self.calibration[5] - self.calibration[7]) * (touch[0] / 4096)
        yadd = self.calibration[6] + (self.calibration[4] - self.calibration[6]) * (touch[0] / 4096)
        x = int((touch[0] + xadd) * xmul)
        y = int((touch[1] + yadd) * ymul)
        return (x, y)
#
# raw_touch(tuple)
# raw read touch. Returns (x,y) or None
#
    def raw_touch(self):
        x  = self.touch_talk(T_GETX, 12)
        y  = self.touch_talk(T_GETY, 12)
        if x > X_LOW and y < Y_HIGH:  # touch pressed?
            return (x, y)
        else:
            return None
#
# Send a command to the touch controller and wait for the response
# cmd is the command byte
# int is the expected size of return data bits
#
# Straight down coding of the data sheet's timing diagram
# Clock low & high cycles must last at least 200ns, therefore
# additional delays are required. At the moment it is set to 
# about 500ns each, 1µs total at 168 MHz clock rate.
# Total net time for a 12 bit sample: ~ 25 µs, 8 bit sample ~20 µs
#
    @staticmethod
    @micropython.viper        
    def touch_talk(cmd: int, bits: int)  -> int:
        gpiob_bsr = ptr16(stm.GPIOB + stm.GPIO_BSRRL)
        gpiob_idr = ptr16(stm.GPIOB + stm.GPIO_IDR)
#
# now shift the command out, which is 8 bits 
# data is sampled at the low-> high transient
#
        gpiob_bsr[1] = T_CLOCK # Empty clock cycle before start, maybe obsolete
        for i in range(2): pass #delay
#        gpiob_bsr[0] = T_CLOCK # clock High
#        for i in range(2): pass #delay
#        gpiob_bsr[1] = T_CLOCK # set clock low in the beginning
        mask = 0x80  # high bit first
        for i in range(8):
            gpiob_bsr[1] = T_CLOCK # set clock low in the beginning
            if cmd & mask:
                gpiob_bsr[0] = T_DOUT # set data bit high
            else:
                gpiob_bsr[1] = T_DOUT # set data bit low
            for i in range(1): pass #delay
            gpiob_bsr[0] = T_CLOCK # set clock high
            mask >>= 1
            for i in range(0): pass #delay
        gpiob_bsr[1] = T_CLOCK | T_DOUT# Another clock & data, low
        for i in range(2): pass #delay
        gpiob_bsr[0] = T_CLOCK # clock High
        for i in range(0): pass #delay
#
# now shift the data in, which is 8 or 12 bits 
# data is sampled after the high->low transient
#
        result = 0
        for i in range(bits):
            gpiob_bsr[1] = T_CLOCK # Clock low
            for i in range(1): pass # short delay
            if gpiob_idr[0] & T_DIN: # get data
                bit = 1
            else:
                bit = 0
            result = (result << 1) | bit # shift data in
            gpiob_bsr[0] = T_CLOCK # Clock high
            for i in range(1): pass # delay
#
# another clock cycle, maybe obsolete
#
        gpiob_bsr[1] = T_CLOCK # Another clock toggle, low
        for i in range(2): pass # delay
        gpiob_bsr[0] = T_CLOCK # clock High
        for i in range(2): pass #delay
        gpiob_bsr[1] = T_CLOCK # Clock low
# now we're ready to leave
        return result

