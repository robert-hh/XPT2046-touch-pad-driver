#
# Some sample code
#
import os, gc
from uctypes import addressof
from tft import *
from touch import *
from font8mono import font8mono

def print_centered(tft, x, y, s, font):
    length, height = font.get_stringsize(s)
    tft.setTextPos(x - length // 2, y - height // 2)
    tft.printString(s)

def draw_crosshair(tft, x, y):
    color = tft.getColor() # get previous color
    tft.setColor((255,0,0))  # red
    tft.drawHLine(x - 10, y, 20)
    tft.drawVLine(x, y - 10, 20)
    tft.setColor(color) # reset color

    
def main(get_cal = False):

    mytft = TFT("SSD1963", "LB04301", LANDSCAPE)
    width, height = mytft.getScreensize()
    mytouch = TOUCH("XPT2046")
    mytft.backlight(100) # light on

    if get_cal:
        mytft.setTextStyle(None, None, 0, font8mono)
        mytouch.touch_parameter(confidence=20, margin = 15) # make it slow & precise
        print_centered(mytft, 240, 136, "Touch the crosshair in the upper left corner", font8mono)
        draw_crosshair(mytft, 10, 10)
        x1, y1 = mytouch.get_touch(raw = True) # need the raw values here

        mytft.clrSCR()
        print_centered(mytft, 240, 136, "Touch the crosshair in the upper right corner", font8mono)
        draw_crosshair(mytft, width - 11, 10)
        x2, y2 = mytouch.get_touch(raw = True) # need the raw values here

        mytft.clrSCR()
        print_centered(mytft, 240, 136, "Touch the crosshair in the lower left corner", font8mono)
        draw_crosshair(mytft, 10, height - 11)
        x3, y3 = mytouch.get_touch(raw = True) # need the raw values here

        mytft.clrSCR()
        print_centered(mytft, 240, 136, "Touch the crosshair in the lower right corner", font8mono)
        draw_crosshair(mytft, width - 11, height - 11)
        x4, y4 = mytouch.get_touch(raw = True) # need the raw values here

        mytft.clrSCR()
        xmul_top = (width - 20) / (x2 - x1)
        xadd_top = int(-x1 + 10 / xmul_top)
        xmul_bot = (width - 20) / (x4 - x3)
        xadd_bot = int(-x3 + 10 / xmul_bot)
        ymul_left = (height - 20) / (y3 - y1)
        yadd_left = int(-y1 + 10 / ymul_left)
        ymul_right = (height - 20) / (y4 - y2)
        yadd_right = int(-y2 + 10 / ymul_right)
        res = "({},{:6.4},{},{:6.4},{},{:6.4},{},{:6.4})".format(
                xadd_top, xmul_top, xadd_bot, xmul_bot, yadd_left, ymul_left, yadd_right, ymul_right)
        mytft.setColor((255,255,255))
        print_centered(mytft, 240, 120, "Calibration =", font8mono)
        print_centered(mytft, 240, 136, res, font8mono)
        print ("Calibration =", res)
        mytouch.touch_parameter(confidence = 5, margin = 20, 
            calibration = (xadd_top, xmul_top, xadd_bot, xmul_bot, yadd_left, ymul_left, yadd_right, ymul_right))
        print_centered(mytft, 240, 152, "Now you may touch for testing", font8mono)
    else:
        print_centered(mytft, 240, 136, "Please touch me!", font8mono)
    mytft.setColor((0, 255, 0))  # green as can be
    while True:
        res = mytouch.get_touch()
        if res:
            mytft.fillCircle(res[0], res[1], 5)
    
main(True)

