from core.core30_context.policy.common_contexts import load_local_context
from core.core31_policy.entrypoint.entrypoint import cli_entrypoint


if __name__ == "__main__":
    load_local_context()
    cli_entrypoint(True)

    from core.core00_core_model.mixin.meta_mixin.create_table_when_engine_mixin import AutoTableCreationMixin
    from core.core00_core_model.mixin.instance_mixin.collection_mixin import CollectionMixin
    from core.core00_core_model.mixin.instance_mixin.representation_mixin import ReprMixin
    from core.core00_core_model.mixin.instance_mixin.repository_mixin import RepositoryMixin
    from core.core00_core_model.mixin.instance_mixin.session_mixin import SessionMixin
    from core.core05_persistent_model.policy.session import get_session
    from core.core00_core_model.concept.timed import CreatedModifiedAt
    from core.core20_messaging.log.common_loggers import debug_logger
    from core.core00_core_model.concept.merge import merge_concepts
    from core.core00_core_model.concept.named import Named

    logger = debug_logger()

    from sqlalchemy.orm import mapped_column, Mapped, relationship
    from sqlalchemy import String as _String, Integer, ForeignKey

    named_and_createdmodified_at = merge_concepts(Named, CreatedModifiedAt)

    class BaseMetadata(AutoTableCreationMixin, ReprMixin, RepositoryMixin, named_and_createdmodified_at):
        __tablename__ = 'named_dated'

    class BasicListItem(AutoTableCreationMixin, ReprMixin, RepositoryMixin):
        __tablename__ = 'item'
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        value: Mapped[str] = mapped_column(_String, unique=True)

    with get_session() as session:
        metadata1 = BaseMetadata.get_create(name='liste1')
        item1 = BasicListItem.get_create(value='item1')
        item2 = BasicListItem.get_create(value='item2')
        item3 = BasicListItem.get_create(value='item3')
        item4 = BasicListItem.get_create(value='item4')

    class BasicList(CollectionMixin(BaseMetadata, BasicListItem), ReprMixin):
        pass

    session.add(BasicList(metadata_obj=metadata1, entry=item1))
    session.commit()
