from .settings import BASE_DIR

# Configuration of project ovveride here
ALLOWED_HOSTS = ["*"]
DEBUG = True

# Database configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}
