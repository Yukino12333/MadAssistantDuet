from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import time
import logging
import json

# 导入 PostMessage 相关的自定义动作
from postmessage.actions import RunWithShift, LongPressKey, PressMultipleKeys, RunWithJump

# 获取日志记录器
logger = logging.getLogger(__name__)


@AgentServer.custom_action("SetDodgeKey")
class SetDodgeKey(CustomAction):
    """
    设置闪避键配置
    用于保存用户选择的闪避键到全局配置中
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
                logger.error(f"[SetDodgeKey] 参数类型错误: {type(argv.custom_action_param)}")
                return False
            
            # 获取闪避键虚拟键码(现在直接是 int)
            dodge_key_vk = params.get("dodge_key", 0x10)  # 默认 Shift = 0x10
            
            # 导入 main 模块以访问全局配置
            import main
            
            # 保存到全局配置
            main.GAME_CONFIG["dodge_key"] = dodge_key_vk
            
            logger.info(f"[SetDodgeKey] [OK] 闪避键已设置为: VK=0x{dodge_key_vk:02X} ({dodge_key_vk})")
            logger.info(f"[SetDodgeKey] 当前配置: {main.GAME_CONFIG}")
            
            # 强制刷新截图缓存，避免后续节点使用旧图
            logger.info(f"[SetDodgeKey] 刷新截图缓存...")
            screencap_job = context.tasker.controller.post_screencap()
            screencap_job.wait()
            logger.info(f"[SetDodgeKey] [OK] 截图缓存已更新")
            
            return True
            
        except Exception as e:
            logger.error(f"[SetDodgeKey] 发生异常: {e}", exc_info=True)
            return False


@AgentServer.custom_action("SetAutoBattleMode")
class SetAutoBattleMode(CustomAction):
    """
    设置自动战斗模式配置
    用于保存用户选择的自动战斗模式到全局配置中
    
    参数说明：
    {
        "auto_battle_mode": 0  // 自动战斗模式：0=循环按E键（默认）, 1=什么也不做
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
                logger.error(f"[SetAutoBattleMode] 参数类型错误: {type(argv.custom_action_param)}")
                return False
            
            # 获取自动战斗模式（默认为 0）
            auto_battle_mode = params.get("auto_battle_mode", 0)
            
            # 验证模式值
            if auto_battle_mode not in [0, 1]:
                logger.error(f"[SetAutoBattleMode] 无效的模式值: {auto_battle_mode}，仅支持 0 或 1")
                return False
            
            # 导入 main 模块以访问全局配置
            import main
            
            # 保存到全局配置
            main.GAME_CONFIG["auto_battle_mode"] = auto_battle_mode
            
            mode_desc = "循环按E键" if auto_battle_mode == 0 else "什么也不做"
            logger.info(f"[SetAutoBattleMode] [OK] 自动战斗模式已设置为: {auto_battle_mode} ({mode_desc})")
            logger.info(f"[SetAutoBattleMode] 当前配置: {main.GAME_CONFIG}")
            
            # 强制刷新截图缓存，避免后续节点使用旧图
            logger.info(f"[SetAutoBattleMode] 刷新截图缓存...")
            screencap_job = context.tasker.controller.post_screencap()
            screencap_job.wait()
            logger.info(f"[SetAutoBattleMode] [OK] 截图缓存已更新")
            
            return True
            
        except Exception as e:
            logger.error(f"[SetAutoBattleMode] 发生异常: {e}", exc_info=True)
            return False


@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        logger.info("my_action_111 is running!")

        return True




@AgentServer.custom_action("LongPressMultipleKeys")
class LongPressMultipleKeys(CustomAction):
    """
    同时长按多个按键
    支持同时按下多个键并保持指定时长
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        # 从参数中获取配置
        try:
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                logger.error(f"[LongPressMultipleKeys] 参数类型错误: {type(argv.custom_action_param)}")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"[LongPressMultipleKeys] JSON 解析失败: {e}")
            logger.error(f"  参数内容: {argv.custom_action_param}")
            return False
        
        # 获取参数
        keys = params.get("keys", [])  # 按键列表
        duration = params.get("duration", 1000)  # 持续时间（毫秒）
        
        if not keys or not isinstance(keys, list):
            logger.error(f"[LongPressMultipleKeys] 参数错误: keys 必须是非空列表，当前值: {keys}")
            return False
        
        logger.info("=" * 50)
        logger.info(f"[LongPressMultipleKeys] 开始同时长按多个按键")
        logger.info(f"  按键列表: {keys} (数量: {len(keys)})")
        logger.info(f"  持续时长: {duration}ms ({duration/1000:.1f}秒)")
        
        try:
            # 1. 按下所有键
            logger.info(f"[LongPressMultipleKeys] 步骤 1: 按下所有键...")
            down_jobs = []
            for key in keys:
                logger.info(f"  -> 按下键: {key}")
                job = context.tasker.controller.post_key_down(key)
                down_jobs.append(job)
            
            # 等待所有按键操作完成
            # for job in down_jobs:
            #     job.wait()
            
            # 2. 保持按下状态指定时长
            logger.info(f"[LongPressMultipleKeys] 步骤 2: 保持 {duration}ms...")
            time.sleep(duration / 1000.0)
            
            # 3. 释放所有键
            logger.info(f"[LongPressMultipleKeys] 步骤 3: 释放所有键...")
            up_jobs = []
            for key in keys:
                logger.info(f"  -> 释放键: {key}")
                job = context.tasker.controller.post_key_up(key)
                up_jobs.append(job)
            
            # 等待所有释放操作完成
            # for job in up_jobs:
            #     job.wait()
            
            logger.info(f"[LongPressMultipleKeys] [OK] 完成！同时长按 {len(keys)} 个键共 {duration}ms")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"[LongPressMultipleKeys] 发生异常: {e}", exc_info=True)
            return False


@AgentServer.custom_action("SequentialLongPress")
class SequentialLongPress(CustomAction):
    """
    顺序按下多个按键并长按，最后一起释放
    适用于需要先后按下不同键并保持的场景（如：先移动再冲刺）
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        # 从参数中获取配置
        try:
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                logger.error(f"[SequentialLongPress] 参数类型错误: {type(argv.custom_action_param)}")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"[SequentialLongPress] JSON 解析失败: {e}")
            logger.error(f"  参数内容: {argv.custom_action_param}")
            return False
        
        # 获取参数
        key_sequence = params.get("key_sequence", [])  # 按键序列: [{key: 65, delay: 500}, ...]
        hold_duration = params.get("hold_duration", 1000)  # 保持时长（毫秒）
        
        if not key_sequence or not isinstance(key_sequence, list):
            logger.error(f"[SequentialLongPress] 参数错误: key_sequence 必须是非空列表")
            return False
        
        logger.info("=" * 50)
        logger.info(f"[SequentialLongPress] 开始顺序长按按键")
        logger.info(f"  按键序列: {key_sequence}")
        logger.info(f"  保持时长: {hold_duration}ms ({hold_duration/1000:.1f}秒)")
        
        try:
            pressed_keys = []  # 记录已按下的键
            
            # 步骤 1: 按顺序按下所有键
            logger.info(f"[SequentialLongPress] 步骤 1: 按顺序按下所有键...")
            for i, key_info in enumerate(key_sequence):
                key = key_info.get("key")
                delay = key_info.get("delay", 0)  # 按下此键前的延迟（毫秒）
                
                if delay > 0:
                    logger.info(f"  -> 等待 {delay}ms...")
                    time.sleep(delay / 1000.0)
                
                logger.info(f"  -> 按下键 {i+1}/{len(key_sequence)}: {key}")
                context.tasker.controller.post_key_down(key)
                pressed_keys.append(key)
            
            # 步骤 2: 保持所有键按下状态
            logger.info(f"[SequentialLongPress] 步骤 2: 保持所有键按下 {hold_duration}ms...")
            time.sleep(hold_duration / 1000.0)
            
            # 步骤 3: 一起释放所有键
            logger.info(f"[SequentialLongPress] 步骤 3: 释放所有键...")
            for key in pressed_keys:
                logger.info(f"  -> 释放键: {key}")
                context.tasker.controller.post_key_up(key)
            
            logger.info(f"[SequentialLongPress] [OK] 完成！顺序按下 {len(pressed_keys)} 个键，保持 {hold_duration}ms")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"[SequentialLongPress] 发生异常: {e}", exc_info=True)
            # 尝试释放所有已按下的键
            logger.info("[SequentialLongPress] 尝试释放所有已按下的键...")
            for key in pressed_keys:
                try:
                    context.tasker.controller.post_key_up(key)
                except:
                    pass
            return False


# ========== PostMessage 按键输入动作（支持扫描码） ==========

@AgentServer.custom_action("RunWithShift")
class RunWithShiftAction(RunWithShift):
    """
    奔跑动作：先按下方向键，再按下 Shift，保持指定时长
    使用 PostMessage + 扫描码实现，兼容性更好
    
    参数示例：
    {
        "direction": "w",      // 方向键：'w', 'a', 's', 'd' 或 'up', 'down', 'left', 'right'
        "duration": 2.0,       // 持续时长（秒）
        "shift_delay": 0.05    // 按下方向键后，多久按下 Shift（秒），默认 0.05
    }
    """
    pass


@AgentServer.custom_action("LongPressKey")
class LongPressKeyAction(LongPressKey):
    """
    长按单个按键
    使用 PostMessage + 扫描码实现
    
    参数示例：
    {
        "key": "w",           // 按键：字符或虚拟键码
        "duration": 2.0       // 持续时长（秒）
    }
    """
    pass


@AgentServer.custom_action("PressMultipleKeys")
class PressMultipleKeysAction(PressMultipleKeys):
    """
    同时按下多个按键
    使用 PostMessage + 扫描码实现
    
    参数示例：
    {
        "keys": ["w", "shift"],  // 按键列表
        "duration": 2.0          // 持续时长（秒）
    }
    """
    pass


@AgentServer.custom_action("RunWithJump")
class RunWithJumpAction(RunWithJump):
    """
    边跑边跳动作：先按下方向键，延迟后按下闪避键（奔跑），然后周期性短按空格键（跳跃）
    使用 PostMessage + 扫描码实现
    
    参数示例：
    {
        "direction": "w",        // 方向键：'w', 'a', 's', 'd' 或 'up', 'down', 'left', 'right'
        "duration": 3.0,         // 总持续时长（秒）
        "dodge_delay": 0.05,     // 按下方向键后，多久按下闪避键（秒），默认 0.05
        "jump_interval": 0.5,    // 跳跃间隔（秒），默认 0.5 秒跳一次
        "jump_press_time": 0.1   // 每次跳跃按键时长（秒），默认 0.1 秒
    }
    """
    pass
