from core.core05_persistent_model.policy.session import create_sql_engine
from core.core30_context.policy.common_contexts import load_local_context
from core.core31_policy.entrypoint.entrypoint import cli_entrypoint


if __name__ == "__main__":
    load_local_context()
    cli_entrypoint(True)
    engine = create_sql_engine()

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, String as _String

    Base = declarative_base()
    sql_bases = [Base]

    STRING_SIZE = 256


    class String(Base):
        __tablename__ = 'string'

        id = Column(_String(STRING_SIZE), primary_key=True)


    Base.metadata.create_all(engine)
