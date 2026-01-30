"""
NV3007 LCD 绘制性能基准测试
分析各绘制操作的性能瓶颈
输出 CSV 格式便于在 Excel 中对比
"""

from nv3007 import NV3007
import font_wqy_16
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
lcd.set_font(font_wqy_16)

def benchmark(name, func, iterations=10, setup_func=None):
    """运行性能测试

    参数:
        name: 测试名称
        func: 测试函数
        iterations: 迭代次数
        setup_func: 每次迭代前的设置函数
    """
    if setup_func is None:
        setup_func = lambda: None

    # 预热
    setup_func()
    func()

    # 实际测试
    times = []
    for i in range(iterations):
        setup_func()
        start = time.ticks_ms()
        func()
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        times.append(elapsed)

    avg_time = sum(times) // iterations
    min_time = min(times)
    max_time = max(times)
    # CSV 格式输出
    print(f"{name},{avg_time},{min_time},{max_time},{iterations}")

def benchmark(name, func, iterations=10, setup_func=None):
    """运行性能测试

    参数:
        name: 测试名称
        func: 测试函数
        iterations: 迭代次数
        setup_func: 每次迭代前的设置函数
    """
    if setup_func is None:
        setup_func = lambda: None

    # 预热
    setup_func()
    func()

    # 实际测试
    times = []
    for i in range(iterations):
        setup_func()
        start = time.ticks_ms()
        func()
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        times.append(elapsed)

    avg_time = sum(times) // iterations
    min_time = min(times)
    max_time = max(times)
    # CSV 格式输出
    print(f"{name},{avg_time},{min_time},{max_time},{iterations}")

def benchmark_compare(name, func_auto, func_manual, iterations=10, setup_func=None):
    """对比自动刷新和手动刷新的性能

    参数:
        name: 测试名称
        func_auto: 自动刷新测试函数
        func_manual: 手动刷新测试函数
        iterations: 迭代次数
        setup_func: 每次迭代前的设置函数
    """
    if setup_func is None:
        setup_func = lambda: None

    # 预热
    setup_func()
    func_auto()
    setup_func()
    func_manual()

    # 测试自动刷新
    times_auto = []
    for i in range(iterations):
        setup_func()
        start = time.ticks_ms()
        func_auto()
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        times_auto.append(elapsed)

    # 测试手动刷新
    times_manual = []
    for i in range(iterations):
        setup_func()
        start = time.ticks_ms()
        func_manual()
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        times_manual.append(elapsed)

    avg_auto = sum(times_auto) // iterations
    avg_manual = sum(times_manual) // iterations
    improvement = ((avg_auto - avg_manual) / avg_auto) * 100 if avg_auto > 0 else 0

    # CSV 格式输出
    print(f"{name}(自动),{avg_auto},-,-,{iterations}")
    print(f"{name}(手动),{avg_manual},-,-,{iterations}")

print("NV3007 LCD 绘制性能基准测试")
print(f"屏幕分辨率: {lcd.width}x{lcd.height}")
# CSV 表头
print("测试名称,平均时间(ms),最小时间(ms),最大时间(ms),迭代次数")

print("\n【基础操作】")

benchmark(
    "清屏 (白色)",
    lambda: lcd.clear(NV3007.WHITE),
    iterations=5
)

benchmark(
    "清屏 (黑色)",
    lambda: lcd.clear(NV3007.BLACK),
    iterations=5
)

print("\n【像素点绘制】")

def setup_100_pixels():
    lcd.clear(NV3007.BLACK)

def test_100_pixels():
    for i in range(100):
        x = (i * 13) % lcd.width
        y = (i * 17) % lcd.height
        lcd.draw_pixel(x, y, NV3007.WHITE)

benchmark_compare(
    "绘制100个像素点",
    lambda: (lcd.set_auto_flush(True), test_100_pixels())[1],
    lambda: (lcd.set_auto_flush(False), test_100_pixels(), lcd.flush())[2],
    iterations=1,
    setup_func=setup_100_pixels
)

def setup_1000_pixels():
    lcd.clear(NV3007.BLACK)

def test_1000_pixels():
    for i in range(1000):
        x = (i * 7) % lcd.width
        y = (i * 11) % lcd.height
        lcd.draw_pixel(x, y, NV3007.WHITE)

benchmark(
    "绘制1000个像素点 (手动刷新)",
    lambda: (lcd.set_auto_flush(False), test_1000_pixels(), lcd.flush())[2],
    iterations=5,
    setup_func=setup_1000_pixels
)

print("\n【直线绘制】")

def setup_line():
    lcd.clear(NV3007.BLACK)

def test_short_line():
    for i in range(10):
        lcd.draw_line(10 + i * 10, 10, 10 + i * 10, 50, NV3007.WHITE)

def test_long_line():
    for i in range(10):
        lcd.draw_line(10, 10 + i * 10, 130, 10 + i * 10, NV3007.WHITE)

def test_diagonal_line():
    for i in range(5):
        lcd.draw_line(10, 10 + i * 80, 130, 90 + i * 80, NV3007.WHITE)

benchmark("绘制10条短直线", lambda: (lcd.set_auto_flush(False), test_short_line(), lcd.flush())[2],
          iterations=10, setup_func=setup_line)
benchmark("绘制10条长直线", lambda: (lcd.set_auto_flush(False), test_long_line(), lcd.flush())[2],
          iterations=10, setup_func=setup_line)
benchmark("绘制5条对角线", lambda: (lcd.set_auto_flush(False), test_diagonal_line(), lcd.flush())[2],
          iterations=10, setup_func=setup_line)

print("\n【矩形绘制】")

def setup_rect():
    lcd.clear(NV3007.BLACK)

def test_small_rect_hollow():
    for i in range(10):
        for j in range(10):
            lcd.draw_rect(i * 14, j * 42, 12, 40, NV3007.WHITE, filled=False)

def test_small_rect_filled():
    for i in range(10):
        for j in range(10):
            lcd.draw_rect(i * 14, j * 42, 12, 40, NV3007.WHITE, filled=True)

def test_large_rect_hollow():
    for i in range(4):
        lcd.draw_rect(10, i * 107, 122, 105, NV3007.WHITE, filled=False)

def test_large_rect_filled():
    for i in range(4):
        lcd.draw_rect(10, i * 107, 122, 105, NV3007.WHITE, filled=True)

benchmark("100个小矩形 (空心)", lambda: (lcd.set_auto_flush(False), test_small_rect_hollow(), lcd.flush())[2],
          iterations=5, setup_func=setup_rect)
benchmark("100个小矩形 (填充)", lambda: (lcd.set_auto_flush(False), test_small_rect_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_rect)
benchmark("4个大矩形 (空心)", lambda: (lcd.set_auto_flush(False), test_large_rect_hollow(), lcd.flush())[2],
          iterations=10, setup_func=setup_rect)
benchmark("4个大矩形 (填充)", lambda: (lcd.set_auto_flush(False), test_large_rect_filled(), lcd.flush())[2],
          iterations=10, setup_func=setup_rect)

print("\n【圆角矩形绘制】")

def setup_round_rect():
    lcd.clear(NV3007.BLACK)

def test_round_rect_small_radius():
    for i in range(4):
        lcd.draw_rect(10, i * 107, 122, 105, NV3007.WHITE, radius=5, filled=False)

def test_round_rect_medium_radius():
    for i in range(4):
        lcd.draw_rect(10, i * 107, 122, 105, NV3007.WHITE, radius=15, filled=False)

def test_round_rect_large_radius():
    for i in range(4):
        lcd.draw_rect(10, i * 107, 122, 105, NV3007.WHITE, radius=30, filled=False)

def test_round_rect_filled():
    for i in range(2):
        lcd.draw_rect(10, i * 214, 122, 210, NV3007.WHITE, radius=20, filled=True)

benchmark("4个圆角矩形 半径=5 (空心)", lambda: (lcd.set_auto_flush(False), test_round_rect_small_radius(), lcd.flush())[2],
          iterations=10, setup_func=setup_round_rect)
benchmark("4个圆角矩形 半径=15 (空心)", lambda: (lcd.set_auto_flush(False), test_round_rect_medium_radius(), lcd.flush())[2],
          iterations=10, setup_func=setup_round_rect)
benchmark("4个圆角矩形 半径=30 (空心)", lambda: (lcd.set_auto_flush(False), test_round_rect_large_radius(), lcd.flush())[2],
          iterations=10, setup_func=setup_round_rect)
benchmark("2个圆角矩形 半径=20 (填充)", lambda: (lcd.set_auto_flush(False), test_round_rect_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_round_rect)

print("\n【圆形绘制】")

def setup_circle():
    lcd.clear(NV3007.BLACK)

def test_small_circle_hollow():
    for i in range(5):
        for j in range(10):
            lcd.draw_circle(21 + i * 28, 21 + j * 42, 15, NV3007.WHITE, filled=False)

def test_small_circle_filled():
    for i in range(5):
        for j in range(5):
            lcd.draw_circle(21 + i * 28, 31 + j * 84, 15, NV3007.WHITE, filled=True)

def test_large_circle_hollow():
    for i in range(4):
        lcd.draw_circle(71, 54 + i * 105, 50, NV3007.WHITE, filled=False)

def test_large_circle_filled():
    for i in range(2):
        lcd.draw_circle(71, 107 + i * 214, 50, NV3007.WHITE, filled=True)

benchmark("50个小圆 (空心)", lambda: (lcd.set_auto_flush(False), test_small_circle_hollow(), lcd.flush())[2],
          iterations=5, setup_func=setup_circle)
benchmark("25个小圆 (填充)", lambda: (lcd.set_auto_flush(False), test_small_circle_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_circle)
benchmark("4个大圆 (空心)", lambda: (lcd.set_auto_flush(False), test_large_circle_hollow(), lcd.flush())[2],
          iterations=10, setup_func=setup_circle)
benchmark("2个大圆 (填充)", lambda: (lcd.set_auto_flush(False), test_large_circle_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_circle)

print("\n【弧绘制】")

def setup_arc():
    lcd.clear(NV3007.BLACK)

def test_arc_hollow():
    for i in range(5):
        lcd.draw_arc(71, 50 + i * 80, 40, 0, 3.14159, NV3007.WHITE, filled=False)

def test_arc_filled():
    for i in range(5):
        lcd.draw_arc(71, 50 + i * 80, 40, 0, 3.14159, NV3007.WHITE, filled=True)

benchmark("5个半圆弧 (空心)", lambda: (lcd.set_auto_flush(False), test_arc_hollow(), lcd.flush())[2],
          iterations=10, setup_func=setup_arc)
benchmark("5个半圆弧 (填充)", lambda: (lcd.set_auto_flush(False), test_arc_filled(), lcd.flush())[2],
          iterations=10, setup_func=setup_arc)

print("\n【椭圆绘制】")

def setup_ellipse():
    lcd.clear(NV3007.BLACK)

def test_ellipse_hollow():
    for i in range(4):
        lcd.draw_ellipse(71, 54 + i * 105, 60, 30, NV3007.WHITE, filled=False)

def test_ellipse_filled():
    for i in range(2):
        lcd.draw_ellipse(71, 107 + i * 214, 60, 30, NV3007.WHITE, filled=True)

benchmark("4个椭圆 (空心)", lambda: (lcd.set_auto_flush(False), test_ellipse_hollow(), lcd.flush())[2],
          iterations=10, setup_func=setup_ellipse)
benchmark("2个椭圆 (填充)", lambda: (lcd.set_auto_flush(False), test_ellipse_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_ellipse)

print("\n【多边形绘制】")

def setup_polygon():
    lcd.clear(NV3007.BLACK)

def test_triangle_hollow():
    for i in range(10):
        lcd.draw_triangle(71, 20 + i * 42, 20, 40 + i * 42, 122, 40 + i * 42,
                         NV3007.WHITE, filled=False)

def test_triangle_filled():
    for i in range(5):
        lcd.draw_triangle(71, 40 + i * 84, 20, 80 + i * 84, 122, 80 + i * 84,
                         NV3007.WHITE, filled=True)

def test_pentagon_hollow():
    pentagon = [(71, 30), (90, 50), (82, 80), (60, 80), (52, 50)]
    for i in range(5):
        pentagon_offseted = [(x, y + i * 84) for x, y in pentagon]
        lcd.draw_polygon(pentagon_offseted, NV3007.WHITE, filled=False)

def test_pentagon_filled():
    pentagon = [(71, 30), (90, 50), (82, 80), (60, 80), (52, 50)]
    for i in range(5):
        pentagon_offseted = [(x, y + i * 84) for x, y in pentagon]
        lcd.draw_polygon(pentagon_offseted, NV3007.WHITE, filled=True)

benchmark("10个三角形 (空心)", lambda: (lcd.set_auto_flush(False), test_triangle_hollow(), lcd.flush())[2],
          iterations=10, setup_func=setup_polygon)
benchmark("5个三角形 (填充)", lambda: (lcd.set_auto_flush(False), test_triangle_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_polygon)
benchmark("5个五边形 (空心)", lambda: (lcd.set_auto_flush(False), test_pentagon_hollow(), lcd.flush())[2],
          iterations=10, setup_func=setup_polygon)
benchmark("5个五边形 (填充)", lambda: (lcd.set_auto_flush(False), test_pentagon_filled(), lcd.flush())[2],
          iterations=5, setup_func=setup_polygon)

print("\n【位图绘制】")

def setup_bitmap():
    lcd.clear(NV3007.BLACK)

# 8x8 单色位图
bitmap_8x8 = bytes([
    0x3C, 0x3C, 0x3C, 0x3C, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x3C, 0x3C, 0x3C, 0x3C, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

def test_bitmap_8x8():
    for i in range(18):
        for j in range(53):
            lcd.draw_bitmap(i * 8, j * 8, bitmap_8x8, 8, 8, NV3007.WHITE)

# RGB565 8x8 位图
bitmap_rgb_8x8 = bytes()
for i in range(64):
    bitmap_rgb_8x8 += bytes([0x07, 0xE0])  # GREEN

def test_bitmap_rgb_8x8():
    for i in range(18):
        for j in range(53):
            lcd.draw_bitmap_rgb565(i * 8, j * 8, bitmap_rgb_8x8, 8, 8)

benchmark("954个8x8单色位图", lambda: (lcd.set_auto_flush(False), test_bitmap_8x8(), lcd.flush())[2],
          iterations=3, setup_func=setup_bitmap)
benchmark("954个8x8 RGB565位图", lambda: (lcd.set_auto_flush(False), test_bitmap_rgb_8x8(), lcd.flush())[2],
          iterations=3, setup_func=setup_bitmap)

print("\n【混合场景测试】")

def setup_mixed():
    lcd.clear(NV3007.WHITE)

def test_mixed_scene():
    center_x = 71
    center_y = 214

    # 同心圆
    for r in range(5, 60, 5):
        lcd.draw_circle(center_x, center_y, r, NV3007.RED, filled=False)

    # 菱形
    lcd.draw_polygon([(center_x, center_y - 70), (center_x + 50, center_y),
                      (center_x, center_y + 70), (center_x - 50, center_y)],
                     NV3007.BLUE, filled=True)

    # 椭圆
    lcd.draw_ellipse(center_x, 80, 40, 20, NV3007.GREEN, filled=False)
    lcd.draw_ellipse(center_x, 350, 40, 20, NV3007.GREEN, filled=False)

    # 圆角矩形
    lcd.draw_rect(5, 5, 132, 30, NV3007.BLACK, radius=5, filled=True)
    lcd.draw_rect(5, 395, 132, 28, NV3007.BLACK, radius=5, filled=True)

    # 线条
    lcd.draw_line(10, 214, 132, 214, NV3007.CYAN)
    lcd.draw_line(71, 50, 71, 380, NV3007.CYAN)

    # 三角形
    lcd.draw_triangle(35, 100, 15, 140, 55, 140, NV3007.YELLOW, filled=True)
    lcd.draw_triangle(107, 100, 87, 140, 127, 140, NV3007.YELLOW, filled=True)

benchmark("混合场景 (12个图形)", lambda: (lcd.set_auto_flush(False), test_mixed_scene(), lcd.flush())[2],
          iterations=10, setup_func=setup_mixed)

def setup_complex():
    lcd.clear(NV3007.WHITE)

def test_complex_scene():
    # 网格
    for i in range(0, 142, 10):
        lcd.draw_line(i, 0, i, 428, NV3007.GRAY)
    for i in range(0, 428, 10):
        lcd.draw_line(0, i, 142, i, NV3007.GRAY)

    # 多个圆
    for i in range(3):
        for j in range(4):
            x = 30 + i * 40
            y = 50 + j * 80
            colors = [NV3007.RED, NV3007.GREEN, NV3007.BLUE]
            lcd.draw_circle(x, y, 20, colors[i], filled=True)
            lcd.draw_circle(x, y, 20, NV3007.BLACK)

    # 多个矩形
    for i in range(2):
        for j in range(3):
            x = 20 + i * 50
            y = 380 + j * 18
            colors = [NV3007.YELLOW, NV3007.CYAN]
            lcd.draw_rect(x, y, 40, 15, colors[i], radius=3, filled=True)

    benchmark("复杂场景 (网格+12圆+6矩形)", lambda: (lcd.set_auto_flush(False), test_complex_scene(), lcd.flush())[2],
           iterations=5, setup_func=setup_complex)

print("\n【文本渲染测试】")

def setup_text():
    lcd.clear(NV3007.BLACK)

def test_text_short():
    for i in range(10):
        y = 20 + i * 40
        lcd.draw_text(10, y, "强制Viper", NV3007.WHITE)

def test_text_medium():
    for i in range(5):
        y = 20 + i * 80
        lcd.draw_text(10, y, "本地的 Viper 变量", NV3007.WHITE)

def test_text_long():
    for i in range(3):
        y = 20 + i * 130
        lcd.draw_text(10, y, "强制转换的结果将是一个本地的 Viper 变量。", NV3007.WHITE)

def test_text_multiline():
    for i in range(5):
        y = 20 + i * 80
        lcd.draw_text(10, y, "第一行", NV3007.WHITE)
        lcd.draw_text(10, y + 20, "第二行", NV3007.WHITE)
        lcd.draw_text(10, y + 40, "第三行", NV3007.WHITE)

benchmark("10次短文本(5字符)", lambda: (lcd.set_auto_flush(False), test_text_short(), lcd.flush())[2],
           iterations=5, setup_func=setup_text)
benchmark("5次中长文本(10字符)", lambda: (lcd.set_auto_flush(False), test_text_medium(), lcd.flush())[2],
           iterations=5, setup_func=setup_text)
benchmark("3次长文本(15字符)", lambda: (lcd.set_auto_flush(False), test_text_long(), lcd.flush())[2],
           iterations=5, setup_func=setup_text)
benchmark("5次多行文本(3行x5字符)", lambda: (lcd.set_auto_flush(False), test_text_multiline(), lcd.flush())[2],
           iterations=5, setup_func=setup_text)

print("\n【性能瓶颈分析】")

def analyze_pixel_operations():
    """分析单像素操作的性能"""
    lcd.clear(NV3007.BLACK)
    lcd.set_auto_flush(False)

    start = time.ticks_ms()
    for i in range(10000):
        x = i % lcd.width
        y = (i * 2) % lcd.height
        lcd._fb_set_pixel(x, y, NV3007.WHITE)
    set_pixel_time = time.ticks_diff(time.ticks_ms(), start)

    start = time.ticks_ms()
    for i in range(10000):
        x = i % lcd.width
        y = (i * 2) % lcd.height
        offset = (y * lcd._fb_width + x) * 2
        lcd._framebuffer[offset] = (NV3007.WHITE >> 8) & 0xFF
        lcd._framebuffer[offset + 1] = NV3007.WHITE & 0xFF
    direct_write_time = time.ticks_diff(time.ticks_ms(), start)

    start = time.ticks_ms()
    lcd.flush()
    flush_time = time.ticks_diff(time.ticks_ms(), start)

    print(f"10000次_fb_set_pixel,{set_pixel_time},-,-,10000")
    print(f"10000次直接写入framebuffer,{direct_write_time},-,-,10000")
    print(f"flush()完整屏幕,{flush_time},-,-,1")
    print(f"每像素设置开销,{set_pixel_time / 10000:.3f},-,-,-")
    print(f"边界检查开销,{set_pixel_time - direct_write_time:.0f},-,-,-")

    analyze_pixel_operations()

print("\n基准测试完成")

# 恢复自动刷新
lcd.set_auto_flush(True)
lcd.clear(NV3007.WHITE)
