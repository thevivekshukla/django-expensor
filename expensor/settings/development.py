from expensor.old_settings import *


DEBUG = True


DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'dbbackups/'}


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
