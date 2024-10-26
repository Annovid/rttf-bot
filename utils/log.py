import datetime
import logging
import os

log_dir = "logs/runs/"
os.makedirs(log_dir, exist_ok=True)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)-7s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_filepath)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
