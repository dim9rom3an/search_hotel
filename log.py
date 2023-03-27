from loguru import logger

logger.add('debug.log', level='DEBUG', format='{time}, {level}, {message}',
           rotation='100 KB', compression='zip', backtrace=True)

