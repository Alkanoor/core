from core.core00_core_model.mixin.instance_mixin.introspection_mixin import IntrospectionMixin
from core.core30_context.policy.common_contexts import load_local_context
from core.core31_policy.entrypoint.entrypoint import cli_entrypoint


def create_list():
    from core.core00_core_model.mixin.meta_mixin.create_table_when_engine_mixin import AutoTableCreationMixin
    from core.core00_core_model.mixin.instance_mixin.collection_mixin import CollectionMixin
    from core.core00_core_model.mixin.instance_mixin.repository_mixin import RepositoryMixin
    from core.core00_core_model.mixin.instance_mixin.representation_mixin import ReprMixin
    from core.core00_core_model.concept.timed import CreatedModifiedAt
    from core.core00_core_model.concept.merge import merge_concepts
    from core.core00_core_model.concept.named import Named
    from sqlalchemy import String as _String, Integer
    from sqlalchemy.orm import mapped_column, Mapped


    named_and_createdmodified_at = merge_concepts(Named, CreatedModifiedAt)

    class BaseMetadata(AutoTableCreationMixin, ReprMixin, RepositoryMixin, named_and_createdmodified_at):
        __tablename__ = 'named_dated'

    class BasicListItem(AutoTableCreationMixin, ReprMixin, RepositoryMixin, IntrospectionMixin):
        __tablename__ = 'item'
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        value: Mapped[str] = mapped_column(_String, unique=True)

    class BasicList(CollectionMixin('BASICLIST', BaseMetadata, BasicListItem)):
        def add(self, entry, commit=False):
            self.session.add(self.__collection_entry__.create(metadata_obj=self.metadata, entry=entry, commit=False))
            if commit:
                commit_and_rollback_if_exception(self.session)
            self._entries.append(entry)

    return BaseMetadata, BasicListItem, BasicList


if __name__ == "__main__":
    load_local_context()
    cli_entrypoint(True)

    from core.core05_persistent_model.policy.session import get_session, commit_and_rollback_if_exception
    from core.core20_messaging.log.common_loggers import debug_logger

    logger = debug_logger()


    BaseMetadata, BasicListItem, BasicList = create_list()

    with get_session() as session:
        metadata1 = BaseMetadata.get_create(name='liste1')
        item1 = BasicListItem.get_create(value='item1')
        item2 = BasicListItem.get_create(value='item2')
        item3 = BasicListItem.get_create(value='item3')
        item4 = BasicListItem.get_create(value='item4')

        print(metadata1, metadata1.name)
        l = BasicList(metadata1)
        l.add(item3)
        print(l)
        BasicList.delete(l, True, True)

        l = BasicList(name='list2')
        l.add(item2)
        l.add(item1)
        l.update()
        l.add(item4)
        l.add(item1)
        print(l)

        l.entries = [item1, item1, item3, item4]
        print(l)
