import sys
from pathlib import Path

from loguru import logger

log_path = Path("logs/app.log")
log_path.parent.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
)

logger.add(
    str(log_path),
    level="DEBUG",
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
