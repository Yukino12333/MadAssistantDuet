# -*- coding: utf-8 -*-
"""
设置自定义动作中的参数
"""

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import logging
import json

# 导入全局配置
from config import GAME_CONFIG

# 获取日志记录器
logger = logging.getLogger(__name__)

@AgentServer.custom_action("SetTargetWave")
class SetTargetWave(CustomAction):
    """
    设置目标波次配置
    用于保存用户选择的目标波次到全局配置中
    
    参数说明：
    {
        "target_wave": 15  // 目标波次：1-15（默认为15）
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            # 解析参数
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                logger.error(f"[SetTargetWave] 参数类型错误: {type(argv.custom_action_param)}")
                return False
            
            # 获取目标波次（默认为15）
            target_wave = params.get("target_wave", 15)
            
            # 验证波次值（必须是1-15的整数）
            if not isinstance(target_wave, int) or target_wave < 1 or target_wave > 15:
                logger.error(f"[SetTargetWave] 无效的波次值: {target_wave}，必须是1-15的整数")
                return False
            
            # 保存到全局配置
            GAME_CONFIG["target_wave"] = target_wave
            
            # 获取对应的正则表达式
            wave_regex = WAVE_REGEX_MAP.get(target_wave, "^(0?[1-9]|1[0-5])$")
            GAME_CONFIG["target_wave_regex"] = wave_regex
            
            logger.info(f"[SetTargetWave] [OK] 目标波次已设置为: {target_wave}")
            logger.info(f"[SetTargetWave] 使用正则表达式: {wave_regex}")
            logger.info(f"[SetTargetWave] 当前配置: {GAME_CONFIG}")
            
            # 强制刷新截图缓存，避免后续节点使用旧图
            logger.info(f"[SetTargetWave] 刷新截图缓存...")
            screencap_job = context.tasker.controller.post_screencap()
            screencap_job.wait()
            logger.info(f"[SetTargetWave] [OK] 截图缓存已更新")
            
            return True
            
        except Exception as e:
            logger.error(f"[SetTargetWave] 发生异常: {e}", exc_info=True)
            return False
        
@AgentServer.custom_action("SetBookOption")
class SetBookOption(CustomAction):
    """
    设置选书选项配置
    用于保存用户选择的选书选项到全局配置中
    
    参数说明：
    {
        "book_option": "不选择"  // 选书选项：["不选择", "+100%", "+200%", "+800%", "+2000%"]（默认为"不选择"）
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            # 解析参数
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                logger.error(f"[SetBookOption] 参数类型错误: {type(argv.custom_action_param)}")
                return False
            
            # 获取选书选项（默认为"不选择"）
            book_option = params.get("book_option", "不选择")
            
            # 验证选项值
            valid_options = ["不选择", "+100%", "+200%", "+800%", "+2000%"]
            if book_option not in valid_options:
                logger.error(f"[SetBookOption] 无效的选书选项: {book_option}，必须是{valid_options}之一")
                return False
            
            # 保存到全局配置
            GAME_CONFIG["book_option"] = book_option
            
            logger.info(f"[SetBookOption] [OK] 选书选项已设置为: {book_option}")
            logger.info(f"[SetBookOption] 当前配置: {GAME_CONFIG}")
            
            # 强制刷新截图缓存，避免后续节点使用旧图
            logger.info(f"[SetBookOption] 刷新截图缓存...")
            screencap_job = context.tasker.controller.post_screencap()
            screencap_job.wait()
            logger.info(f"[SetBookOption] [OK] 截图缓存已更新")
            
            return True
            
        except Exception as e:
            logger.error(f"[SetBookOption] 发生异常: {e}", exc_info=True)
            return False