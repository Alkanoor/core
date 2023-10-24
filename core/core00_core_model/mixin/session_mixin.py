from sqlalchemy.util import classproperty


class SessionMixin:
    _session = None

    @classmethod
    def set_session(cls, session):
        cls._session = session

    @classproperty
    def session(cls):
        if cls._session is not None:
            return cls._session
        else:
            raise NoSessionError('Cant get session.'
                                 'Please, call SaActiveRecord.set_session()')

    @classproperty
    def query(cls):
        return cls.session.query(cls)