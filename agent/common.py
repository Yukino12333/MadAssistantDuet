# -*- coding: utf-8 -*-
"""
通用自定义动作模块
包含选书相关的自定义 Action
"""

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import logging

# 导入全局配置
from config import GAME_CONFIG

# 获取日志记录器
logger = logging.getLogger(__name__)

@AgentServer.custom_action("SelectBookByOption")
class SelectBookByOption(CustomAction):
    """
    根据全局配置中的选书选项执行选书操作
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            # 从全局配置获取选书选项
            book_option = GAME_CONFIG.get("book_option", "不选择")
            logger.info(f"[SelectBookByOption] 开始选书，选项: {book_option}")
            
            # 根据选书选项执行不同的点击操作
            controller = context.tasker.controller
            
            if book_option == "不选择":
                logger.info("[SelectBookByOption] 不选择书，直接跳过")
                return True
            elif book_option == "+100%":
                # 点击 +100% 书的位置
                logger.info("[SelectBookByOption] 选择 +100% 书")
                click_job = controller.post_click(521, 334)
                click_job.wait()
            elif book_option == "+200%":
                # 点击 +200% 书的位置
                logger.info("[SelectBookByOption] 选择 +200% 书")
                click_job = controller.post_click(647, 327)
                click_job.wait()
            elif book_option == "+800%":
                # 点击 +800% 书的位置
                logger.info("[SelectBookByOption] 选择 +800% 书")
                click_job = controller.post_click(763, 337)
                click_job.wait()
            elif book_option == "+2000%":
                # 点击 +2000% 书的位置
                logger.info("[SelectBookByOption] 选择 +2000% 书")
                click_job = controller.post_click(878, 330)
                click_job.wait()
            else:
                logger.error(f"[SelectBookByOption] 未知的选书选项: {book_option}")
                return False
            
            logger.info(f"[SelectBookByOption] [OK] 已选择: {book_option}")
            return True
            
        except Exception as e:
            logger.error(f"[SelectBookByOption] 发生异常: {e}", exc_info=True)
            return False