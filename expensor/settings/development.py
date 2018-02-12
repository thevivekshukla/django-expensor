from expensor.old_settings import *


DEBUG = True


DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'dbbackups/'}


CELERY_BROKER_URL = 'amqp://localhost'


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL_DEV')
    )
}


# memcache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}