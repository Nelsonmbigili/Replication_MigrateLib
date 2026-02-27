from dynaconf import settings

REDIS_HOST = settings.get('REDIS_HOST', '0.0.0.0')
REDIS_PORT = settings.get('REDIS_PORT', 6379)
REDIS_DB = settings.get('REDIS_DB', 0)
REDIS_KEY_PREFIX = settings.get('REDIS_KEY_PREFIX', 'fastapi_pydiator:')

DISTRIBUTED_CACHE_IS_ENABLED = settings.get("DISTRIBUTED_CACHE_IS_ENABLED", True)
CACHE_PIPELINE_IS_ENABLED = settings.get("CACHE_PIPELINE_IS_ENABLED", False)
LOG_PIPELINE_IS_ENABLED = settings.get("LOG_PIPELINE_IS_ENABLED", True)
