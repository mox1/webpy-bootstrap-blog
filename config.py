import logging
logger = logging.getLogger("")
import os
import sys
import web

####USER EDITABLE####
#disabled by default, set to true to enable
EMAIL_ERRORS = False
ERROR_EMAIL_ADDR = "root@localhost"
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 25
#to display time
TIME_FORMAT = "%a, %d %b %Y" # %H:%M:%S
#double %% required
LONG_TIME_FORMAT = "%%A, %%b %s %%Y"
#The Database limit for this field is 16656, values larger than that will error out.
MAX_COMMENT = 4096
#how often to update stats (in seconds)
STAT_UPDATES = 60 * 60 #every hour by default
####END USER EDITABLE####

valid_upload_ext = [".png",".jpg",".jpeg",".gif",".ico"]

logging.info("emailing errors to %s using server: %s:%s" % (ERROR_EMAIL_ADDR,SMTP_SERVER,SMTP_PORT))


####DEVLOPMENT / ADVANCED CONFIG#####

env = os.environ.get("WEB_ENV", "production")
logging.info("Environment: %s" % env)


#db wildcard selector (for sqlite / mysql /etc) % or *
db_wildcard = "*"
#from playhouse.postgres_ext import PostgresqlExtDatabase
#db = PostgresqlExtDatabase("webpy_skeleton", user="jzellman")
#for sqlite, this is simply the filename
db_name = "peewee.db"

# Default settings. Override below
web.config.debug = True
cache = False

email_errors = web.storage(to_address="",
                           from_address=ERROR_EMAIL_ADDR)

web.config.smtp_server = SMTP_SERVER
web.config.smtp_port = SMTP_PORT


if env == "production":
    web.config.debug = False
    cache = True
    logging.getLogger("").setLevel(logging.INFO)
    email_errors.to_address = ERROR_EMAIL_ADDR
elif env == "staging":
    dac_host = "localhost:8000"
    web.config.debug = True
    cache = False
    email_errors.to_address = ERROR_EMAIL_ADDR
elif env == "development":
    logging.getLogger("").setLevel(logging.DEBUG)
    #logging.basicConfig(filename="logs/%s.log" % env, level=logging.DEBUG)
    #add peewee debugging to output
    #ch = logging.StreamHandler(sys.stdout)
    #ch.setLevel(logging.DEBUG)
    #formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #ch.setFormatter(formatter)
    #logger.addHandler(ch)
    #logging.getLogger("peewee").addHandler(ch)
elif env == "test":
    pass
