"""
NV3007 LCD模块使用示例
测试所有绘制功能和framebuffer性能优化
"""

from nv3007 import NV3007
import time
from machine import Pin, SPI

# 创建屏幕实例
spi = SPI(
    0,
    baudrate=100_000_000,
    polarity=1,
    phase=1,
    bits=8,
    sck=Pin(18),
    mosi=Pin(19),
)

lcd = NV3007(spi, 17, 20, 21, 14, 142, 428, 0)

print("NV3007 LCD 完整功能测试")
print(f"屏幕分辨率: {lcd.width}x{lcd.height}")

# 测试1: 清屏和自动刷新
print("\n[测试1] 清屏为白色（自动刷新）...")
lcd.clear(NV3007.WHITE)
time.sleep_ms(1000)

# 测试2: 手动刷新模式
print("[测试2] 手动刷新模式测试...")
lcd.set_auto_flush(False)
lcd.clear(NV3007.BLACK)
lcd.draw_rect(10, 10, 50, 50, NV3007.RED)
lcd.draw_rect(80, 10, 50, 50, NV3007.GREEN)
print("调用flush()前，屏幕应该仍然是黑色...")
time.sleep_ms(1500)
print("调用flush()...")
lcd.flush()
time.sleep_ms(1000)
lcd.set_auto_flush(True)

# 测试3: 像素点
print("[测试3] 像素点测试...")
lcd.clear(NV3007.BLACK)
for i in range(10, 140, 10):
    lcd.draw_pixel(i, 10, NV3007.WHITE)
    lcd.draw_pixel(i, 418, NV3007.WHITE)
for i in range(10, 420, 10):
    lcd.draw_pixel(10, i, NV3007.RED)
    lcd.draw_pixel(132, i, NV3007.BLUE)
time.sleep_ms(1500)

# 测试4: 直线
print("[测试4] 直线测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_line(10, 10, 132, 10, NV3007.WHITE)
lcd.draw_line(10, 10, 10, 418, NV3007.RED)
lcd.draw_line(132, 10, 132, 418, NV3007.GREEN)
lcd.draw_line(10, 418, 132, 418, NV3007.BLUE)
lcd.draw_line(10, 10, 132, 418, NV3007.YELLOW)
lcd.draw_line(132, 10, 10, 418, NV3007.CYAN)
time.sleep_ms(1500)

# 测试5: 矩形（空心）
print("[测试5] 矩形（空心）测试...")
lcd.clear(NV3007.WHITE)
lcd.draw_rect(10, 10, 122, 98, NV3007.BLACK)
lcd.draw_rect(10, 120, 122, 98, NV3007.RED)
lcd.draw_rect(10, 230, 122, 98, NV3007.BLUE)
lcd.draw_rect(10, 340, 122, 78, NV3007.GREEN)
time.sleep_ms(1500)

# 测试6: 矩形（填充）
print("[测试6] 矩形（填充）测试...")
lcd.clear(NV3007.WHITE)
lcd.draw_rect(10, 10, 122, 98, NV3007.BLACK, filled=True)
lcd.draw_rect(10, 120, 122, 98, NV3007.RED, filled=True)
lcd.draw_rect(10, 230, 122, 98, NV3007.BLUE, filled=True)
lcd.draw_rect(10, 340, 122, 78, NV3007.GREEN, filled=True)
time.sleep_ms(1500)

# 测试7: 圆角矩形（空心）
print("[测试7] 圆角矩形（空心）测试...")
lcd.clear(NV3007.WHITE)
lcd.draw_rect(5, 5, 132, 98, NV3007.BLACK, radius=10)
lcd.draw_rect(5, 120, 132, 98, NV3007.RED, radius=15)
lcd.draw_rect(5, 230, 132, 98, NV3007.BLUE, radius=20)
lcd.draw_rect(5, 340, 132, 78, NV3007.GREEN, radius=5)
time.sleep_ms(1500)

# 测试8: 圆角矩形（填充）
print("[测试8] 圆角矩形（填充）测试...")
lcd.clear(NV3007.WHITE)
lcd.draw_rect(5, 5, 132, 98, NV3007.BLACK, radius=10, filled=True)
lcd.draw_rect(5, 120, 132, 98, NV3007.RED, radius=15, filled=True)
lcd.draw_rect(5, 230, 132, 98, NV3007.BLUE, radius=20, filled=True)
lcd.draw_rect(5, 340, 132, 78, NV3007.GREEN, radius=5, filled=True)
time.sleep_ms(1500)

# 测试9: 圆（空心）
print("[测试9] 圆（空心）测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_circle(71, 100, 40, NV3007.WHITE)
lcd.draw_circle(71, 220, 30, NV3007.RED)
lcd.draw_circle(35, 350, 20, NV3007.GREEN)
lcd.draw_circle(107, 350, 20, NV3007.BLUE)
time.sleep_ms(1500)

# 测试10: 圆（填充）
print("[测试10] 圆（填充）测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_circle(71, 100, 40, NV3007.WHITE, filled=True)
lcd.draw_circle(71, 220, 30, NV3007.RED, filled=True)
lcd.draw_circle(35, 350, 20, NV3007.GREEN, filled=True)
lcd.draw_circle(107, 350, 20, NV3007.BLUE, filled=True)
time.sleep_ms(1500)

# 测试11: 弧
print("[测试11] 弧测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_arc(71, 100, 40, 0, 3.14159, NV3007.WHITE)
lcd.draw_arc(71, 200, 40, 0, 1.5708, NV3007.RED)
lcd.draw_arc(71, 200, 40, 1.5708, 3.14159, NV3007.GREEN)
lcd.draw_arc(71, 300, 40, 3.14159, 4.71239, NV3007.BLUE)
lcd.draw_arc(71, 300, 40, 4.71239, 6.28318, NV3007.YELLOW)
time.sleep_ms(1500)

# 测试12: 弧（填充）
print("[测试12] 弧（填充）测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_arc(71, 100, 40, 0, 1.5708, NV3007.WHITE, filled=True)
lcd.draw_arc(71, 100, 40, 1.5708, 3.14159, NV3007.RED, filled=True)
lcd.draw_arc(71, 100, 40, 3.14159, 4.71239, NV3007.GREEN, filled=True)
lcd.draw_arc(71, 100, 40, 4.71239, 6.28318, NV3007.BLUE, filled=True)
time.sleep_ms(1500)

# 测试13: 椭圆
print("[测试13] 椭圆测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_ellipse(71, 100, 60, 30, NV3007.WHITE)
lcd.draw_ellipse(71, 200, 40, 60, NV3007.RED)
lcd.draw_ellipse(35, 350, 25, 20, NV3007.GREEN)
lcd.draw_ellipse(107, 350, 25, 20, NV3007.BLUE)
time.sleep_ms(1500)

# 测试14: 椭圆（填充）
print("[测试14] 椭圆（填充）测试...")
lcd.clear(NV3007.BLACK)
lcd.draw_ellipse(71, 100, 60, 30, NV3007.WHITE, filled=True)
lcd.draw_ellipse(71, 220, 40, 50, NV3007.RED, filled=True)
lcd.draw_ellipse(35, 370, 25, 20, NV3007.GREEN, filled=True)
lcd.draw_ellipse(107, 370, 25, 20, NV3007.BLUE, filled=True)
time.sleep_ms(1500)

# 测试15: 三角形（空心）
print("[测试15] 三角形（空心）测试...")
lcd.clear(NV3007.WHITE)
lcd.draw_triangle(71, 40, 20, 120, 122, 120, NV3007.BLACK)
lcd.draw_triangle(71, 160, 30, 250, 112, 250, NV3007.RED)
lcd.draw_triangle(35, 290, 15, 370, 55, 370, NV3007.GREEN)
lcd.draw_triangle(107, 290, 87, 370, 127, 370, NV3007.BLUE)
time.sleep_ms(1500)

# 测试16: 三角形（填充）
print("[测试16] 三角形（填充）测试...")
lcd.clear(NV3007.WHITE)
lcd.draw_triangle(71, 40, 20, 120, 122, 120, NV3007.BLACK, filled=True)
lcd.draw_triangle(71, 160, 30, 250, 112, 250, NV3007.RED, filled=True)
lcd.draw_triangle(35, 290, 15, 370, 55, 370, NV3007.GREEN, filled=True)
lcd.draw_triangle(107, 290, 87, 370, 127, 370, NV3007.BLUE, filled=True)
time.sleep_ms(1500)

# 测试17: 多边形（空心）
print("[测试17] 多边形（空心）测试...")
lcd.clear(NV3007.WHITE)
pentagon = [(71, 50), (100, 100), (90, 150), (52, 150), (42, 100)]
hexagon = [(71, 190), (90, 220), (90, 270), (71, 300), (52, 270), (52, 220)]
lcd.draw_polygon(pentagon, NV3007.BLACK)
lcd.draw_polygon(hexagon, NV3007.RED)
time.sleep_ms(1500)

# 测试18: 多边形（填充）
print("[测试18] 多边形（填充）测试...")
lcd.clear(NV3007.WHITE)
pentagon = [(71, 50), (100, 100), (90, 150), (52, 150), (42, 100)]
hexagon = [(71, 200), (90, 230), (90, 280), (71, 310), (52, 280), (52, 230)]
star = [(71, 340), (76, 355), (92, 355), (80, 365), (85, 380), (71, 372), (57, 380), (62, 365), (50, 355), (66, 355)]
lcd.draw_polygon(pentagon, NV3007.BLACK, filled=True)
lcd.draw_polygon(hexagon, NV3007.RED, filled=True)
lcd.draw_polygon(star, NV3007.BLUE, filled=True)
time.sleep_ms(1500)

# 测试19: 单色位图
print("[测试19] 单色位图测试...")
lcd.clear(NV3007.WHITE)
smiley = bytes([
    0x3C, 0x3C, 0x3C, 0x3C, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x3C, 0x3C, 0x3C, 0x3C, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])
lcd.draw_bitmap(51, 50, smiley, 8, 16, NV3007.BLACK)
lcd.draw_bitmap(51, 150, smiley, 8, 16, NV3007.RED)
lcd.draw_bitmap(51, 250, smiley, 8, 16, NV3007.BLUE)
time.sleep_ms(1500)

# 测试20: RGB565位图
print("[测试20] RGB565位图测试...")
lcd.clear(NV3007.BLACK)
color_bar = bytes()
for c in [NV3007.RED, NV3007.GREEN, NV3007.BLUE, NV3007.YELLOW, NV3007.CYAN, NV3007.MAGENTA]:
    color_bar += bytes([(c >> 8) & 0xFF, c & 0xFF])
lcd.draw_bitmap_rgb565(10, 50, color_bar, 6, 1)
for i in range(10):
    color_bar_extended = color_bar * 10
    lcd.draw_bitmap_rgb565(10, 60 + i * 10, color_bar_extended, 60, 1)
lcd.draw_bitmap_rgb565(10, 180, color_bar * 20, 120, 1)
time.sleep_ms(1500)

# 测试21: 混合绘制（性能测试）
print("[测试21] 混合绘制（性能测试）...")
lcd.set_auto_flush(False)
lcd.clear(NV3007.WHITE)
center_x = 71
center_y = 214

for r in range(5, 60, 5):
    lcd.draw_circle(center_x, center_y, r, NV3007.RED)

lcd.draw_polygon([(center_x, center_y - 70), (center_x + 50, center_y), (center_x, center_y + 70), (center_x - 50, center_y)], NV3007.BLUE, filled=True)

lcd.draw_ellipse(center_x, 80, 40, 20, NV3007.GREEN)
lcd.draw_ellipse(center_x, 350, 40, 20, NV3007.GREEN)

lcd.draw_rect(5, 5, 132, 30, NV3007.BLACK, radius=5)
lcd.draw_rect(5, 395, 132, 28, NV3007.BLACK, radius=5)

lcd.draw_line(10, 214, 132, 214, NV3007.CYAN)
lcd.draw_line(71, 50, 71, 380, NV3007.CYAN)

print("一次性刷新所有绘制内容...")
lcd.flush()
time.sleep_ms(2000)

# 测试22: 背光控制
print("[测试22] 背光控制测试...")
lcd.clear(NV3007.CYAN)
lcd.draw_rect(30, 150, 82, 128, NV3007.BLACK, filled=True)
for i in range(3):
    lcd.set_backlight(0)
    time.sleep_ms(500)
    lcd.set_backlight(1)
    time.sleep_ms(500)

# 测试23: 复杂场景
print("[测试23] 复杂场景测试...")
lcd.set_auto_flush(False)
lcd.clear(NV3007.WHITE)

# 绘制网格
for i in range(0, 142, 10):
    lcd.draw_line(i, 0, i, 428, NV3007.GRAY)
for i in range(0, 428, 10):
    lcd.draw_line(0, i, 142, i, NV3007.GRAY)

# 绘制多个圆
for i in range(3):
    for j in range(4):
        x = 30 + i * 40
        y = 50 + j * 80
        colors = [NV3007.RED, NV3007.GREEN, NV3007.BLUE]
        lcd.draw_circle(x, y, 20, colors[i], filled=True)
        lcd.draw_circle(x, y, 20, NV3007.BLACK)

# 绘制多个矩形
for i in range(2):
    for j in range(3):
        x = 20 + i * 50
        y = 380 + j * 18
        colors = [NV3007.YELLOW, NV3007.CYAN]
        lcd.draw_rect(x, y, 40, 15, colors[i], radius=3, filled=True)

lcd.flush()
time.sleep_ms(2000)

# 测试24: 大量绘制性能对比
print("[测试24] 性能对比（大量绘制）...")
import time

test_auto_start = time.ticks_ms()
lcd.set_auto_flush(True)
lcd.clear(NV3007.BLACK)
for i in range(100):
    x = (i * 13) % 142
    y = (i * 17) % 428
    lcd.draw_pixel(x, y, NV3007.WHITE)
auto_flush_time = time.ticks_diff(time.ticks_ms(), test_auto_start)
print(f"自动刷新100个像素耗时: {auto_flush_time}ms")

test_manual_start = time.ticks_ms()
lcd.set_auto_flush(False)
lcd.clear(NV3007.BLACK)
for i in range(100):
    x = (i * 13) % 142
    y = (i * 17) % 428
    lcd.draw_pixel(x, y, NV3007.WHITE)
lcd.flush()
manual_flush_time = time.ticks_diff(time.ticks_ms(), test_manual_start)
print(f"手动刷新100个像素耗时: {manual_flush_time}ms")
print(f"性能提升: {(auto_flush_time - manual_flush_time) / auto_flush_time * 100:.1f}%")

time.sleep_ms(2000)

# 测试25: 填充性能对比（优化后）
print("[测试25] 填充性能对比...")
test_fill_start = time.ticks_ms()
lcd.set_auto_flush(False)
lcd.clear(NV3007.WHITE)
pentagon = [(71, 100), (100, 150), (90, 200), (52, 200), (42, 150)]
for i in range(10):
    offset_y = i * 30
    pentagon_offseted = [(x, y + offset_y) for x, y in pentagon]
    lcd.draw_polygon(pentagon_offseted, NV3007.RED, filled=True)
lcd.flush()
fill_time = time.ticks_diff(time.ticks_ms(), test_fill_start)
print(f"扫描线算法填充10个多边形耗时: {fill_time}ms")

time.sleep_ms(2000)

# 最终清屏
print("\n所有测试完成，清屏...")
lcd.set_auto_flush(True)
lcd.clear(NV3007.WHITE)
print("所有测试通过！")
