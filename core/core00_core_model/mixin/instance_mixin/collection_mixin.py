from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from ..meta_mixin.name_from_dependencies_mixin import ChangeClassNameMixin
from ....core05_persistent_model.sql_bases import add_sql_base
from ...utils.naming import classname_for

from sqlalchemy.ext.declarative import declarative_base



def CollectionMixin(metadata_type, entry_type):
    assert getattr(metadata_type, '__tablename__', None),\
        f"Metadata type {metadata_type} does not have mandatory tablename, it must by some SQL Alchemy object" \
        f" to create relation on"
    assert getattr(entry_type, '__tablename__', None),\
        f"Entry type {entry_type} does not have mandatory tablename, it must by some SQL Alchemy object" \
        f" to create relation on"
    assert len(metadata_type.primary_keys) == 1, f"Composite foreign key not supported by CollectionMixin (yet)"
    assert len(entry_type.primary_keys) == 1, f"Composite foreign key not supported by CollectionMixin (yet)"
    # metadata_concept must inherit from the repository mixin
    print(metadata_type)
    print(metadata_type.primary_keys_full[0])
    print(entry_type.primary_keys_full[0])
    class Mixin(ChangeClassNameMixin(metadata_type, entry_type)):
        __abstract__ = True

        __tablename__ = f"<{metadata_type.__tablename__}>[{entry_type.__tablename__}]"

        __named_metadata__ = f"metadata<{metadata_type.__tablename__}>"
        __named_entry__ = f"entry<{entry_type.__tablename__}>"

        metadata_id: Mapped[int] = mapped_column(__named_metadata__, Integer,
                                                 ForeignKey(metadata_type.primary_keys_full[0]), primary_key=True)
        entry_id: Mapped[int] = mapped_column(__named_entry__, Integer,
                                              ForeignKey(entry_type.primary_keys_full[0]), primary_key=True)

        @declared_attr
        def metadata_obj(cls) -> Mapped[metadata_type]:
            return relationship(metadata_type, foreign_keys=[cls.metadata_id])

        @declared_attr
        def entry(cls) -> Mapped[entry_type]:
            return relationship(entry_type, foreign_keys=[cls.entry_id])

        @classmethod
        def __getattr__(cls, attr_name):
            print("GETTING ATTR")
            print(attr_name)
            if attr_name == '__init__':
                raise AttributeError
            return getattr(cls, attr_name)

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


        @classmethod
        def create(cls, metadata: metadata_type | None = None, **metadata_attrs):
            if not metadata:
                metadata = metadata_type.create(commit=True, **metadata_attrs)
            return cls(metadata)
    return Mixin