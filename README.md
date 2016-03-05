#touch pad Class for the XPT2046 controller

**Description**

A Python class for using a resistive touch pad with a XPT2046 controller. This port uses at least 3 control lines:

- Y8 for Clock
- Y7 for Data Out (from Pyboard to XPT2046)
- Y6 for Data In  (from XPT2046 to Pyboard)

Optional:

- Y5 for IRQ (not used at the moment)

CS of the touch pad must be tied to GND. The touch pad will typically uses in combination with a TFT. In may case, it was glued to a 4.3" TFT with an SSD1963 controller. The class itself does not rely on an TFT, but for calibration a TFT is used.

At the moment, the code is a basic package. It will deliver touch events. But the mapping to a TFT's coordinates is tested with that single TFT in Landscape mode only.

The touch pad is used in 12 bit mode, returning values in the range of 0..4095 for the coordinates. A single raw sampling takes about 40µs (25µs net). The result is somewhat noisy, and the touch pad has the habit of creating false touches in the transition of press and release. The function get_touch caters for that.


**Functions**
```
Create instance:

mytouch = TOUCH(controller [, calibration = (cal. vector))
    controller: String with the controller model. At the moment, it is ignored
    calibration: Tuple of 8 numbers, which transpose touch pad coordinates into TFT coordinates. 
        You can determine these with the tool calibraty.py (see below) of the package. A vector of
        (0, 1, 0, 1, 0, 1, 0, 1) will deliver the raw values.
        The calibration is performed typically once. Once determined, you may also code these values
        into the sources.

Functions:

touch_parameter(confidence = 5, margin = 10, delay = 10, calibration = None)
    # Set the operational parameters of the touch pad. All parameters are optional
    confidence: Number of consecutive touches that must match within the value of margin.
    margin: Value by which touch coordinates may differ and still being considered at the 
        same place.
    delay: delay in ms between consecutive samples during data capture.
    calibration: Calibration vector. This is the same one as may be used in creating the instance.
    
get_touch(initial = True, wait = True, raw = False, timeout = None)
    # This is the major data entry function. Parameters:
    initial: if True, wait for a non-touch state of the touch pad before getting 
        the touch coordinates. This is the natural behavior. If False, get the next touch 
        immediately and do not what for the stylus to be released.
    wait: If True, wait for a valid touch event. If True, return immediately if no
        touch is made.
    raw: If False, return screen coordinates. That  required that valid calibration
        values have been set. If True, return the raw coordinates of the touch pad
    timeout: Timeout for the function, unit ms, for all situations where the function is
        told to wait, e.g. initial = True or wait = True. 
        A value of None is considered as a timeout of an hour.
    
    The function returns a two value tuple (x,y) of the touch coordinates, or 'None', if either no touch is 
    pressed or the timeout triggers.

do_normalize(touch)
    # Transpose touch coordinates into TFT coordinates. The function requires the calibration 
      values to be set to a reasonable value. It is called within get_touch too. Parameter:
    touch: a touch pad value tuple returned by get_touch() in raw mode or raw_touch()
----- lower level functions ---

raw_touch()
    # determine the raw touch value and return immediately. The return value is a pair of 
      touch pad coordinates, is a touch is present, or 'None'
      
touch_talk(command, bits)
    # send commands to the touch pad controller and retrieves 'bits' data from it.
      It will always perform and return. No checking is done for the command value
      and the returned information.
```

**Files:**
- touch.py: Source file with comments.
- calibration.py: Code to determine the calibration of the touch pad, which allows to map between touch pad
and screen coordinates. You will be asked to touch four points at the screen indicated by a cross-hair. 
The confidence level is set high, so keep your hand steady. If it fails at a certain point, release and touch again.
The determined values are printed on the screen and at the USB interface. So you can copy them from there.
Once the values are know, they are set temporarily, and you may try them. Just touch the screen. At the point of 
touching, a small green circle should light up. If the match is bad, repeat the calibration. 
- touchtest.py: Another sample test program, which creates a small four button keypad, which is defined by
a table.
- README.md: this one
- LICENSE: The MIT license file

**To Do**
- consider ISR mode
- test portrait mode

**Short Version History**

**0.1** 
Initial release with the basic functions

