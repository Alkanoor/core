from ....core05_persistent_model.policy.session import commit_and_rollback_if_exception
from ....core24_datastream.policy.function_call import CallingContractArguments, consume_arguments_method
from ..meta_mixin.name_from_dependencies_mixin import ChangeClassNameMixin
from ...utils.column_type import column_to_type
from .repository_mixin import RepositoryMixin
from .session_mixin import SessionMixin

from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr, joinedload
from sqlalchemy import Integer, ForeignKey
from typing import List


def CollectionMixin(collection_name, metadata_type, entry_type, is_set: bool = False):
    assert getattr(metadata_type, '__tablename__', None), \
        f"Metadata type {metadata_type} does not have mandatory tablename, it must by some SQL Alchemy object" \
        f" to create relation on"
    assert getattr(entry_type, '__tablename__', None), \
        f"Entry type {entry_type} does not have mandatory tablename, it must by some SQL Alchemy object" \
        f" to create relation on"
    assert len(metadata_type.primary_keys) == 1, f"Composite foreign key not supported by CollectionMixin (yet)"
    assert len(entry_type.primary_keys) == 1, f"Composite foreign key not supported by CollectionMixin (yet)"

    metadata_primary_key_name = metadata_type.primary_keys_full[0].key
    mapped_metadata_type, sqlalchemy_metdata_type = column_to_type(metadata_type.primary_keys_full[0])
    mapped_entry_type, sqlalchemy_entry_type = column_to_type(entry_type.primary_keys_full[0])

    # metadata_concept must inherit from the repository mixin
    class EntryMixin(ChangeClassNameMixin(metadata_type, entry_type), RepositoryMixin):

        __tablename__ = f"{collection_name}<{metadata_type.__tablename__}>[{entry_type.__tablename__}]"

        __named_metadata__ = f"metadata<{metadata_type.__tablename__}>"
        __named_entry__ = f"entry<{entry_type.__tablename__}>"

        if not is_set:
            id: Mapped[str] = mapped_column('id', Integer, primary_key=True)

        metadata_id: Mapped[mapped_metadata_type] = mapped_column(__named_metadata__, sqlalchemy_metdata_type,
                                                                  ForeignKey(metadata_type.primary_keys_full[0]),
                                                                  primary_key=is_set)
        entry_id: Mapped[mapped_entry_type] = mapped_column(__named_entry__, sqlalchemy_entry_type,
                                                            ForeignKey(entry_type.primary_keys_full[0]),
                                                            primary_key=is_set)

        @declared_attr
        def metadata_obj(cls) -> Mapped[metadata_type]:
            return relationship(metadata_type, foreign_keys=[cls.metadata_id])

        @declared_attr
        def entry(cls) -> Mapped[entry_type]:
            return relationship(entry_type, foreign_keys=[cls.entry_id])


    class CollectionMixin(SessionMixin):

        __metadata__ = metadata_type
        __entry__ = entry_type
        __collection_entry__ = EntryMixin

        @consume_arguments_method({
            'commit': (bool, CallingContractArguments.OneOrNone),
            'metadata': (metadata_type, CallingContractArguments.OneOrNone),
        })
        def __init__(self, commit: bool = True, metadata: metadata_type | None = None, **argv):
            if not metadata:
                metadata = metadata_type.get_create(commit, **argv)
            self.entries_initialized = False
            self.metadata = metadata
            self._entries = []

        @classmethod
        def create(cls, commit=True, **argv):
            return cls(commit=commit, **argv)

        def update(self, commit=True, **argv):
            if argv:
                self.metadata.fill(**argv).save(commit=commit)
            else:
                self.__metadata__.query \
                    .filter_by(**{metadata_primary_key_name: getattr(self.metadata, metadata_primary_key_name)}) \
                    .update({})
                if commit:
                    commit_and_rollback_if_exception(self.session)

        def delete(self, commit=True, with_entries=False):
            if with_entries:
                del self.entries
            self.metadata.delete(commit=commit)

        @property
        def entries(self) -> List[entry_type]:
            if not self.entries_initialized:
                self.entries_initialized = True
                self._entries = self.session \
                    .query(self.__collection_entry__) \
                    .join(self.__collection_entry__.entry) \
                    .options(joinedload(self.__collection_entry__.entry)) \
                    .filter(self.__collection_entry__.metadata_obj == self.metadata) \
                    .all()
            return [e.entry for e in self._entries]

        @entries.setter
        def entries(self, new_entries: List[entry_type]):
            del self.entries
            self._entries = []
            for entry in new_entries:
                col_entry = self.__collection_entry__.create(metadata_obj=self.metadata, entry=entry, commit=False)
                self.session.add(col_entry)
                self._entries.append(col_entry)
            self.entries_initialized = True
            self.update(commit=False)
            commit_and_rollback_if_exception(self.session)

        @entries.deleter
        def entries(self):
            self.entries_initialized = False
            self.session.query(self.__collection_entry__) \
                .filter(self.__collection_entry__.id.in_([entry.id for entry in self._entries])) \
                .delete(synchronize_session=False)
            self.update(commit=False)
            self._entries = []

        def __repr__(self):
            entries = '\n- '.join(map(repr, self.entries))
            return f"{self.metadata}" + f"\n- {entries}" if entries else ''

        @classmethod
        def get_for(cls, **attrs):
            metadata = cls.metadata.query.filter_by(**attrs).one_or_none()
            return cls(metadata) if metadata else None

        @classmethod
        def get_create(cls, commit=True, **attrs):
            return cls(commit=commit, **attrs)

        @classmethod
        def all_for(cls, **attrs):
            return [cls(m) for m in cls.metadata.query.filter_by(**attrs).all()]

        @classmethod
        def all_for_condition(cls, condition):
            return [cls(m) for m in cls.metadata.query.filter(condition).all()]

    return CollectionMixin
