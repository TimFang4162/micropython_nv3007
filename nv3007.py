"""
NV3007 LCD Driver for Raspberry Pi Pico / MicroPython
"""

import time
import math
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
        if rotation == 0 or rotation == 1:
            self.width = width
            self.height = height
        else:
            self.width = height
            self.height = width

        self._fb_width = self.width
        self._fb_height = self.height
        self._framebuffer = bytearray(self._fb_width * self._fb_height * 2)
        self._fb_dirty = True
        self._auto_flush = True
        self._font = None

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
        """写16位（半字）数据"""
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

    def _fb_set_pixel(self, x, y, color):
        """在framebuffer中设置像素点（带边界检查）"""
        if x < 0 or x >= self._fb_width or y < 0 or y >= self._fb_height:
            return
        offset = (y * self._fb_width + x) * 2
        self._framebuffer[offset] = (color >> 8) & 0xFF
        self._framebuffer[offset + 1] = color & 0xFF
        self._fb_dirty = True

    def _fb_set_pixel_unsafe(self, x, y, color):
        """在framebuffer中设置像素点（无边界检查，性能优化版本）"""
        offset = (y * self._fb_width + x) * 2
        self._framebuffer[offset] = (color >> 8) & 0xFF
        self._framebuffer[offset + 1] = color & 0xFF
        self._fb_dirty = True

    def _fb_fill_rect(self, x, y, w, h, color):
        """在framebuffer中填充矩形（优化版）"""
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if x + w > self._fb_width:
            w = self._fb_width - x
        if y + h > self._fb_height:
            h = self._fb_height - y
        if w <= 0 or h <= 0:
            return

        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF
        row_size = w * 2

        for py in range(y, y + h):
            offset = (py * self._fb_width + x) * 2
            self._framebuffer[offset : offset + row_size] = bytes([color_hi, color_lo]) * w

        self._fb_dirty = True

    def _fb_fill_h_line(self, x1, x2, y, color):
        """快速填充水平线（优化版）"""
        if y < 0 or y >= self._fb_height:
            return
        if x1 > x2:
            x1, x2 = x2, x1
        if x1 < 0:
            x1 = 0
        if x2 >= self._fb_width:
            x2 = self._fb_width - 1
        if x1 > x2:
            return

        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF
        w = x2 - x1 + 1
        offset = (y * self._fb_width + x1) * 2

        self._framebuffer[offset : offset + w * 2] = bytes([color_hi, color_lo]) * w
        self._fb_dirty = True

    def _fb_fill_v_line(self, x, y1, y2, color):
        """快速填充垂直线（优化版）"""
        if x < 0 or x >= self._fb_width:
            return
        if y1 > y2:
            y1, y2 = y2, y1
        if y1 < 0:
            y1 = 0
        if y2 >= self._fb_height:
            y2 = self._fb_height - 1
        if y1 > y2:
            return

        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF

        for py in range(y1, y2 + 1):
            offset = (py * self._fb_width + x) * 2
            self._framebuffer[offset] = color_hi
            self._framebuffer[offset + 1] = color_lo

        self._fb_dirty = True

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

    def flush(self):
        """将framebuffer内容提交到屏幕"""
        if not self._fb_dirty:
            return
        self._set_address(0, 0, self.width - 1, self.height - 1)
        chunk_size = 2048
        for i in range(0, len(self._framebuffer), chunk_size):
            chunk = self._framebuffer[i : i + chunk_size]
            self._write_buffer(chunk)
        self._fb_dirty = False

    def set_auto_flush(self, enable):
        """设置自动刷新模式"""
        self._auto_flush = enable

    def clear(self, color=WHITE):
        """清屏（优化版）"""
        self._fb_fill_rect(0, 0, self.width, self.height, color)
        if self._auto_flush:
            self.flush()

    def draw_pixel(self, x, y, color):
        """画像素点"""
        self._fb_set_pixel(x, y, color)
        if self._auto_flush:
            self.flush()

    def draw_line(self, x1, y1, x2, y2, color):
        """画直线（Bresenham算法优化）"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self._fb_set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        if self._auto_flush:
            self.flush()

    def draw_rect(self, x, y, w, h, color, radius=0, filled=False):
        """画矩形/圆角矩形（优化版）

        参数:
            x, y: 起始坐标
            w, h: 宽度和高度
            color: 颜色
            radius: 圆角半径（0为普通矩形）
            filled: 是否填充
        """
        old_auto_flush = self._auto_flush
        self._auto_flush = False

        if radius <= 0:
            if filled:
                self._fb_fill_rect(x, y, w, h, color)
            else:
                self._fb_fill_h_line(x, x + w - 1, y, color)
                self._fb_fill_h_line(x, x + w - 1, y + h - 1, color)
                self._fb_fill_v_line(x, y, y + h - 1, color)
                self._fb_fill_v_line(x + w - 1, y, y + h - 1, color)
        else:
            r = min(radius, w // 2, h // 2)
            if filled:
                self._fb_fill_rect(x, y + r, w, h - 2 * r, color)
                self._fb_fill_rect(x + r, y, w - 2 * r, h, color)
            else:
                self._fb_fill_h_line(x + r, x + w - 1 - r, y, color)
                self._fb_fill_h_line(x + r, x + w - 1 - r, y + h - 1, color)
                self._fb_fill_v_line(x, y + r, y + h - 1 - r, color)
                self._fb_fill_v_line(x + w - 1, y + r, y + h - 1 - r, color)
            self._draw_circle_quadrant(x + r, y + r, r, -1, -1, color, filled)
            self._draw_circle_quadrant(x + w - 1 - r, y + r, r, 1, -1, color, filled)
            self._draw_circle_quadrant(x + r, y + h - 1 - r, r, -1, 1, color, filled)
            self._draw_circle_quadrant(
                x + w - 1 - r, y + h - 1 - r, r, 1, 1, color, filled
            )

        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def _draw_circle_quadrant(self, xc, yc, r, x_sign, y_sign, color, filled):
        """画圆的特定象限（用于圆角矩形）

        参数:
            xc, yc: 圆心坐标
            r: 半径
            x_sign: x方向符号（1或-1）
            y_sign: y方向符号（1或-1）
            color: 颜色
            filled: 是否填充
        """
        if not filled:
            x = 0
            y = r
            d = 3 - 2 * r
            while y >= x:
                px1 = xc + x * x_sign
                py1 = yc + y * y_sign
                if 0 <= px1 < self._fb_width and 0 <= py1 < self._fb_height:
                    self._fb_set_pixel_unsafe(px1, py1, color)
                px2 = xc + y * x_sign
                py2 = yc + x * y_sign
                if 0 <= px2 < self._fb_width and 0 <= py2 < self._fb_height:
                    self._fb_set_pixel_unsafe(px2, py2, color)
                x += 1
                if d > 0:
                    y -= 1
                    d = d + 4 * (x - y) + 10
                else:
                    d = d + 4 * x + 6
        else:
            y_start = max(0, yc - r)
            y_end = min(yc + r, self._fb_height - 1)
            for py in range(y_start, y_end + 1):
                dy = py - yc
                dy2 = dy * dy
                dx_max = int(math.sqrt(r * r - dy2))
                if dy2 <= r * r:
                    x_start = max(0, xc - dx_max)
                    x_end = min(xc + dx_max, self._fb_width - 1)
                    if x_start <= x_end:
                        self._fb_fill_h_line(x_start, x_end, py, color)

    def draw_circle(self, xc, yc, r, color, filled=False):
        """画圆（极致优化版）"""
        old_auto_flush = self._auto_flush
        self._auto_flush = False

        if filled:
            y_start = max(0, yc - r)
            y_end = min(yc + r, self._fb_height - 1)

            color_hi = (color >> 8) & 0xFF
            color_lo = color & 0xFF
            r2 = r * r

            for py in range(y_start, y_end + 1):
                dy = py - yc
                dy2 = dy * dy
                if dy2 <= r2:
                    dx_max = int(math.sqrt(r2 - dy2))
                    x_start = max(0, xc - dx_max)
                    x_end = min(xc + dx_max, self._fb_width - 1)
                    if x_start <= x_end:
                        w = x_end - x_start + 1
                        offset = (py * self._fb_width + x_start) * 2
                        self._framebuffer[offset : offset + w * 2] = bytes([color_hi, color_lo]) * w
            self._fb_dirty = True
        else:
            x = 0
            y = r
            d = 3 - 2 * r

            while y >= x:
                points = [
                    (xc + x, yc + y), (xc - x, yc + y),
                    (xc + x, yc - y), (xc - x, yc - y),
                    (xc + y, yc + x), (xc - y, yc + x),
                    (xc + y, yc - x), (xc - y, yc - x)
                ]

                for px, py in points:
                    if 0 <= px < self._fb_width and 0 <= py < self._fb_height:
                        offset = (py * self._fb_width + px) * 2
                        self._framebuffer[offset] = (color >> 8) & 0xFF
                        self._framebuffer[offset + 1] = color & 0xFF

                x += 1
                if d > 0:
                    y -= 1
                    d = d + 4 * (x - y) + 10
                else:
                    d = d + 4 * x + 6

            self._fb_dirty = True

        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def draw_arc(self, xc, yc, r, start_angle, end_angle, color, filled=False):
        """画弧（优化版）"""
        points = []
        steps = max(1, int(r * 2 * 3.14159 / 5))
        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * i / steps
            px = int(xc + r * math.cos(angle))
            py = int(yc + r * math.sin(angle))
            points.append((px, py))
        if filled:
            points.append((xc, yc))
        old_auto_flush = self._auto_flush
        self._auto_flush = False
        for i in range(len(points) - 1):
            px1, py1 = points[i]
            px2, py2 = points[i + 1]
            dx = abs(px2 - px1)
            dy = abs(py2 - py1)
            sx = 1 if px1 < px2 else -1
            sy = 1 if py1 < py2 else -1
            err = dx - dy
            while True:
                if 0 <= px1 < self._fb_width and 0 <= py1 < self._fb_height:
                    self._fb_set_pixel_unsafe(px1, py1, color)
                if px1 == px2 and py1 == py2:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    px1 += sx
                if e2 < dx:
                    err += dx
                    py1 += sy
        if filled:
            self.draw_polygon(points, color, filled=True)
        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def draw_ellipse(self, xc, yc, rx, ry, color, filled=False):
        """画椭圆（极致优化版）"""
        old_auto_flush = self._auto_flush
        self._auto_flush = False

        if filled:
            y_start = max(0, yc - ry)
            y_end = min(yc + ry, self._fb_height - 1)

            color_hi = (color >> 8) & 0xFF
            color_lo = color & 0xFF
            ry2 = ry * ry

            for py in range(y_start, y_end + 1):
                dy = py - yc
                dy2 = dy * dy
                if dy2 <= ry2:
                    dx_max = int(rx * math.sqrt(1 - dy2 / ry2))
                    x_start = max(0, xc - dx_max)
                    x_end = min(xc + dx_max, self._fb_width - 1)
                    if x_start <= x_end:
                        w = x_end - x_start + 1
                        offset = (py * self._fb_width + x_start) * 2
                        self._framebuffer[offset : offset + w * 2] = bytes([color_hi, color_lo]) * w
            self._fb_dirty = True
        else:
            steps = max(1, int(max(rx, ry) * 2 * 3.14159 / 5))
            for i in range(steps):
                angle = 2 * 3.14159 * i / steps
                px = int(xc + rx * math.cos(angle))
                py = int(yc + ry * math.sin(angle))
                if 0 <= px < self._fb_width and 0 <= py < self._fb_height:
                    offset = (py * self._fb_width + px) * 2
                    self._framebuffer[offset] = (color >> 8) & 0xFF
                    self._framebuffer[offset + 1] = color & 0xFF
            self._fb_dirty = True

        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def draw_triangle(self, x1, y1, x2, y2, x3, y3, color, filled=False):
        """画三角形"""
        self.draw_polygon([(x1, y1), (x2, y2), (x3, y3)], color, filled)

    def draw_polygon(self, vertices, color, filled=False):
        """画多边形（优化版）"""
        n = len(vertices)
        if n < 3:
            return
        old_auto_flush = self._auto_flush
        self._auto_flush = False
        if not filled:
            for i in range(n):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % n]
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                sx = 1 if x1 < x2 else -1
                sy = 1 if y1 < y2 else -1
                err = dx - dy
                while True:
                    if 0 <= x1 < self._fb_width and 0 <= y1 < self._fb_height:
                        self._fb_set_pixel_unsafe(x1, y1, color)
                    if x1 == x2 and y1 == y2:
                        break
                    e2 = 2 * err
                    if e2 > -dy:
                        err -= dy
                        x1 += sx
                    if e2 < dx:
                        err += dx
                        y1 += sy
        else:
            min_y = max(0, min(v[1] for v in vertices))
            max_y = min(max(v[1] for v in vertices), self._fb_height - 1)

            color_hi = (color >> 8) & 0xFF
            color_lo = color & 0xFF

            for y in range(min_y, max_y + 1):
                intersections = []
                for i in range(n):
                    x1, y1 = vertices[i]
                    x2, y2 = vertices[(i + 1) % n]
                    if (y1 <= y < y2) or (y2 <= y < y1):
                        if y1 != y2:
                            x = x1 + (y - y1) * (x2 - x1) // (y2 - y1)
                            intersections.append(x)
                intersections.sort()
                for i in range(0, len(intersections), 2):
                    if i + 1 < len(intersections):
                        x_start = max(0, min(intersections[i], self._fb_width - 1))
                        x_end = max(0, min(intersections[i + 1], self._fb_width - 1))
                        if x_start <= x_end:
                            w = x_end - x_start + 1
                            offset = (y * self._fb_width + x_start) * 2
                            self._framebuffer[offset : offset + w * 2] = bytes([color_hi, color_lo]) * w

            self._fb_dirty = True
        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def draw_bitmap(self, x, y, bitmap, w, h, color):
        """画位图（优化版）"""
        if not isinstance(bitmap, bytes):
            bitmap = bytes(bitmap)
        old_auto_flush = self._auto_flush
        self._auto_flush = False

        rows = (h + 7) // 8
        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF

        for row in range(h):
            byte_row = row // 8
            bit_offset = 7 - (row % 8)
            for col in range(w):
                byte_index = byte_row * w + col
                if byte_index < len(bitmap) and (bitmap[byte_index] >> bit_offset) & 1:
                    px, py = x + col, y + row
                    if 0 <= px < self._fb_width and 0 <= py < self._fb_height:
                        offset = (py * self._fb_width + px) * 2
                        self._framebuffer[offset] = color_hi
                        self._framebuffer[offset + 1] = color_lo

        self._fb_dirty = True
        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def draw_bitmap_rgb565(self, x, y, bitmap, w, h):
        """画RGB565位图（优化版）"""
        if not isinstance(bitmap, bytes):
            bitmap = bytes(bitmap)
        old_auto_flush = self._auto_flush
        self._auto_flush = False

        for row in range(h):
            if y + row < 0 or y + row >= self._fb_height:
                continue
            for col in range(w):
                if x + col < 0 or x + col >= self._fb_width:
                    continue
                index = (row * w + col) * 2
                if index + 1 < len(bitmap):
                    offset = ((y + row) * self._fb_width + (x + col)) * 2
                    self._framebuffer[offset] = bitmap[index]
                    self._framebuffer[offset + 1] = bitmap[index + 1]

        self._fb_dirty = True
        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

    def set_font(self, font_module):
        """设置字体模块"""
        self._font = font_module

    def draw_text(self, x, y, text, fg_color=None):
        """绘制文本

        参数:
            x, y: 文本起始坐标
            text: 要绘制的文本
            fg_color: 前景色（默认WHITE）
        """
        if self._font is None:
            return

        if fg_color is None:
            fg_color = self.WHITE

        old_auto_flush = self._auto_flush
        self._auto_flush = False

        font_height = self._font.height()

        cur_x = x
        for ch in text:
            bitmap, ch_height, ch_width = self._font.get_ch(ch)
            bytes_per_row = (ch_width + 7) // 8

            for row in range(ch_height):
                py = y + row
                if py < 0 or py >= self._fb_height:
                    continue

                for col in range(ch_width):
                    px = cur_x + col
                    if px < 0 or px >= self._fb_width:
                        continue

                    byte_idx = row * bytes_per_row + (col // 8)
                    bit_pos = 7 - (col % 8)

                    if byte_idx < len(bitmap):
                        pixel_set = (bitmap[byte_idx] >> bit_pos) & 1
                    else:
                        pixel_set = 0

                    if pixel_set:
                        self._fb_set_pixel_unsafe(px, py, fg_color)

            cur_x += ch_width

        self._fb_dirty = True
        self._auto_flush = old_auto_flush
        if self._auto_flush:
            self.flush()

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
