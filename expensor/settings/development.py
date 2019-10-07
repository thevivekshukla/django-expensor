from expensor.common import *


DEBUG = True

SECRET_KEY = config('SECRET_KEY')


DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'dbbackups/'}


CELERY_BROKER_URL = config('CELERY_BROKER_URL')


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}


# memcache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': config('MEMCACHED_LOCATION'),
    }
}
