import logging

def build_logger(name: str)-> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

logger: logging.Logger = build_logger("darwin-box-poc")