import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(filename)s:%(lineno)d:%(funcName)s:%(levelname)s:%(name)s:%(message)s",
    filename="output.log",
    filemode="a",
)

