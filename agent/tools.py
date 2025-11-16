import sys
import logging
import os
from datetime import datetime
from pathlib import Path
import locale
import codecs

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
