import machine
import time
from machine import SPI, Pin

# 屏幕分辨率配置
USE_HORIZONTAL = 0  # 0或1为竖屏 2或3为横屏
if USE_HORIZONTAL == 0 or USE_HORIZONTAL == 1:
    LCD_W = 142
    LCD_H = 428
else:
    LCD_W = 428
    LCD_H = 142

# 引脚定义
BLK_PIN = 14
RST_PIN = 21
DC_PIN = 20
SDA_PIN = 19  # MOSI
SCL_PIN = 18  # SCK
CS_PIN = 17

# 颜色定义 (RGB565格式)
WHITE = 0xFFFF
BLACK = 0x0000
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0
YELLOW = 0xFFE0
CYAN = 0x07FF
MAGENTA = 0xF81F

# 初始化SPI和GPIO
spi = SPI(0, baudrate=8000000, polarity=1, phase=1, bits=8, sck=Pin(SCL_PIN), mosi=Pin(SDA_PIN))
cs = Pin(CS_PIN, Pin.OUT, value=1)
dc = Pin(DC_PIN, Pin.OUT, value=1)
rst = Pin(RST_PIN, Pin.OUT, value=1)
blk = Pin(BLK_PIN, Pin.OUT, value=0)

# SPI写入函数
def spi_write(data):
    cs.value(0)
    spi.write(data)
    cs.value(1)

def spi_write_byte(dat):
    spi_write(bytes([dat]))

def spi_write_halfword(dat):
    spi_write(bytes([(dat >> 8) & 0xFF, dat & 0xFF]))

# 屏幕控制函数
def lcd_write_reg(reg):
    dc.value(0)
    spi_write_byte(reg)
    dc.value(1)

def lcd_write_data(dat):
    dc.value(1)
    spi_write_byte(dat)

def lcd_write_halfword(dat):
    dc.value(1)
    spi_write_halfword(dat)

def lcd_address_set(xs, ys, xe, ye):
    if USE_HORIZONTAL == 0:
        lcd_write_reg(0x2a)
        lcd_write_halfword(xs + 12)
        lcd_write_halfword(xe + 12)
        lcd_write_reg(0x2b)
        lcd_write_halfword(ys)
        lcd_write_halfword(ye)
        lcd_write_reg(0x2c)
    elif USE_HORIZONTAL == 1:
        lcd_write_reg(0x2a)
        lcd_write_halfword(xs + 14)
        lcd_write_halfword(xe + 14)
        lcd_write_reg(0x2b)
        lcd_write_halfword(ys)
        lcd_write_halfword(ye)
        lcd_write_reg(0x2c)
    elif USE_HORIZONTAL == 2:
        lcd_write_reg(0x2a)
        lcd_write_halfword(xs)
        lcd_write_halfword(xe)
        lcd_write_reg(0x2b)
        lcd_write_halfword(ys + 14)
        lcd_write_halfword(ye + 14)
        lcd_write_reg(0x2c)
    else:
        lcd_write_reg(0x2a)
        lcd_write_halfword(xs)
        lcd_write_halfword(xe)
        lcd_write_reg(0x2b)
        lcd_write_halfword(ys + 12)
        lcd_write_halfword(ye + 12)
        lcd_write_reg(0x2c)

def lcd_fill(xs, ys, xe, ye, color):
    lcd_address_set(xs, ys, xe - 1, ye - 1)
    num_pixels = (xe - xs) * (ye - ys)
    color_hi = (color >> 8) & 0xFF
    color_lo = color & 0xFF
    buffer = bytes([color_hi, color_lo]) * min(num_pixels, 4096)
    pixels_sent = 0
    while pixels_sent < num_pixels:
        chunk_size = min(4096, num_pixels - pixels_sent)
        dc.value(1)
        cs.value(0)
        spi.write(buffer[:chunk_size * 2])
        cs.value(1)
        pixels_sent += chunk_size

# 屏幕初始化序列
def lcd_init():
    rst.value(1)
    time.sleep_ms(50)
    rst.value(0)
    time.sleep_ms(50)
    rst.value(1)
    time.sleep_ms(120)
    blk.value(1)
    
    # 初始化序列
    lcd_write_reg(0xff)
    lcd_write_data(0xa5)
    lcd_write_reg(0x9a)
    lcd_write_data(0x08)
    lcd_write_reg(0x9b)
    lcd_write_data(0x08)
    lcd_write_reg(0x9c)
    lcd_write_data(0xb0)
    lcd_write_reg(0x9d)
    lcd_write_data(0x16)
    lcd_write_reg(0x9e)
    lcd_write_data(0xc4)
    lcd_write_reg(0x8f)
    lcd_write_data(0x55)
    lcd_write_data(0x04)
    lcd_write_reg(0x84)
    lcd_write_data(0x90)
    lcd_write_reg(0x83)
    lcd_write_data(0x7b)
    lcd_write_reg(0x85)
    lcd_write_data(0x33)
    lcd_write_reg(0x60)
    lcd_write_data(0x00)
    lcd_write_reg(0x70)
    lcd_write_data(0x00)
    lcd_write_reg(0x61)
    lcd_write_data(0x02)
    lcd_write_reg(0x71)
    lcd_write_data(0x02)
    lcd_write_reg(0x62)
    lcd_write_data(0x04)
    lcd_write_reg(0x72)
    lcd_write_data(0x04)
    lcd_write_reg(0x6c)
    lcd_write_data(0x29)
    lcd_write_reg(0x7c)
    lcd_write_data(0x29)
    lcd_write_reg(0x6d)
    lcd_write_data(0x31)
    lcd_write_reg(0x7d)
    lcd_write_data(0x31)
    lcd_write_reg(0x6e)
    lcd_write_data(0x0f)
    lcd_write_reg(0x7e)
    lcd_write_data(0x0f)
    lcd_write_reg(0x66)
    lcd_write_data(0x21)
    lcd_write_reg(0x76)
    lcd_write_data(0x21)
    lcd_write_reg(0x68)
    lcd_write_data(0x3A)
    lcd_write_reg(0x78)
    lcd_write_data(0x3A)
    lcd_write_reg(0x63)
    lcd_write_data(0x07)
    lcd_write_reg(0x73)
    lcd_write_data(0x07)
    lcd_write_reg(0x64)
    lcd_write_data(0x05)
    lcd_write_reg(0x74)
    lcd_write_data(0x05)
    lcd_write_reg(0x65)
    lcd_write_data(0x02)
    lcd_write_reg(0x75)
    lcd_write_data(0x02)
    lcd_write_reg(0x67)
    lcd_write_data(0x23)
    lcd_write_reg(0x77)
    lcd_write_data(0x23)
    lcd_write_reg(0x69)
    lcd_write_data(0x08)
    lcd_write_reg(0x79)
    lcd_write_data(0x08)
    lcd_write_reg(0x6a)
    lcd_write_data(0x13)
    lcd_write_reg(0x7a)
    lcd_write_data(0x13)
    lcd_write_reg(0x6b)
    lcd_write_data(0x13)
    lcd_write_reg(0x7b)
    lcd_write_data(0x13)
    lcd_write_reg(0x6f)
    lcd_write_data(0x00)
    lcd_write_reg(0x7f)
    lcd_write_data(0x00)
    lcd_write_reg(0x50)
    lcd_write_data(0x00)
    lcd_write_reg(0x52)
    lcd_write_data(0xd6)
    lcd_write_reg(0x53)
    lcd_write_data(0x08)
    lcd_write_reg(0x54)
    lcd_write_data(0x08)
    lcd_write_reg(0x55)
    lcd_write_data(0x1e)
    lcd_write_reg(0x56)
    lcd_write_data(0x1c)
    # GOA map_sel
    lcd_write_reg(0xa0)
    lcd_write_data(0x2b)
    lcd_write_data(0x24)
    lcd_write_data(0x00)
    lcd_write_reg(0xa1)
    lcd_write_data(0x87)
    lcd_write_reg(0xa2)
    lcd_write_data(0x86)
    lcd_write_reg(0xa5)
    lcd_write_data(0x00)
    lcd_write_reg(0xa6)
    lcd_write_data(0x00)
    lcd_write_reg(0xa7)
    lcd_write_data(0x00)
    lcd_write_reg(0xa8)
    lcd_write_data(0x36)
    lcd_write_reg(0xa9)
    lcd_write_data(0x7e)
    lcd_write_reg(0xaa)
    lcd_write_data(0x7e)
    lcd_write_reg(0xB9)
    lcd_write_data(0x85)
    lcd_write_reg(0xBA)
    lcd_write_data(0x84)
    lcd_write_reg(0xBB)
    lcd_write_data(0x83)
    lcd_write_reg(0xBC)
    lcd_write_data(0x82)
    lcd_write_reg(0xBD)
    lcd_write_data(0x81)
    lcd_write_reg(0xBE)
    lcd_write_data(0x80)
    lcd_write_reg(0xBF)
    lcd_write_data(0x01)
    lcd_write_reg(0xC0)
    lcd_write_data(0x02)
    lcd_write_reg(0xc1)
    lcd_write_data(0x00)
    lcd_write_reg(0xc2)
    lcd_write_data(0x00)
    lcd_write_reg(0xc3)
    lcd_write_data(0x00)
    lcd_write_reg(0xc4)
    lcd_write_data(0x33)
    lcd_write_reg(0xc5)
    lcd_write_data(0x7e)
    lcd_write_reg(0xc6)
    lcd_write_data(0x7e)
    lcd_write_reg(0xC8)
    lcd_write_data(0x33)
    lcd_write_data(0x33)
    lcd_write_reg(0xC9)
    lcd_write_data(0x68)
    lcd_write_reg(0xCA)
    lcd_write_data(0x69)
    lcd_write_reg(0xCB)
    lcd_write_data(0x6a)
    lcd_write_reg(0xCC)
    lcd_write_data(0x6b)
    lcd_write_reg(0xCD)
    lcd_write_data(0x33)
    lcd_write_data(0x33)
    lcd_write_reg(0xCE)
    lcd_write_data(0x6c)
    lcd_write_reg(0xCF)
    lcd_write_data(0x6d)
    lcd_write_reg(0xD0)
    lcd_write_data(0x6e)
    lcd_write_reg(0xD1)
    lcd_write_data(0x6f)
    lcd_write_reg(0xAB)
    lcd_write_data(0x03)
    lcd_write_data(0x67)
    lcd_write_reg(0xAC)
    lcd_write_data(0x03)
    lcd_write_data(0x6b)
    lcd_write_reg(0xAD)
    lcd_write_data(0x03)
    lcd_write_data(0x68)
    lcd_write_reg(0xAE)
    lcd_write_data(0x03)
    lcd_write_data(0x6c)
    lcd_write_reg(0xb3)
    lcd_write_data(0x00)
    lcd_write_reg(0xb4)
    lcd_write_data(0x00)
    lcd_write_reg(0xb5)
    lcd_write_data(0x00)
    lcd_write_reg(0xB6)
    lcd_write_data(0x32)
    lcd_write_reg(0xB7)
    lcd_write_data(0x7e)
    lcd_write_reg(0xB8)
    lcd_write_data(0x7e)
    lcd_write_reg(0xe0)
    lcd_write_data(0x00)
    lcd_write_reg(0xe1)
    lcd_write_data(0x03)
    lcd_write_data(0x0f)
    lcd_write_reg(0xe2)
    lcd_write_data(0x04)
    lcd_write_reg(0xe3)
    lcd_write_data(0x01)
    lcd_write_reg(0xe4)
    lcd_write_data(0x0e)
    lcd_write_reg(0xe5)
    lcd_write_data(0x01)
    lcd_write_reg(0xe6)
    lcd_write_data(0x19)
    lcd_write_reg(0xe7)
    lcd_write_data(0x10)
    lcd_write_reg(0xe8)
    lcd_write_data(0x10)
    lcd_write_reg(0xea)
    lcd_write_data(0x12)
    lcd_write_reg(0xeb)
    lcd_write_data(0xd0)
    lcd_write_reg(0xec)
    lcd_write_data(0x04)
    lcd_write_reg(0xed)
    lcd_write_data(0x07)
    lcd_write_reg(0xee)
    lcd_write_data(0x07)
    lcd_write_reg(0xef)
    lcd_write_data(0x09)
    lcd_write_reg(0xf0)
    lcd_write_data(0xd0)
    lcd_write_reg(0xf1)
    lcd_write_data(0x0e)
    lcd_write_reg(0xf9)
    lcd_write_data(0x17)
    lcd_write_reg(0xf2)
    lcd_write_data(0x2c)
    lcd_write_data(0x1b)
    lcd_write_data(0x0b)
    lcd_write_data(0x20)
    # 1 dot
    lcd_write_reg(0xe9)
    lcd_write_data(0x29)
    lcd_write_reg(0xec)
    lcd_write_data(0x04)
    # TE
    lcd_write_reg(0x35)
    lcd_write_data(0x00)
    lcd_write_reg(0x44)
    lcd_write_data(0x00)
    lcd_write_data(0x10)
    lcd_write_reg(0x46)
    lcd_write_data(0x10)
    lcd_write_reg(0xff)
    lcd_write_data(0x00)
    lcd_write_reg(0x3a)
    lcd_write_data(0x05)
    lcd_write_reg(0x36)
    if USE_HORIZONTAL == 0:
        lcd_write_data(0x00)
    elif USE_HORIZONTAL == 1:
        lcd_write_data(0xC0)
    elif USE_HORIZONTAL == 2:
        lcd_write_data(0x60)
    else:
        lcd_write_data(0xA0)
    lcd_write_reg(0x11)
    time.sleep_ms(220)
    lcd_write_reg(0x29)
    time.sleep_ms(200)

# 主程序
def main():
    print("正在初始化屏幕...")
    lcd_init()
    print("屏幕初始化完成")
    
    # 清屏为白色
    print("清屏...")
    lcd_fill(0, 0, LCD_W, LCD_H, WHITE)
    time.sleep_ms(1000)
    
    # 测试不同颜色的矩形
    print("测试不同颜色的矩形...")
    
    # 红色矩形
    print("绘制红色矩形...")
    lcd_fill(0, 0, 36, LCD_H, RED)
    time.sleep_ms(500)
    
    # 绿色矩形
    print("绘制绿色矩形...")
    lcd_fill(36, 0, 72, LCD_H, GREEN)
    time.sleep_ms(500)
    
    # 黑色矩形
    print("绘制黑色矩形...")
    lcd_fill(72, 0, 107, LCD_H, BLACK)
    time.sleep_ms(500)
    
    # 蓝色矩形
    print("绘制蓝色矩形...")
    lcd_fill(107, 0, 142, LCD_H, BLUE)
    time.sleep_ms(500)
    
    time.sleep_ms(1000)
    
    # 四象限颜色测试
    print("四象限颜色测试...")
    lcd_fill(0, 0, LCD_W // 2, LCD_H // 2, RED)
    lcd_fill(LCD_W // 2, 0, LCD_W, LCD_H // 2, GREEN)
    lcd_fill(0, LCD_H // 2, LCD_W // 2, LCD_H, BLUE)
    lcd_fill(LCD_W // 2, LCD_H // 2, LCD_W, LCD_H, WHITE)
    
    print("测试完成！")

if __name__ == "__main__":
    main()
