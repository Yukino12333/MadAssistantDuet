# -*- coding: utf-8 -*-
"""
MaaAgent 主程序入口
精简版本，只包含核心功能
"""

import sys
import logging
import os
from datetime import datetime
from pathlib import Path
import locale
import codecs

# 确保当前脚本所在目录在 Python 路径中
script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

print(f"脚本目录: {script_dir}")
print(f"工作目录: {os.getcwd()}")
print(f"Python 路径: {sys.path[:3]}")  # 只打印前3个

try:
    from maa.agent.agent_server import AgentServer
    from maa.toolkit import Toolkit
    
    # 导入全局配置
    from config import GAME_CONFIG
    
    # 导入自定义动作
    from movement_action import LongPressKey
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保 MaaFramework 和相关依赖已正确安装")
    sys.exit(1)


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """请求管理员权限重新运行当前脚本"""
    try:
        import ctypes
        # 获取当前脚本的完整路径
        script = os.path.abspath(sys.argv[0])
        
        # 获取参数
        params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
        
        # 使用 ShellExecuteEx 请求管理员权限
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,           # hwnd
            "runas",        # lpOperation - 请求管理员权限
            sys.executable, # lpFile - Python 解释器
            f'"{script}" {params}',  # lpParameters - 脚本和参数
            None,           # lpDirectory
            1               # nShowCmd - SW_SHOWNORMAL
        )
        
        if ret > 32:  # ShellExecute 成功
            sys.exit(0)
        else:
            print(f"请求管理员权限失败，错误代码: {ret}")
            return False
            
    except Exception as e:
        print(f"请求管理员权限时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def setup_logging():
    """配置日志系统，将日志输出到文件和控制台"""
    # 创建日志目录
    log_dir = r".\logs_agent"
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名（按日期和时间）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"agent_{timestamp}.log")
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志记录器
    root_logger = logging.getLogger()

    # 清除已有 handler，避免重复添加
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # 根 logger 设置为最低级别
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 文件处理器：DEBUG 及以上写入文件
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 控制台处理器：INFO 及以上输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
    logger.info(f"日志系统已初始化，日志文件: {log_file}")
    
    return log_file


def main():
    # 检查管理员权限
    if not is_admin():
        print("=" * 60)
        print("[!] 检测到未以管理员权限运行")
        print("PostMessage 输入需要管理员权限才能向游戏窗口发送消息")
        print("正在请求管理员权限...")
        print("=" * 60)
        
        if run_as_admin():
            # 成功请求提权，当前进程将退出
            return
        else:
            print("=" * 60)
            print("❌ 无法获取管理员权限")
            print("请手动以管理员身份运行此脚本")
            print("=" * 60)
            input("按 Enter 键退出...")
            sys.exit(1)
    
    # 初始化日志系统
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("MAD Assistant Agent 启动")
    logger.info("=" * 60)
    logger.info("[OK] 以管理员权限运行")
    logger.info(f"脚本目录: {script_dir}")
    logger.info(f"工作目录: {os.getcwd()}")
    
    # 检查参数
    if len(sys.argv) < 2:
        logger.error("缺少 socket_id 参数")
        print("Usage: python main.py <socket_id>")
        print("socket_id is provided by AgentIdentifier.")
        sys.exit(1)
        
    socket_id = sys.argv[1]
    logger.info(f"Socket ID: {socket_id}")

    try:
        # 初始化 MAA Toolkit
        logger.info("初始化 MAA Toolkit...")
        Toolkit.init_option("./")
        
        # 注册自定义动作（通过导入模块自动注册）
        logger.info("注册自定义动作...")
        logger.info(f"已注册动作: LongPressKey")
        
        # 启动 AgentServer
        logger.info("启动 AgentServer...")
        AgentServer.start_up(socket_id)
        logger.info("AgentServer 已启动，等待任务...")
        
        # 保持运行
        AgentServer.join()
        logger.info("AgentServer 正常退出")
        
    except Exception as e:
        logger.error(f"AgentServer 运行出错: {e}", exc_info=True)
        raise
    finally:
        logger.info("关闭 AgentServer...")
        AgentServer.shut_down()
        logger.info("=" * 60)
        logger.info("MAD Assistant Agent 已退出")
        logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] 程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] 程序异常退出: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
