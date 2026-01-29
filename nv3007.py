"""
NV3007 LCD Driver for Raspberry Pi Pico / MicroPython
"""

import machine
import time
from machine import SPI, Pin


class NV3007:
    """NV3007 LCD driver class"""

    # RGB565颜色定义
    WHITE = 0xFFFF
    BLACK = 0x0000
    BLUE = 0x001F
    BRED = 0xF81F
    GRED = 0xFFE0
    GBLUE = 0x07FF
    RED = 0xF800
    MAGENTA = 0xF81F
    GREEN = 0x07E0
    CYAN = 0x7FFF
    YELLOW = 0xFFE0
    BROWN = 0xBC40
    BRRED = 0xFC07
    GRAY = 0x8430
    DARKBLUE = 0x01CF
    LIGHTBLUE = 0x7D7C
    GRAYBLUE = 0x5458
    LIGHTGREEN = 0x841F
    LGRAY = 0xC618
    LGRAYBLUE = 0xA651
    LBBLUE = 0x2B12

    def __init__(self, spi, cs, dc, rst, blk, width=142, height=428, rotation=0):
        """
        初始化NV3007屏幕

        参数:
            spi: SPI对象
            cs: CS引脚
            dc: DC引脚
            rst: RST引脚
            blk: 背光引脚
            width: 屏幕宽度
            height: 屏幕高度
            rotation: 屏幕旋转方向 (0-3) 0或1为竖屏 2或3为横屏
        """
        self.spi = spi
        self.cs = cs if isinstance(cs, Pin) else Pin(cs, Pin.OUT, value=1)
        self.dc = dc if isinstance(dc, Pin) else Pin(dc, Pin.OUT, value=1)
        self.rst = rst if isinstance(rst, Pin) else Pin(rst, Pin.OUT, value=1)
        self.blk = blk if isinstance(blk, Pin) else Pin(blk, Pin.OUT, value=0)

        self.rotation = rotation
        # 根据旋转方向设置实际的宽高
        if rotation == 0 or rotation == 1:
            self.width = width
            self.height = height
        else:
            self.width = height
            self.height = width

        self._init_display()

    def _write_reg(self, reg):
        """写寄存器命令"""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes([reg]))
        self.cs.value(1)
        self.dc.value(1)

    def _write_data(self, dat):
        """写数据"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytes([dat]))
        self.cs.value(1)

    def _write_data16(self, dat):
        """写16位数据"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytes([(dat >> 8) & 0xFF, dat & 0xFF]))
        self.cs.value(1)

    def _write_buffer(self, buffer):
        """写缓冲区数据"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(buffer)
        self.cs.value(1)

    def _set_address(self, xs, ys, xe, ye):
        """设置显示区域"""
        if self.rotation == 0:
            self._write_reg(0x2A)
            self._write_data16(xs + 12)
            self._write_data16(xe + 12)
            self._write_reg(0x2B)
            self._write_data16(ys)
            self._write_data16(ye)
            self._write_reg(0x2C)
        elif self.rotation == 1:
            self._write_reg(0x2A)
            self._write_data16(xs + 14)
            self._write_data16(xe + 14)
            self._write_reg(0x2B)
            self._write_data16(ys)
            self._write_data16(ye)
            self._write_reg(0x2C)
        elif self.rotation == 2:
            self._write_reg(0x2A)
            self._write_data16(xs)
            self._write_data16(xe)
            self._write_reg(0x2B)
            self._write_data16(ys + 14)
            self._write_data16(ye + 14)
            self._write_reg(0x2C)
        else:
            self._write_reg(0x2A)
            self._write_data16(xs)
            self._write_data16(xe)
            self._write_reg(0x2B)
            self._write_data16(ys + 12)
            self._write_data16(ye + 12)
            self._write_reg(0x2C)

    def _init_display(self):
        """初始化显示序列"""
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(120)
        self.blk.value(1)

        # 解锁并配置寄存器
        self._write_reg(0xFF)
        self._write_data(0xA5)
        self._write_reg(0x9A)
        self._write_data(0x08)
        self._write_reg(0x9B)
        self._write_data(0x08)
        self._write_reg(0x9C)
        self._write_data(0xB0)
        self._write_reg(0x9D)
        self._write_data(0x16)
        self._write_reg(0x9E)
        self._write_data(0xC4)
        self._write_reg(0x8F)
        self._write_data(0x55)
        self._write_data(0x04)
        self._write_reg(0x84)
        self._write_data(0x90)
        self._write_reg(0x83)
        self._write_data(0x7B)
        self._write_reg(0x85)
        self._write_data(0x33)
        self._write_reg(0x60)
        self._write_data(0x00)
        self._write_reg(0x70)
        self._write_data(0x00)
        self._write_reg(0x61)
        self._write_data(0x02)
        self._write_reg(0x71)
        self._write_data(0x02)
        self._write_reg(0x62)
        self._write_data(0x04)
        self._write_reg(0x72)
        self._write_data(0x04)
        self._write_reg(0x6C)
        self._write_data(0x29)
        self._write_reg(0x7C)
        self._write_data(0x29)
        self._write_reg(0x6D)
        self._write_data(0x31)
        self._write_reg(0x7D)
        self._write_data(0x31)
        self._write_reg(0x6E)
        self._write_data(0x0F)
        self._write_reg(0x7E)
        self._write_data(0x0F)
        self._write_reg(0x66)
        self._write_data(0x21)
        self._write_reg(0x76)
        self._write_data(0x21)
        self._write_reg(0x68)
        self._write_data(0x3A)
        self._write_reg(0x78)
        self._write_data(0x3A)
        self._write_reg(0x63)
        self._write_data(0x07)
        self._write_reg(0x73)
        self._write_data(0x07)
        self._write_reg(0x64)
        self._write_data(0x05)
        self._write_reg(0x74)
        self._write_data(0x05)
        self._write_reg(0x65)
        self._write_data(0x02)
        self._write_reg(0x75)
        self._write_data(0x02)
        self._write_reg(0x67)
        self._write_data(0x23)
        self._write_reg(0x77)
        self._write_data(0x23)
        self._write_reg(0x69)
        self._write_data(0x08)
        self._write_reg(0x79)
        self._write_data(0x08)
        self._write_reg(0x6A)
        self._write_data(0x13)
        self._write_reg(0x7A)
        self._write_data(0x13)
        self._write_reg(0x6B)
        self._write_data(0x13)
        self._write_reg(0x7B)
        self._write_data(0x13)
        self._write_reg(0x6F)
        self._write_data(0x00)
        self._write_reg(0x7F)
        self._write_data(0x00)
        self._write_reg(0x50)
        self._write_data(0x00)
        self._write_reg(0x52)
        self._write_data(0xD6)
        self._write_reg(0x53)
        self._write_data(0x08)
        self._write_reg(0x54)
        self._write_data(0x08)
        self._write_reg(0x55)
        self._write_data(0x1E)
        self._write_reg(0x56)
        self._write_data(0x1C)

        # GOA配置
        self._write_reg(0xA0)
        self._write_data(0x2B)
        self._write_data(0x24)
        self._write_data(0x00)
        self._write_reg(0xA1)
        self._write_data(0x87)
        self._write_reg(0xA2)
        self._write_data(0x86)
        self._write_reg(0xA5)
        self._write_data(0x00)
        self._write_reg(0xA6)
        self._write_data(0x00)
        self._write_reg(0xA7)
        self._write_data(0x00)
        self._write_reg(0xA8)
        self._write_data(0x36)
        self._write_reg(0xA9)
        self._write_data(0x7E)
        self._write_reg(0xAA)
        self._write_data(0x7E)
        self._write_reg(0xB9)
        self._write_data(0x85)
        self._write_reg(0xBA)
        self._write_data(0x84)
        self._write_reg(0xBB)
        self._write_data(0x83)
        self._write_reg(0xBC)
        self._write_data(0x82)
        self._write_reg(0xBD)
        self._write_data(0x81)
        self._write_reg(0xBE)
        self._write_data(0x80)
        self._write_reg(0xBF)
        self._write_data(0x01)
        self._write_reg(0xC0)
        self._write_data(0x02)
        self._write_reg(0xC1)
        self._write_data(0x00)
        self._write_reg(0xC2)
        self._write_data(0x00)
        self._write_reg(0xC3)
        self._write_data(0x00)
        self._write_reg(0xC4)
        self._write_data(0x33)
        self._write_reg(0xC5)
        self._write_data(0x7E)
        self._write_reg(0xC6)
        self._write_data(0x7E)
        self._write_reg(0xC8)
        self._write_data(0x33)
        self._write_data(0x33)
        self._write_reg(0xC9)
        self._write_data(0x68)
        self._write_reg(0xCA)
        self._write_data(0x69)
        self._write_reg(0xCB)
        self._write_data(0x6A)
        self._write_reg(0xCC)
        self._write_data(0x6B)
        self._write_reg(0xCD)
        self._write_data(0x33)
        self._write_data(0x33)
        self._write_reg(0xCE)
        self._write_data(0x6C)
        self._write_reg(0xCF)
        self._write_data(0x6D)
        self._write_reg(0xD0)
        self._write_data(0x6E)
        self._write_reg(0xD1)
        self._write_data(0x6F)
        self._write_reg(0xAB)
        self._write_data(0x03)
        self._write_data(0x67)
        self._write_reg(0xAC)
        self._write_data(0x03)
        self._write_data(0x6B)
        self._write_reg(0xAD)
        self._write_data(0x03)
        self._write_data(0x68)
        self._write_reg(0xAE)
        self._write_data(0x03)
        self._write_data(0x6C)
        self._write_reg(0xB3)
        self._write_data(0x00)
        self._write_reg(0xB4)
        self._write_data(0x00)
        self._write_reg(0xB5)
        self._write_data(0x00)
        self._write_reg(0xB6)
        self._write_data(0x32)
        self._write_reg(0xB7)
        self._write_data(0x7E)
        self._write_reg(0xB8)
        self._write_data(0x7E)

        # Gamma和显示配置
        self._write_reg(0xE0)
        self._write_data(0x00)
        self._write_reg(0xE1)
        self._write_data(0x03)
        self._write_data(0x0F)
        self._write_reg(0xE2)
        self._write_data(0x04)
        self._write_reg(0xE3)
        self._write_data(0x01)
        self._write_reg(0xE4)
        self._write_data(0x0E)
        self._write_reg(0xE5)
        self._write_data(0x01)
        self._write_reg(0xE6)
        self._write_data(0x19)
        self._write_reg(0xE7)
        self._write_data(0x10)
        self._write_reg(0xE8)
        self._write_data(0x10)
        self._write_reg(0xEA)
        self._write_data(0x12)
        self._write_reg(0xEB)
        self._write_data(0xD0)
        self._write_reg(0xEC)
        self._write_data(0x04)
        self._write_reg(0xED)
        self._write_data(0x07)
        self._write_reg(0xEE)
        self._write_data(0x07)
        self._write_reg(0xEF)
        self._write_data(0x09)
        self._write_reg(0xF0)
        self._write_data(0xD0)
        self._write_reg(0xF1)
        self._write_data(0x0E)
        self._write_reg(0xF9)
        self._write_data(0x17)
        self._write_reg(0xF2)
        self._write_data(0x2C)
        self._write_data(0x1B)
        self._write_data(0x0B)
        self._write_data(0x20)

        self._write_reg(0xE9)
        self._write_data(0x29)
        self._write_reg(0xEC)
        self._write_data(0x04)

        # TE配置
        self._write_reg(0x35)
        self._write_data(0x00)
        self._write_reg(0x44)
        self._write_data(0x00)
        self._write_data(0x10)
        self._write_reg(0x46)
        self._write_data(0x10)

        self._write_reg(0xFF)
        self._write_data(0x00)
        self._write_reg(0x3A)
        self._write_data(0x05)

        # 设置旋转方向
        self._write_reg(0x36)
        if self.rotation == 0:
            self._write_data(0x00)
        elif self.rotation == 1:
            self._write_data(0xC0)
        elif self.rotation == 2:
            self._write_data(0x60)
        else:
            self._write_data(0xA0)

        self._write_reg(0x11)
        time.sleep_ms(220)
        self._write_reg(0x29)
        time.sleep_ms(200)

    def clear(self, color=WHITE):
        """清屏"""
        self.fill(0, 0, self.width, self.height, color)

    def fill(self, x, y, w, h, color):
        """填充矩形区域"""
        self._set_address(x, y, x + w - 1, y + h - 1)
        num_pixels = w * h
        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF
        buffer = bytes([color_hi, color_lo]) * min(num_pixels, 2048)
        pixels_sent = 0
        while pixels_sent < num_pixels:
            chunk_size = min(2048, num_pixels - pixels_sent)
            self._write_buffer(buffer[: chunk_size * 2])
            pixels_sent += chunk_size

    def pixel(self, x, y, color):
        """画点"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self._set_address(x, y, x, y)
        self._write_data16(color)

    def line(self, x1, y1, x2, y2, color):
        """画线"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def rect(self, x, y, w, h, color):
        """画空心矩形"""
        self.line(x, y, x + w - 1, y, color)
        self.line(x, y, x, y + h - 1, color)
        self.line(x + w - 1, y, x + w - 1, y + h - 1, color)
        self.line(x, y + h - 1, x + w - 1, y + h - 1, color)

    def fill_rect(self, x, y, w, h, color):
        """画实心矩形"""
        self.fill(x, y, w, h, color)

    def circle(self, xc, yc, r, color, filled=False):
        """画圆"""
        x = 0
        y = r
        d = 3 - 2 * r
        points = []

        while y >= x:
            points.extend(
                [
                    (xc + x, yc + y),
                    (xc - x, yc + y),
                    (xc + x, yc - y),
                    (xc - x, yc - y),
                    (xc + y, yc + x),
                    (xc - y, yc + x),
                    (xc + y, yc - x),
                    (xc - y, yc - x),
                ]
            )
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

        for px, py in points:
            if filled:
                self.line(xc, yc, px, py, color)
            else:
                self.pixel(px, py, color)

    def fill_circle(self, xc, yc, r, color):
        """画实心圆"""
        self.circle(xc, yc, r, color, filled=True)

    def triangle(self, x1, y1, x2, y2, x3, y3, color, filled=False):
        """画三角形"""
        if filled:
            self.line(x1, y1, x2, y2, color)
            self.line(x2, y2, x3, y3, color)
            self.line(x3, y3, x1, y1, color)
            min_x = min(x1, x2, x3)
            max_x = max(x1, x2, x3)
            min_y = min(y1, y2, y3)
            max_y = max(y1, y2, y3)
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if self._point_in_triangle(x, y, x1, y1, x2, y2, x3, y3):
                        self.pixel(x, y, color)
        else:
            self.line(x1, y1, x2, y2, color)
            self.line(x2, y2, x3, y3, color)
            self.line(x3, y3, x1, y1, color)

    def _point_in_triangle(self, px, py, x1, y1, x2, y2, x3, y3):
        """判断点是否在三角形内"""

        def sign(p1x, p1y, p2x, p2y, p3x, p3y):
            return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)

        d1 = sign(px, py, x1, y1, x2, y2)
        d2 = sign(px, py, x2, y2, x3, y3)
        d3 = sign(px, py, x3, y3, x1, y1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def set_backlight(self, value):
        """设置背光亮度 (0-1)"""
        if value > 0:
            self.blk.value(1)
        else:
            self.blk.value(0)

    def sleep(self):
        """进入睡眠模式"""
        self._write_reg(0x28)
        time.sleep_ms(120)
        self._write_reg(0x10)
        time.sleep_ms(50)

    def wake(self):
        """唤醒屏幕"""
        self._write_reg(0x11)
        time.sleep_ms(120)
        self._write_reg(0x29)


def create(
    width=142,
    height=428,
    rotation=0,
    spi_id=0,
    sck=18,
    mosi=19,
    cs=17,
    dc=20,
    rst=21,
    blk=14,
):
    """
    创建NV3007实例的便捷函数

    参数:
        width: 屏幕宽度 (默认142)
        height: 屏幕高度 (默认428)
        rotation: 旋转方向 0-3 (默认0) 0或1为竖屏 2或3为横屏
        spi_id: SPI总线ID (默认0)
        sck: SCK引脚号 (默认18)
        mosi: MOSI引脚号 (默认19)
        cs: CS引脚号 (默认17)
        dc: DC引脚号 (默认20)
        rst: RST引脚号 (默认21)
        blk: 背光引脚号 (默认14)

    返回:
        NV3007实例
    """
    spi = SPI(
        spi_id,
        baudrate=100_000_000,
        polarity=1,
        phase=1,
        bits=8,
        sck=Pin(sck),
        mosi=Pin(mosi),
    )
    return NV3007(spi, cs, dc, rst, blk, width, height, rotation)
