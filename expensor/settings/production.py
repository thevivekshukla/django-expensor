from expensor.old_settings import *

DEBUG = False

ALLOWED_HOSTS = config("HOST", cast=Csv())

SECRET_KEY = config("SECRET_KEY")

"""
*************************** SECURITY ****************************************
"""
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


####################### django-dbbackup ##############3
DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DBBACKUP_STORAGE_OPTIONS = {
    "access_key": config("AWS_DB_ACCESS_KEY"),
    "secret_key": config("AWS_DB_SECRET_KEY"),
    "bucket_name": config("AWS_DB_BUCKET_NAME"),
    "default_acl": "private",
}


DATABASES = {"default": dj_database_url.config(default=config("DATABASE_URL"))}
