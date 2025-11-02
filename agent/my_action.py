from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import time
import logging
import json

# 获取日志记录器
logger = logging.getLogger(__name__)


@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        logger.info("my_action_111 is running!")

        return True


@AgentServer.custom_action("LongPressWithTimeoutDetection")
class LongPressWithTimeoutDetection(CustomAction):
    """
    循环检测目标文字，支持超时处理和中断动作
    当未检测到目标时，执行中断动作（自动战斗）
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        # 从参数中获取配置
        # custom_action_param 是 JSON 字符串，需要解析为字典
        try:
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                logger.error(f"[LongPressWithTimeoutDetection] 参数类型错误: {type(argv.custom_action_param)}")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"[LongPressWithTimeoutDetection] JSON 解析失败: {e}")
            logger.error(f"  参数内容: {argv.custom_action_param}")
            return False
        
        check_interval = params.get("check_interval", 1000)  # 检测间隔
        total_timeout = params.get("total_timeout", 180000)  # 总超时时间 180s
        target_node = params.get("target_node", "again_for_win")  # 要检测的目标节点
        interrupt_node = params.get("interrupt_node", "autoBattle_for_win")  # 未检测到时的候补节点
        
        logger.info("=" * 50)
        logger.info("[LongPressWithTimeoutDetection] 开始战斗循环检测")
        logger.info(f"  检测间隔: {check_interval}ms, 总超时: {total_timeout}ms")
        logger.info(f"  目标节点: {target_node}, 中断节点: {interrupt_node}")
        
        try:
            # 开始循环检测目标节点
            start_time = time.time()
            loop_count = 0
            
            while True:
                loop_count += 1
                elapsed = (time.time() - start_time) * 1000  # 已经过的时间（毫秒）
                
                # 检查是否超时
                if elapsed >= total_timeout:
                    logger.warning(f"[LongPressWithTimeoutDetection] 超时 {total_timeout}ms，跳转到 on_error")
                    logger.info(f"  总循环次数: {loop_count}")
                    return False
                
                # 尝试检测目标节点
                logger.info(f"[LongPressWithTimeoutDetection] 第 {loop_count} 次检测 '{target_node}'... (已用时: {int(elapsed)}ms / {total_timeout}ms)")
                
                # 获取最新截图
                sync_job = context.tasker.controller.post_screencap()
                sync_job.wait()
                image = context.tasker.controller.cached_image  # 这是属性,不是方法
                
                # 运行目标节点的识别
                reco_result = context.run_recognition(target_node, image)
                
                # 检查识别结果是否有效（有 box 说明识别到了）
                if reco_result and reco_result.box and len(reco_result.box) == 4:
                    logger.info(f"[LongPressWithTimeoutDetection] ✓ 检测到 '{target_node}'，box={reco_result.box}")
                    logger.info(f"  总循环次数: {loop_count}, 总用时: {int(elapsed)}ms")
                    # 动态设置 next 节点
                    context.override_next(argv.node_name, [target_node])
                    return True
                else:
                    logger.info(f"[LongPressWithTimeoutDetection] ✗ 未检测到 '{target_node}'，执行 interrupt '{interrupt_node}'")
                    
                    # 直接执行 interrupt 节点的动作（按 E 键）
                    try:
                        # 获取 interrupt_node 的配置并执行
                        click_job = context.tasker.controller.post_click_key(69)  # E 键
                        click_job.wait()
                        logger.info(f"[LongPressWithTimeoutDetection] → 执行了按键 E (自动战斗)")
                        
                        # 等待 interrupt 节点的 post_delay
                        logger.info(f"[LongPressWithTimeoutDetection] → 等待 8 秒...")
                        time.sleep(8)  # autoBattle_for_win 的 post_delay 是 8000ms
                        
                    except Exception as e:
                        logger.error(f"[LongPressWithTimeoutDetection] 执行 interrupt 节点出错: {e}", exc_info=True)
                    
                    # 等待检测间隔
                    logger.info(f"[LongPressWithTimeoutDetection] → 等待检测间隔 {check_interval}ms...")
                    time.sleep(check_interval / 1000.0)
                    
        except Exception as e:
            logger.error(f"[LongPressWithTimeoutDetection] 发生异常: {e}", exc_info=True)
            return False
