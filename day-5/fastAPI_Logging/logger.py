import logging
import sys

#Get logger
logger=logging.getLogger()

#Create formatter
formatter=logging.Formatter(fmt="%(asctime)s-%(levelname)s-%(message)s")

#create handler
stream_handler=logging.StreamHandler(sys.stdout)
file_handler=logging.FileHandler("app.log")

#set formatter
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

#Add handler to logger
logger.handlers=[stream_handler,file_handler]

#set-log
logger.setLevel(logging.INFO)


