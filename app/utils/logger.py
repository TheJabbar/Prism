from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan> - <level>{message}</level>")
logger.add("logs/prism.log", rotation="10 MB", retention="30 days", level="DEBUG")
