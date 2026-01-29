"""
NV3007 LCD模块使用示例
演示各种绘制功能
"""

from nv3007 import NV3007, create
import time

# 创建屏幕实例（使用默认引脚配置）
lcd = create()

print("NV3007 LCD 示例程序")
print(f"屏幕分辨率: {lcd.width}x{lcd.height}")

# 测试1: 清屏
print("\n[测试1] 清屏为白色...")
lcd.clear(NV3007.WHITE)
time.sleep_ms(1000)

# 测试2: 填充不同颜色的矩形
print("[测试2] 绘制不同颜色的矩形...")
lcd.fill(0, 0, 36, lcd.height, NV3007.RED)
lcd.fill(36, 0, 36, lcd.height, NV3007.GREEN)
lcd.fill(72, 0, 35, lcd.height, NV3007.BLUE)
lcd.fill(107, 0, 35, lcd.height, NV3007.YELLOW)
time.sleep_ms(2000)

# 测试3: 四象限颜色
print("[测试3] 四象限颜色测试...")
lcd.fill(0, 0, lcd.width // 2, lcd.height // 2, NV3007.RED)
lcd.fill(lcd.width // 2, 0, lcd.width // 2, lcd.height // 2, NV3007.GREEN)
lcd.fill(0, lcd.height // 2, lcd.width // 2, lcd.height // 2, NV3007.BLUE)
lcd.fill(lcd.width // 2, lcd.height // 2, lcd.width // 2, lcd.height // 2, NV3007.WHITE)
time.sleep_ms(2000)

# 测试4: 画点
print("[测试4] 画点测试...")
lcd.clear(NV3007.BLACK)
for i in range(10, 140, 10):
    lcd.pixel(i, 10, NV3007.WHITE)
    lcd.pixel(i, 418, NV3007.WHITE)
for i in range(10, 420, 10):
    lcd.pixel(10, i, NV3007.WHITE)
    lcd.pixel(132, i, NV3007.WHITE)
time.sleep_ms(2000)

# 测试5: 画线
print("[测试5] 画线测试...")
lcd.clear(NV3007.BLACK)
lcd.line(10, 10, 132, 10, NV3007.WHITE)
lcd.line(10, 10, 10, 418, NV3007.RED)
lcd.line(132, 10, 132, 418, NV3007.GREEN)
lcd.line(10, 418, 132, 418, NV3007.BLUE)
lcd.line(10, 10, 132, 418, NV3007.YELLOW)
lcd.line(132, 10, 10, 418, NV3007.CYAN)
time.sleep_ms(2000)

# 测试6: 矩形
print("[测试6] 矩形测试...")
lcd.clear(NV3007.WHITE)
lcd.rect(10, 10, 120, 100, NV3007.BLACK)
lcd.fill_rect(20, 20, 100, 80, NV3007.RED)
lcd.rect(10, 120, 120, 100, NV3007.BLACK)
lcd.fill_rect(20, 130, 100, 80, NV3007.GREEN)
lcd.rect(10, 230, 120, 100, NV3007.BLACK)
lcd.fill_rect(20, 240, 100, 80, NV3007.BLUE)
time.sleep_ms(2000)

# 测试7: 圆形
print("[测试7] 圆形测试...")
lcd.clear(NV3007.BLACK)
lcd.circle(71, 214, 30, NV3007.WHITE)
lcd.fill_circle(71, 150, 20, NV3007.RED)
lcd.fill_circle(35, 300, 15, NV3007.GREEN)
lcd.fill_circle(107, 300, 15, NV3007.BLUE)
lcd.circle(71, 380, 10, NV3007.YELLOW)
time.sleep_ms(2000)

# 测试8: 三角形
print("[测试8] 三角形测试...")
lcd.clear(NV3007.WHITE)
lcd.triangle(71, 50, 20, 150, 122, 150, NV3007.BLACK)
lcd.fill_rect(30, 160, 82, 1, NV3007.BLACK)
lcd.triangle(71, 200, 30, 300, 112, 300, NV3007.RED, filled=True)
lcd.triangle(35, 350, 15, 400, 55, 400, NV3007.GREEN, filled=True)
lcd.triangle(107, 350, 87, 400, 127, 400, NV3007.BLUE, filled=True)
time.sleep_ms(2000)

# 测试9: 背光控制
print("[测试9] 背光控制测试...")
lcd.clear(NV3007.CYAN)
lcd.fill_rect(30, 150, 82, 130, NV3007.BLACK)
for i in range(3):
    lcd.set_backlight(0)
    time.sleep_ms(500)
    lcd.set_backlight(1)
    time.sleep_ms(500)

# 测试10: 绘制复杂图形
print("[测试10] 复杂图形测试...")
lcd.clear(NV3007.BLACK)
center_x = 71
center_y = 214

# 绘制同心圆
for r in range(5, 100, 10):
    lcd.circle(center_x, center_y, r, NV3007.WHITE)

# 绘制四角装饰
lcd.fill_rect(5, 5, 20, 20, NV3007.RED)
lcd.fill_rect(117, 5, 20, 20, NV3007.GREEN)
lcd.fill_rect(5, 403, 20, 20, NV3007.BLUE)
lcd.fill_rect(117, 403, 20, 20, NV3007.YELLOW)

time.sleep_ms(3000)

# 最终清屏
print("\n测试完成，清屏...")
lcd.clear(NV3007.WHITE)
print("所有测试完成！")
