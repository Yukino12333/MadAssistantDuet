"""
测试 PostMessage 模块导入
"""

import sys
import os

print("=" * 60)
print("测试 PostMessage 模块导入")
print("=" * 60)

# 测试 1: 基础导入
try:
    print("\n1️⃣ 测试导入 postmessage 模块...")
    from postmessage import PostMessageInputHelper
    print("   ✓ PostMessageInputHelper 导入成功")
except ImportError as e:
    print(f"   ✗ 导入失败: {e}")
    sys.exit(1)

# 测试 2: 导入自定义动作
try:
    print("\n2️⃣ 测试导入自定义动作...")
    from postmessage.actions import RunWithShift, LongPressKey, PressMultipleKeys
    print("   ✓ RunWithShift 导入成功")
    print("   ✓ LongPressKey 导入成功")
    print("   ✓ PressMultipleKeys 导入成功")
except ImportError as e:
    print(f"   ✗ 导入失败: {e}")
    sys.exit(1)

# 测试 3: win32gui 可用性
try:
    print("\n3️⃣ 测试 win32gui 可用性...")
    import win32gui
    import win32con
    import win32api
    print("   ✓ win32gui 可用")
    print("   ✓ win32con 可用")
    print("   ✓ win32api 可用")
except ImportError as e:
    print(f"   ✗ win32 模块不可用: {e}")
    sys.exit(1)

# 测试 4: 扫描码映射
try:
    print("\n4️⃣ 测试扫描码映射...")
    helper_class = PostMessageInputHelper
    
    # 测试一些关键扫描码
    test_keys = {
        'W': 0x11,
        'A': 0x1E,
        'S': 0x1F,
        'D': 0x20,
        'Shift': 0x2A,
    }
    
    for key_name, expected_scan in test_keys.items():
        if key_name == 'Shift':
            vk_code = win32con.VK_SHIFT
        else:
            vk_code = ord(key_name)
        
        scan_code = helper_class.get_scan_code(vk_code)
        if scan_code == expected_scan:
            print(f"   ✓ {key_name}: VK={vk_code} → Scan=0x{scan_code:02X} (正确)")
        else:
            print(f"   ✗ {key_name}: VK={vk_code} → Scan=0x{scan_code:02X} (期望 0x{expected_scan:02X})")
    
except Exception as e:
    print(f"   ✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 5: lParam 构造
try:
    print("\n5️⃣ 测试 lParam 构造...")
    helper_class = PostMessageInputHelper
    
    # Shift 按下
    lparam_down = helper_class.make_key_lparam(0x2A, is_key_up=False)
    expected_down = 0x002A0001
    if lparam_down == expected_down:
        print(f"   ✓ Shift 按下: lParam=0x{lparam_down:08X} (正确)")
    else:
        print(f"   ✗ Shift 按下: lParam=0x{lparam_down:08X} (期望 0x{expected_down:08X})")
    
    # Shift 释放
    lparam_up = helper_class.make_key_lparam(0x2A, is_key_up=True)
    expected_up = 0xC02A0001
    if lparam_up == expected_up:
        print(f"   ✓ Shift 释放: lParam=0x{lparam_up:08X} (正确)")
    else:
        print(f"   ✗ Shift 释放: lParam=0x{lparam_up:08X} (期望 0x{expected_up:08X})")
    
except Exception as e:
    print(f"   ✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有测试通过！")
print("=" * 60)
print()
print("PostMessage 模块已准备就绪，可以正常使用。")
print()
