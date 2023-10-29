from ....core05_persistent_model.policy.session import get_engine
from ....core05_persistent_model.sql_bases import add_sql_base

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base


class AutoTableCreationMeta(DeclarativeMeta):
    # __init__ is ok in this case since it's only an external action to perform
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)

        with get_engine() as engine:
            cls.metadata.create_all(engine)


AutoTableCreationMixin = declarative_base(metaclass=AutoTableCreationMeta)

add_sql_base(AutoTableCreationMixin)
