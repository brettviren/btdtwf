import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from . import models


def session(database = 'sqlite:///:memory:'):
    if not database or database.lower() == 'none' or database.lower() == "memory":
        database = "sqlite:///:memory:"
    if ":///" not in database:      # assume sqlite3 db file
        database = "sqlite:///" + database

    engine = sa.create_engine(database)
    models.Base.metadata.create_all(engine)
    Session = sa.orm.sessionmaker(engine)
    return Session()
