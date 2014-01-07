import logging
import os
import sys
import web



####USER EDITABLE####
#enabled by default, see below to disable
ERROR_EMAIL_ADDR = "root@localhost"
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 25
#to display time
TIME_FORMAT = "%a, %d %b %Y" # %H:%M:%S
#double %% required
LONG_TIME_FORMAT = "%%A, %%b %s %%Y"
MAX_COMMENT = 4096

####END USER EDITABLE####



####DEVLOPMENT / ADVANCED CONFIG#####

env = os.environ.get("WEB_ENV", "development")
print "Environment: %s" % env


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
    email_errors.to_address = ERROR_EMAIL_ADDR
elif env == "staging":
    dac_host = "localhost:8000"
    web.config.debug = True
    cache = False
    email_errors.to_address = ERROR_EMAIL_ADDR
elif env == "development":
    logging.basicConfig(filename="logs/%s.log" % env, level=logging.DEBUG)
    logger = logging.getLogger("webpy-blog")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logging.getLogger("peewee").addHandler(ch)
elif env == "test":
    pass
