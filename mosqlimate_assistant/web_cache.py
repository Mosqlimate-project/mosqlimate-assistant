import requests_cache

shared_cache_session = requests_cache.CachedSession(
    'mosqlimate_docs_cache',
    backend='sqlite',
    expire_after=60 * 60 * 24 * 3,  # 3 dias
)
