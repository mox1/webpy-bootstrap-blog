import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(name,logdir=None, scrnlog=True, txtlog=True, loglevel=logging.DEBUG):
    logdir = os.path.abspath(logdir)

    if not os.path.exists(logdir):
        os.mkdir(logdir)

    log = logging.getLogger(name)
    log.setLevel(loglevel)
    log.propagate = False
    
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if txtlog:
        txt_handler = RotatingFileHandler(os.path.join(logdir, "blogstrap-py.log"), maxBytes=(1024*1024*20), backupCount=5)
        #txt_handler.doRollover()
        txt_handler.setFormatter(log_formatter)
        log.addHandler(txt_handler)
        log.info("Logger initialised.")

    if scrnlog:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        log.addHandler(console_handler)

    return log
        
        
#this allows us to redirect stderr and stdout to a logfile
#mainly because looking at stderr with lighttpd + mod_fastcgi is important
class LoggerWriter:
    def __init__(self,logger):
        self.logger = logger

    def write(self, message):
        #pump message to stdout
        print message
        #and to log
        self.logger.error(message)