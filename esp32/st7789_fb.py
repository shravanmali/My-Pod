from machine import Pin ,SPI
import framebuf
import time

def rgb565(r, g, b):
    c = ((r & 0xf8)<< 8) | ((g & 0xFC) << 3) | (b >> 3)
    return ((c & 0xFF)<< 8) | (c >> 8 )

class ST7789(framebuf.FrameBuffer) :
    def __init__(self , width = 240 , height = 280):
        self.width = width
        self.height = height
        self.buf = bytearray(width * height * 2)
        super().__init__(self.buf, width, height, framebuf.RGB565)

        self.spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(12), mosi=Pin(11))
        self.dc = Pin(9, Pin.OUT, value=0)
        self.cs = Pin(10, Pin.OUT, value=1)
        self.rst = Pin(14, Pin.OUT, value=1)
        self.bl = Pin(13, Pin.OUT, value=1)
        self.init_display()

    def cmd(self, c, data=None):
        self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([c]))
        if data:
            self.dc(1)
            self.spi.write(data)
        self.cs(1)

    def init_display(self):
        self.rst(1)
        time.sleep_ms(20)
        self.rst(0)
        time.sleep_ms(20)
        self.rst(1)
        time.sleep_ms(120)

        self.cmd(0x11)
        time.sleep_ms(120)
        self.cmd(0x36, b"\x00")
        self.cmd(0x3A, b"\x55")
        self.cmd(0x21)
        self.cmd(0x29)

    def show(self):
        self.cmd(0x2A, bytes([0, 0, 0, self.width - 1]))
        y0, y1 = 20, 20 + self.height - 1
        self.cmd(0x2B, bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self.cs(0)
        self.dc(0)
        self.spi.write(b"\x2C")
        self.dc(1)
        self.spi.write(self.buf)
        self.cs(1)