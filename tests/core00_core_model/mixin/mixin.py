import string

from core.core30_context.policy.common_contexts import load_local_context
from core.core31_policy.entrypoint.entrypoint import cli_entrypoint


if __name__ == "__main__":
    load_local_context()
    cli_entrypoint(True)

    from core.core00_core_model.mixin.meta_mixin.create_table_when_engine_mixin import AutoTableCreationMixin
    from core.core00_core_model.mixin.instance_mixin.representation_mixin import ReprMixin
    from core.core00_core_model.mixin.instance_mixin.repository_mixin import RepositoryMixin
    from core.core00_core_model.mixin.instance_mixin.session_mixin import SessionMixin
    from core.core05_persistent_model.policy.session import get_session
    from core.core00_core_model.concept.timed import CreatedModifiedAt
    from core.core20_messaging.log.common_loggers import debug_logger
    from core.core00_core_model.concept.merge import merge_concepts
    from core.core00_core_model.concept.named import Named

    logger = debug_logger()

    from sqlalchemy.orm import mapped_column, Mapped
    from sqlalchemy import String as _String, Integer

    named_and_createdmodified_at = merge_concepts(Named, CreatedModifiedAt)
    print(named_and_createdmodified_at)

    class MyTable(AutoTableCreationMixin, ReprMixin, RepositoryMixin, Named, CreatedModifiedAt):
        __tablename__ = 'autocreate'
        notid: Mapped[int] = mapped_column(Integer(), nullable=True)
        value: Mapped[str] = mapped_column(_String(), unique=True)

    import random

    with get_session() as session:
        logger.info(SessionMixin.session)
        obj = MyTable.get_create(value='bcd', name='??')
        obj2 = MyTable.force_create(value='bcde'+random.choice(string.ascii_letters), name='ab', force_index=True)
        logger.info(obj)
        #logger.info(obj.self_to_json())
        #logger.info(obj.class_to_json())
