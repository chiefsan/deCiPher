"""
Database can be either an sqlite file or a postgres server
"""

import os
from .. import TMPDIR

# Default connection string points to a local sqlite file in
# DB_CONNECTION_STRING = "sqlite:///{}data.db".format(TMPDIR

# Default connection string points to postgres database
DB_CONNECTION_STRING = "postgres://chiefsan:password@127.0.0.1:5432/decipher"

# location of database overridden by an env var (used by heroku)
if "DATABASE_URL" in os.environ.keys():
    DB_CONNECTION_STRING = os.environ["DATABASE_URL"]
