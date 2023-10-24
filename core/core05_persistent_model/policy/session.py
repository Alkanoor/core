from ...core02_model.typed.service import RestrictedService, url_to_service, Service, GenericServiceProxy,\
    ProxifiedService, service_to_url, SimpleService
from ...core30_context.context_dependency_graph import context_dependencies, context_producer
from ...core00_core_model.mixin.session_mixin import SessionMixin
from ...core02_model.typed.file import FilePhysical, EncryptedFile
from ...core11_config.config import config_dependencies, Config
from ..typed.db_target import SQLiteDB, PostgreSQLService
from ...core22_action.policy.fs import check_file_access, bad_file_at
from ...core30_context.context import Context

from sqlalchemy import Engine, create_engine
from typing import Union, Callable, Iterator
from sqlalchemy.orm import sessionmaker, Session
from contextvars import ContextVar
from logging import Logger
import contextlib


SupportedDB = Union[RestrictedService[SQLiteDB], RestrictedService[PostgreSQLService]]

@context_dependencies(('.interactor.server.tunnel_to', Callable[[Service | RestrictedService],
                       SimpleService | Callable[[], SimpleService]]))
@context_producer(('.database.service', SupportedDB | Callable[[], SupportedDB]), ('.database.engine_url', str))
@config_dependencies(('.database', str))
def engine_from_config(config: Config, ctxt: Context):
    if config['database'][:6].lower() == 'sqlite':
        if config['database'][:19].lower() == 'sqlite+pysqlcipher:':
            fname = config['database'].split('@')[-1].split('://')[-1].split('?')[0]
            passwd = config['database'].split('://')[-1].split('@')[0].split(':')[-1]
            service = SQLiteDB(db_file=EncryptedFile(file=FilePhysical(filename=fname), password=passwd))
            engine_string = config['database'][:19].lower() + config['database'][19:]
        else:
            service = SQLiteDB(db_file=FilePhysical(filename=config['database'][9:]))
            engine_string = config['database'][:7].lower() + config['database'][7:]
    else:  # expect pgsql
        complex_service = url_to_service(config['database'])
        match complex_service:
            case GenericServiceProxy() | ProxifiedService():  # this case requires an internal handle for proxying
                # either a SimpleService or an iterable (context managed) SimpleService
                service = ctxt['interactor']['server']['tunnel_to'](complex_service)
                engine_string = service_to_url(service)
            case _:
                service = complex_service
                engine_string = config['database']
    ctxt.setdefault('database', {})['service'] = service
    ctxt['database']['engine_url'] = engine_string


def merge_declarative_bases(sql_bases):
    from sqlalchemy import MetaData

    combined_meta_data = MetaData()

    for declarative_base in sql_bases:
        for (table_name, table) in declarative_base.metadata.tables.items():
            combined_meta_data._add_table(table_name, table.schema, table)

    return combined_meta_data


@context_dependencies(('.log.main_logger', Logger))
def _construct_engine(ctxt: Context, engine_url, echo, sqlite, first_time=True, **argv):
    try:
        db_engine = create_engine(engine_url, echo=echo, **argv)
    except Exception as e:
        if first_time:
            if sqlite:
                fname = engine_url.split('://')[-1].split('?')[0]
                try:
                    check_file_access(fname)
                except Exception as e:
                    ctxt['log']['main_logger'].info(f"File access failed to file {fname}: {e}")
                    # trigger the bad file policy to either move or ask user what to do
                    ctxt['log']['main_logger'].info(f"Tried to operate on bad file with result {bad_file_at(fname)}")
            ctxt['log']['main_logger'].info(f"Unable to access {engine_url}, retrying one time")
            return _construct_engine(engine_url, echo, sqlite, False)
        else:
            raise Exception(f"Failed twice to load {engine_url}, please check your database uri")

    def _fk_pragma_on_connect(dbapi_con, con_record):
        if sqlite:
            dbapi_con.execute('pragma foreign_keys=ON')

    from sqlalchemy import event
    event.listen(db_engine, 'connect', _fk_pragma_on_connect)

    from ..sql_bases import _sql_bases
    # create all currently existing metadata for declared bases
    try:
        (*map(lambda x: x.metadata.create_all(db_engine), _sql_bases[::-1]),)
    except:  # if exception, may be that declarative bases contain unresolved references to other tables
        combined = merge_declarative_bases(_sql_bases)
        combined.create_all(db_engine)

    return db_engine


@context_dependencies(('.database.service', SupportedDB | Callable[[], SupportedDB]), ('.database.engine_url', str),
                      ('.log.main_logger', Logger), ('.log.debug_logger', Logger | None))
@context_producer(('.database.engine', Engine), ('.database.sessionmaker', sessionmaker))
def create_sql_engine(ctxt: Context, argv_engine={}, argv_sessionmaker={}):  # argv like expire_on_commit
    match ctxt['database']['service']:
        case Callable():
            @contextlib.contextmanager
            def create_engine_in_context():
                with ctxt['database']['service']() as _:  # in case the service requires resource management
                    yield _construct_engine(ctxt['database']['engine_url'],
                                            ctxt['log']['debug_logger'] is not None,
                                            isinstance(ctxt['database']['service'], SQLiteDB),
                                            **argv_engine)
            db_engine = create_engine_in_context

            @contextlib.contextmanager
            def create_session_maker() -> ContextVar[sessionmaker]:
                with create_engine_in_context() as db_engine:
                    yield ContextVar('_session', default=sessionmaker(db_engine, **argv_sessionmaker))
            ctxt['database']['sessionmaker'] = create_session_maker
        case _:
            db_engine = _construct_engine(ctxt['database']['engine_url'], ctxt['log']['debug_logger'] is not None,
                                          isinstance(ctxt['database']['service'], SQLiteDB), **argv_engine)
            ctxt['database']['sessionmaker'] = ContextVar('_session',
                                                          default=sessionmaker(db_engine, **argv_sessionmaker))

    ctxt['database']['engine'] = db_engine


def _get_session(_sessionmaker: ContextVar, debug_logger: Logger = None):
    try:
        session = _sessionmaker.get()
        SessionMixin.set_session(session)
        yield session
        session.commit()
        if debug_logger:
            debug_logger.debug("Session committed: {}".format(id(session)))
    except Exception:
        session.rollback()
        if debug_logger:
            debug_logger.debug("Session rollback-ed: {}".format(id(session)))
        raise
    finally:
        SessionMixin.set_session(None)
        if debug_logger:
            debug_logger.debug("Session closed: {}".format(id(session)))
        session.close()

@contextlib.contextmanager
@context_dependencies(('.database.sessionmaker', ContextVar[sessionmaker] | Callable[[...], ContextVar[sessionmaker]]),
                      ('.log.debug_logger', Logger | None))
def get_session(ctxt: Context) -> Iterator[Session]:
    if isinstance(ctxt['database']['sessionmaker'], ContextVar):
        yield from _get_session(ctxt['database']['sessionmaker'], ctxt['log']['debug_logger'])
    else:  # assume the sessionmaker is context-managed
        with ctxt['database']['sessionmaker']() as _sessionmaker:
            yield from _get_session(_sessionmaker, ctxt['log']['debug_logger'])


def commit_and_rollback_if_exception(session):
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


if __name__ == "__main__":
    create_session()
