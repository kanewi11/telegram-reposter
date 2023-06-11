import logging

from .config import LOGS_DIR


logger_name = 'app'
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
log_filepath = LOGS_DIR.joinpath(logger_name + '.log')
handler = logging.FileHandler(log_filepath, encoding='utf8')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.warning(f'Start {logger_name}!')
