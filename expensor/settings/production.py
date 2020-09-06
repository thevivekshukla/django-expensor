from expensor.old_settings import *

DEBUG = False

ALLOWED_HOSTS = config('HOST', cast=Csv())

SECRET_KEY = config('SECRET_KEY')


####################### django-dbbackup ##############3
DBBACKUP_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DBBACKUP_STORAGE_OPTIONS = {
    'access_key': config('AWS_DB_ACCESS_KEY'),
    'secret_key': config('AWS_DB_SECRET_KEY'),
    'bucket_name': config('AWS_DB_BUCKET_NAME'),
    'default_acl': 'private',
}


CELERY_BROKER_URL = 'amqp://localhost'


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}


# memcache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}