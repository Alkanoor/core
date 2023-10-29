from ....core05_persistent_model.policy.session import commit_and_rollback_if_exception
from .session_mixin import SessionMixin


# mostly inspired from https://github.com/absent1706/sqlalchemy-mixins/blob/master/sqlalchemy_mixins/activerecord.py

class RepositoryMixin(SessionMixin):
    __abstract__ = True

    def fill(self, **attrs):
        for key in attrs:
            setattr(self, key, attrs[key])
        return self

    @classmethod
    def create(cls, commit=True, **argv):
        return cls().fill(**argv).save(commit=commit)

    def update(self, commit=True, **argv):
        return self.fill(**argv).save(commit=commit)

    def delete(self, commit=True):
        self.session.delete(self)
        if commit:
            commit_and_rollback_if_exception(self.session)

    @classmethod
    def delete_many(cls, *ids, commit=True):
        for pk in ids:
            obj = cls.find(pk)
            if obj:
                obj.delete(commit=commit)
        if not commit:  # otherwise changes are committed
            cls.session.flush()

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def first(cls):
        return cls.query.first()

    @classmethod
    def find(cls, id_):
        return cls.query.get(id_)


    @classmethod
    def get_for(cls, **attrs):
        return cls.query.filter_by(**attrs).one_or_none()

    @classmethod
    def get_create(cls, **attrs):
        existing = cls.get_for(**attrs)
        return existing if existing else cls.create(**attrs)

    @classmethod
    def all_for(cls, **attrs):
        return cls.query.filter_by(**attrs).all()

    @classmethod
    def all_for_condition(cls, condition):
        return cls.query.filter(condition).all()
