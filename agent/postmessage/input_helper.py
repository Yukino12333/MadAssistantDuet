"""
PostMessage 输入辅助模块
封装基于 PostMessage API 的按键输入功能，支持扫描码
"""

import win32gui
import win32con
import win32api
import time
import logging
from typing import Union, List, Tuple

logger = logging.getLogger(__name__)


class PostMessageInputHelper:
    """
    PostMessage 输入辅助类
    参考 ok-script 实现，提供包含扫描码的按键输入
    """
    
    # 虚拟键码到扫描码的映射表（参考 ok-script 和 Windows 文档）
    VK_TO_SCAN_CODE = {
        # 修饰键
        win32con.VK_SHIFT: 0x2A,      # Left Shift
        win32con.VK_LSHIFT: 0x2A,     # Left Shift
        win32con.VK_RSHIFT: 0x36,     # Right Shift
        win32con.VK_CONTROL: 0x1D,    # Left Ctrl
        win32con.VK_LCONTROL: 0x1D,   # Left Ctrl
        win32con.VK_RCONTROL: 0x1D,   # Right Ctrl
        win32con.VK_MENU: 0x38,       # Left Alt
        win32con.VK_LMENU: 0x38,      # Left Alt
        win32con.VK_RMENU: 0x38,      # Right Alt
        
        # 字母键 A-Z
        ord('A'): 0x1E, ord('B'): 0x30, ord('C'): 0x2E, ord('D'): 0x20,
        ord('E'): 0x12, ord('F'): 0x21, ord('G'): 0x22, ord('H'): 0x23,
        ord('I'): 0x17, ord('J'): 0x24, ord('K'): 0x25, ord('L'): 0x26,
        ord('M'): 0x32, ord('N'): 0x31, ord('O'): 0x18, ord('P'): 0x19,
        ord('Q'): 0x10, ord('R'): 0x13, ord('S'): 0x1F, ord('T'): 0x14,
        ord('U'): 0x16, ord('V'): 0x2F, ord('W'): 0x11, ord('X'): 0x2D,
        ord('Y'): 0x15, ord('Z'): 0x2C,
        
        # 数字键 0-9
        ord('0'): 0x0B, ord('1'): 0x02, ord('2'): 0x03, ord('3'): 0x04,
        ord('4'): 0x05, ord('5'): 0x06, ord('6'): 0x07, ord('7'): 0x08,
        ord('8'): 0x09, ord('9'): 0x0A,
        
        # 功能键 F1-F12
        win32con.VK_F1: 0x3B, win32con.VK_F2: 0x3C, win32con.VK_F3: 0x3D,
        win32con.VK_F4: 0x3E, win32con.VK_F5: 0x3F, win32con.VK_F6: 0x40,
        win32con.VK_F7: 0x41, win32con.VK_F8: 0x42, win32con.VK_F9: 0x43,
        win32con.VK_F10: 0x44, win32con.VK_F11: 0x57, win32con.VK_F12: 0x58,
        
        # 特殊键
        win32con.VK_ESCAPE: 0x01,
        win32con.VK_SPACE: 0x39,
        win32con.VK_RETURN: 0x1C,
        win32con.VK_BACK: 0x0E,
        win32con.VK_TAB: 0x0F,
        win32con.VK_CAPITAL: 0x3A,
        
        # 方向键
        win32con.VK_LEFT: 0x4B,
        win32con.VK_RIGHT: 0x4D,
        win32con.VK_UP: 0x48,
        win32con.VK_DOWN: 0x50,
        
        # 其他常用键
        win32con.VK_INSERT: 0x52,
        win32con.VK_DELETE: 0x53,
        win32con.VK_HOME: 0x47,
        win32con.VK_END: 0x4F,
        win32con.VK_PRIOR: 0x49,  # Page Up
        win32con.VK_NEXT: 0x51,   # Page Down
    }
    
    def __init__(self, hwnd: int):
        """
        初始化 PostMessage 输入辅助类
        
        Args:
            hwnd: 目标窗口句柄
        """
        self.hwnd = hwnd
        self.activated = False
        
        logger.info(f"[PostMessageInputHelper] 初始化，窗口句柄: {hwnd}")
    
    @classmethod
    def get_scan_code(cls, vk_code: int) -> int:
        """
        获取虚拟键码对应的扫描码
        
        Args:
            vk_code: 虚拟键码
            
        Returns:
            扫描码
        """
        # 先查找预定义映射表
        if vk_code in cls.VK_TO_SCAN_CODE:
            return cls.VK_TO_SCAN_CODE[vk_code]
        
        # 使用 Windows API 动态获取扫描码
        scan_code = win32api.MapVirtualKey(vk_code, 0)  # MAPVK_VK_TO_VSC = 0
        if scan_code == 0:
            logger.warning(f"无法获取 VK={vk_code} 的扫描码，使用默认值 0x1E")
            return 0x1E  # 默认使用 A 键的扫描码
        
        return scan_code
    
    @staticmethod
    def make_key_lparam(scan_code: int, is_key_up: bool = False) -> int:
        """
        构造包含扫描码的 lParam
        
        lParam 结构 (32位):
        - Bits 0-15:  Repeat count (通常为 1)
        - Bits 16-23: Scan code (硬件扫描码)
        - Bit 24:     Extended key flag
        - Bits 25-28: Reserved
        - Bit 29:     Context code
        - Bit 30:     Previous key state (按下前的状态)
        - Bit 31:     Transition state (0=按下, 1=释放)
        
        Args:
            scan_code: 扫描码
            is_key_up: 是否为按键释放
            
        Returns:
            lParam 值
        """
        lparam = 1  # Repeat count = 1
        lparam |= (scan_code << 16)  # 设置扫描码 (位 16-23)
        
        if is_key_up:
            lparam |= (1 << 30)  # Previous state = 1 (之前是按下状态)
            lparam |= (1 << 31)  # Transition state = 1 (释放)
        
        return lparam
    
    def try_activate(self):
        """尝试激活窗口（仅在首次使用时）"""
        if not self.activated:
            foreground = win32gui.GetForegroundWindow()
            if foreground != self.hwnd:
                self.activated = True
                self.activate()
    
    def activate(self):
        """发送窗口激活消息"""
        win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        logger.debug(f"[PostMessageInputHelper] 发送 WM_ACTIVATE 到窗口 {self.hwnd}")
    
    def key_down(self, vk_code: int, activate: bool = True):
        """
        按下按键
        
        Args:
            vk_code: 虚拟键码
            activate: 是否先激活窗口
        """
        if activate:
            self.try_activate()
        
        scan_code = self.get_scan_code(vk_code)
        lparam = self.make_key_lparam(scan_code, is_key_up=False)
        
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk_code, lparam)
        
        logger.debug(f"[PostMessageInputHelper] key_down: VK={vk_code}, "
                    f"ScanCode=0x{scan_code:02X}, lParam=0x{lparam:08X}")
    
    def key_up(self, vk_code: int):
        """
        释放按键
        
        Args:
            vk_code: 虚拟键码
        """
        scan_code = self.get_scan_code(vk_code)
        lparam = self.make_key_lparam(scan_code, is_key_up=True)
        
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vk_code, lparam)
        
        logger.debug(f"[PostMessageInputHelper] key_up: VK={vk_code}, "
                    f"ScanCode=0x{scan_code:02X}, lParam=0x{lparam:08X}")
    
    def press_key(self, vk_code: int, duration: float = 0.05):
        """
        按下并释放按键
        
        Args:
            vk_code: 虚拟键码
            duration: 按住时长（秒）
        """
        self.key_down(vk_code)
        time.sleep(duration)
        self.key_up(vk_code)
    
    def long_press_key(self, vk_code: int, duration: float):
        """
        长按按键
        
        Args:
            vk_code: 虚拟键码
            duration: 持续时长（秒）
        """
        logger.info(f"[PostMessageInputHelper] 长按键 VK={vk_code}, 持续 {duration:.2f}秒")
        self.key_down(vk_code)
        time.sleep(duration)
        self.key_up(vk_code)
    
    def press_multiple_keys(self, vk_codes: List[int], duration: float):
        """
        同时按下多个按键并保持指定时长
        
        Args:
            vk_codes: 虚拟键码列表
            duration: 持续时长（秒）
        """
        logger.info(f"[PostMessageInputHelper] 同时按下 {len(vk_codes)} 个键，持续 {duration:.2f}秒")
        logger.debug(f"  按键列表: {vk_codes}")
        
        # 按下所有键
        for vk in vk_codes:
            self.key_down(vk, activate=(vk == vk_codes[0]))  # 只在第一个键时激活
        
        # 保持持续时长
        time.sleep(duration)
        
        # 释放所有键
        for vk in vk_codes:
            self.key_up(vk)
    
    def sequential_press(self, key_sequence: List[Tuple[int, float]], hold_duration: float):
        """
        顺序按下多个按键，最后一起释放
        
        Args:
            key_sequence: 按键序列 [(vk_code, delay_before), ...]
            hold_duration: 所有键按下后的保持时长（秒）
        """
        logger.info(f"[PostMessageInputHelper] 顺序按下 {len(key_sequence)} 个键")
        
        pressed_keys = []
        
        try:
            # 按顺序按下所有键
            for i, (vk_code, delay) in enumerate(key_sequence):
                if delay > 0:
                    logger.debug(f"  等待 {delay:.3f}秒...")
                    time.sleep(delay)
                
                logger.debug(f"  按下键 {i+1}/{len(key_sequence)}: VK={vk_code}")
                self.key_down(vk_code, activate=(i == 0))
                pressed_keys.append(vk_code)
            
            # 保持按下状态
            logger.debug(f"  保持 {hold_duration:.2f}秒...")
            time.sleep(hold_duration)
            
            # 释放所有键
            logger.debug(f"  释放所有键...")
            for vk_code in pressed_keys:
                self.key_up(vk_code)
            
            logger.info(f"[PostMessageInputHelper] ✓ 完成顺序按键")
            
        except Exception as e:
            logger.error(f"[PostMessageInputHelper] 顺序按键失败: {e}", exc_info=True)
            # 尝试释放所有已按下的键
            for vk_code in pressed_keys:
                try:
                    self.key_up(vk_code)
                except:
                    pass
            raise
    
    @staticmethod
    def char_to_vk(char: str) -> int:
        """
        将字符转换为虚拟键码
        
        Args:
            char: 单个字符
            
        Returns:
            虚拟键码
        """
        if len(char) != 1:
            raise ValueError(f"char 必须是单个字符，当前: {char}")
        
        char = char.upper()
        return ord(char)
    
    @staticmethod
    def get_direction_vk(direction: str) -> int:
        """
        获取方向键的虚拟键码（支持 WASD 和方向键）
        
        Args:
            direction: 方向字符 ('w', 'a', 's', 'd' 或 'up', 'down', 'left', 'right')
            
        Returns:
            虚拟键码
        """
        direction = direction.lower()
        
        direction_map = {
            'w': ord('W'),
            'a': ord('A'),
            's': ord('S'),
            'd': ord('D'),
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
        }
        
        if direction not in direction_map:
            raise ValueError(f"不支持的方向: {direction}")
        
        return direction_map[direction]
