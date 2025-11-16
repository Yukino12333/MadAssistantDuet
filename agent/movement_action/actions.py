"""
自定义按键动作 - 精简版本
只保留LongPressKey，移除其他复杂动作
"""

import json
import logging
import time
from maa.custom_action import CustomAction
from maa.context import Context
from maa.agent.agent_server import AgentServer

logger = logging.getLogger(__name__)

@AgentServer.custom_action("LongPressKey")
class LongPressKey(CustomAction):
    """
    长按单个按键
    
    参数说明：
    {
        "key": "w",           // 按键：字符或虚拟键码
        "duration": 2.0       // 持续时长（秒）
    }
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        # 解析参数
        try:
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                logger.error(f"[LongPressKey] 参数类型错误: {type(argv.custom_action_param)}")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"[LongPressKey] JSON 解析失败: {e}")
            return False
        
        # 获取参数
        key = params.get("key")
        duration = params.get("duration", 1.0)
        
        if not key:
            logger.error("[LongPressKey] 缺少参数 'key'")
            return False
        
        logger.info(f"[LongPressKey] 长按键 '{key}' 持续 {duration:.2f}秒")
        
        try:
            controller = context.tasker.controller
            
            # 按键虚拟键码映射
            key_mapping = {
                'w': 87, 'a': 65, 's': 83, 'd': 68,
                'W': 87, 'A': 65, 'S': 83, 'D': 68,
                'space': 32, 'esc': 27, 'f': 70, 'e': 69
            }
            
            if isinstance(key, int):
                vk_code = key
            elif isinstance(key, str) and key in key_mapping:
                vk_code = key_mapping[key]
            else:
                logger.error(f"[LongPressKey] 不支持的键: {key}")
                return False

            # 执行长按操作
            controller.post_key_down(vk_code).wait()
            time.sleep(duration)
            controller.post_key_up(vk_code).wait()
            
            logger.info(f"[LongPressKey] [OK] 完成长按")
            return True
            
        except Exception as e:
            logger.error(f"[LongPressKey] 发生异常: {e}", exc_info=True)
            return False
