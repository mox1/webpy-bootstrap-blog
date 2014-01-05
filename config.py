import logging
import os
import sys
import web

env = os.environ.get("WEB_ENV", "development")
print "Environment: %s" % env

logging.basicConfig(filename='logs/%s.log' % env, level=logging.DEBUG)
logger = logging.getLogger('webpy-blog')


#db wildcard selector (for sqlite / mysql /etc) % or *
db_wildcard = "*"
#from playhouse.postgres_ext import PostgresqlExtDatabase
#db = PostgresqlExtDatabase('webpy_skeleton', user='jzellman')

db_name = 'peewee.db'

# Default settings. Override below
web.config.debug = True
cache = False


#for printing time
TIME_FORMAT = "%a, %d %b %Y" # %H:%M:%S
LONG_TIME_FORMAT = "%%A, %%b %s %%Y"
MAX_COMMENT = 4096
email_errors = web.storage(to_address='',
                           from_address='server-error@example.com')

web.config.smtp_server = '127.0.0.1'
web.config.smtp_port = 25

if env == 'production':
    web.config.debug = False
    cache = True
    email_errors.to_address = 'fixme@example.com'
elif env == 'staging':
    dac_host = 'localhost:8000'
    web.config.debug = True
    cache = False
    email_errors.to_address = 'fixme@example.com'
elif env == 'development':
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logging.getLogger('peewee').addHandler(ch)
elif env == "test":
    pass
