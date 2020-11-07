"""
Database can be either an sqlite file or a postgress server
"""

import os
from .. import TMPDIR

## Default connection string points to a local sqlite file in
## decipher/data/data.db
# DB_CONNECTION_STRING = "postgresql+psycopg2:///{}data.db".format(TMPDIR)
DB_CONNECTION_STRING = "postgres://chiefsan:password@127.0.0.1:5432/decipher"

## location of sqlite file overridden by an env var
if "deCiPherDBFile" in os.environ.keys():
    DB_CONNECTION_STRING = "sqlite:///{}".format(
        os.environ["deCiPherDBFile"])
