"""
PostMessage 输入模块
提供基于 PostMessage API 的按键输入功能，支持扫描码
"""

from .input_helper import PostMessageInputHelper
from .actions import GameWindowAction, RunWithShift, LongPressKey, PressMultipleKeys

__all__ = [
    'PostMessageInputHelper',
    'GameWindowAction',
    'RunWithShift',
    'LongPressKey',
    'PressMultipleKeys',
]
