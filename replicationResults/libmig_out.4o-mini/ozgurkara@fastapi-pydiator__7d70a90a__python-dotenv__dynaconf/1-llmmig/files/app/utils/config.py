from dynaconf import Dynaconf

settings = Dynaconf(settings_files=['.env'])

REDIS_HOST = settings.REDIS_HOST or '0.0.0.0'
REDIS_PORT = settings.REDIS_PORT or 6379
REDIS_DB = settings.REDIS_DB or 0
REDIS_KEY_PREFIX = settings.REDIS_KEY_PREFIX or 'fastapi_pydiator:'

DISTRIBUTED_CACHE_IS_ENABLED = settings.DISTRIBUTED_CACHE_IS_ENABLED or True
CACHE_PIPELINE_IS_ENABLED = settings.CACHE_PIPELINE_IS_ENABLED or False
LOG_PIPELINE_IS_ENABLED = settings.LOG_PIPELINE_IS_ENABLED or True
