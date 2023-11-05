from ...mixin.instance_mixin.eagerload_mixin import EagerloadMixin, JoinBehavior
from ...mixin.instance_mixin.introspection_mixin import IntrospectionMixin
from ....core24_datastream.policy.function_call import CallingContractArguments, consume_arguments_method
from ...mixin.instance_mixin.repository_mixin import RepositoryMixin
from ....core05_persistent_model.policy.session import get_session
from ...mixin.meta_mixin.proxy_to import ProxyToMixin
from ...utils.column_type import column_to_type
from ...mixin.base_mixin import BaseMixins
from ...concept.named import Named

from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr, joinedload, Query
from sqlalchemy import Integer, ForeignKey, orm


class Aliases(*BaseMixins, Named):
    __tablename__ = 'table_aliases'

    detail: Mapped[str]


alias_prefix = 'ALIAS'

def ALIAS(alias_target_class, alias_name: str, keep_full_name: bool = False):

    # this only case is when the class is simple (collections cannot inherit from the RepositoryMixin)
    is_simple = RepositoryMixin in alias_target_class.__mro__
    # either the class itself, or the metadata must be inspectable (for getting its primary key)
    alias_target = alias_target_class if is_simple else alias_target_class.__metadata__
    print("atbeg ", alias_target_class, is_simple, "=> ", alias_target)

    full_tablename = f"{alias_prefix}<{alias_target.__tablename__}({alias_name})>" \
        if not hasattr(alias_target_class, '__collection_entry__') \
        else f"{alias_prefix}<{alias_target_class.__collection_entry__.__tablename__}({alias_name})>"

    with get_session() as _:
        Aliases.get_create(name=alias_name, detail=full_tablename.replace(f"({alias_name})", ''))

    assert getattr(alias_target, '__tablename__', None), \
        f"Target class {alias_target} does not have mandatory tablename, it must by some SQL Alchemy object" \
        f" to create relation on"
    assert len(alias_target.primary_keys) == 1, f"Composite foreign key not supported by Alias class (yet)"

    alias_target_primary_key_name = alias_target.primary_keys_full[0].key
    print("the types?")
    print(alias_target_primary_key_name)
    mapped_alias_target_type, sqlalchemy_alias_target_type = column_to_type(alias_target.primary_keys_full[0])
    print(mapped_alias_target_type, sqlalchemy_alias_target_type)

    class Alias(ProxyToMixin(alias_target,
                             *([alias_target_class.__entry__] if hasattr(alias_target_class, '__collection_entry__')
                                else [])),
                EagerloadMixin, RepositoryMixin):

        __tablename__ = full_tablename if keep_full_name else alias_name

        __named_target__ = f"target<{alias_target.__tablename__}>"

        __joinable__ = {
            'behavior': JoinBehavior.EAGER_ALL,
            'join': ['aliased'],
            'next_join': [alias_target_class] if hasattr(alias_target_class, '__collection_entry__') else []
        }


        aliased_id: Mapped[mapped_alias_target_type] = mapped_column(__named_target__, sqlalchemy_alias_target_type,
                                                                        ForeignKey(alias_target.primary_keys_full[0]),
                                                                        primary_key=True)

        @declared_attr
        def aliased(cls) -> Mapped[alias_target]:
            return relationship(alias_target, foreign_keys=[cls.aliased_id])

        @property
        def target(self):
            return self._base_object

        @target.setter
        def target(self):
            raise NotImplementedError

        @target.deleter
        def target(self):
            raise NotImplementedError

        @consume_arguments_method({
            'commit': (bool, CallingContractArguments.OneOrNone),
            'target': (alias_target, CallingContractArguments.OneOrNone),
            'target_class': (alias_target_class, CallingContractArguments.OneOrNone),  # in case of provided collection
        }, permit_multiple_types=True)
        def __init__(self, commit: bool = True,
                     target: alias_target | None = None,
                     target_class: alias_target_class | None = None,
                     **argv):
            print("CONSTRUCTING")
            print(target, target_class, argv)
            if is_simple and target_class:
                raise Exception(f"Not expecting {target_class} twice (already got target = {target})")
            if target_class:
                self.aliased = target_class.metadata
                self._base_object = target_class
            elif target:
                self.aliased = target
                self._base_object = target if is_simple else alias_target_class.get_create(metadata=self.aliased,
                                                                                           commit=commit)
            else:
                self._base_object = alias_target.get_create(commit=commit, **argv) if is_simple \
                    else alias_target_class.get_create(commit=commit, **argv)
                self.aliased = self._base_object if is_simple else self._base_object.metadata
            if commit:
                self.ensure_target()

        @orm.reconstructor
        def init_on_load(self):
            self._base_object = self.aliased if is_simple else \
                alias_target_class.get_create(metadata=self.aliased, commit=False)

        def ensure_target(self):
            # according to whether the provided object comes from DB (has his primary key set) or not, create the target
            if not hasattr(self.aliased, alias_target_primary_key_name) \
                    or not getattr(self.aliased, alias_target_primary_key_name):
                attrs = {col: getattr(self.aliased, col) for col in self.aliased.columns}
                not_null_attrs = {k: v for k, v in attrs.items() if v}
                all_for = self.aliased.all_for(**not_null_attrs)
                if len(all_for) > 1:
                    raise Exception(f"Too much values for {alias_target} found with criteria: {not_null_attrs}, "
                                    f"either commit=False or add unicity constraint")
                if not all_for:
                    self.aliased.create(commit=True, **not_null_attrs)

        def __getattr__(self, item):
            if item == '_base_object':  # the object is not yet initialized, it causes infinite recursion
                return None
            return getattr(self._base_object, item)

        def __repr__(self):
            return '{'+f"alias #{self.aliased_id} -> {self._base_object}"+'}'

        def join(self, current_query: Query, current_object):  # current_object must be Alias
            query = current_query.options(joinedload(getattr(current_object, 'aliased')))
            if hasattr(alias_target_class, '__joinable__'):
                query = alias_target_class.join(query)
            return query

    return Alias