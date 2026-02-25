#python logging model
import logging as lg

lg.basicConfig(level=lg.INFO,filename="app.log",filemode="w",
               format="%(asctime)s-%(levelname)s-%(message)s")

"""lg.debug("debug..")
lg.info("info")
lg.warning("warning")
lg.error("error")
lg.critical("critical")"""

"""x=60
lg.info(f"the value of x is {x}")"""

"""
#Basic Error handeling
try:
    1 / 0
except ZeroDivisionError as e:
    #lg.error("zeroDivision error ",exc_info=True)
    lg.exception("test")
"""

#Creating a custom LOGGER
logger=lg.getLogger(__name__)

handler=lg.FileHandler("test.log")
formatter=lg.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("test the custom logger")



