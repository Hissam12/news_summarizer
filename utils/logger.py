import logging
import os

def setup_logger(name="NewsLogger", level=logging.INFO):
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        fh = logging.FileHandler("logs/app.log")
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
