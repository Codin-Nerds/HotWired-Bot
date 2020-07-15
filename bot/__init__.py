
import sys

from loguru import logger

from bot.config import DEV_MODE

log_file = "logs/bot.log"
log_format = "<green>{time:YYYY-MM-DD hh:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name: <18}</cyan> | <level>{message}</level>"
log_level = "DEBUG" if DEV_MODE else "INFO"

logger.configure(
    handlers=[
        dict(sink=sys.stdout, format=log_format, level=log_level),
        dict(sink=log_file, format=log_format, level=log_level, rotation="500 MB")
    ]
)
