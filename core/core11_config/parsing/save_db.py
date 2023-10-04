from ..config import Config, config_dependencies


@config_dependencies(('.database', str))
def save_config_into_db(config: Config, db_name: str):
    raise NotImplementedError
