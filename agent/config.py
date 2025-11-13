"""
全局配置模块

定义游戏相关的全局配置，避免循环导入问题。
"""

import win32con

GAME_CONFIG = {
    "dodge_key": win32con.VK_RBUTTON,  # 默认闪避键为 右键 (0x02)
    "auto_battle_mode": 0,  # 自动战斗模式：0=循环按E键, 1=什么也不做
    "battle_rounds": 3,  # 战斗轮数
    # 新增：自动E周期与单轮战斗超时（毫秒）
    "auto_e_interval_ms": 5000,
    "round_timeout_ms": 200000
}