import os
from loguru import logger
import sys

def get_recent_activity_log(n_lines: int = 10) -> list[str]:
    """Devuelve las últimas n líneas del log de actividad."""
    log_path = os.path.join(os.path.dirname(__file__), '../../logs/activity.log')
    log_path = os.path.abspath(log_path)
    if not os.path.exists(log_path):
        return []
    with open(log_path, encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-n_lines:]]

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level}</level> | "
           "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
)
logger.add(
    "logs/activity.log",
    rotation="1 day",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} - {message}",
    encoding="utf-8",
    enqueue=True
)

__all__ = ["logger"]