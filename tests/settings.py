DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-US'
SITE_ID = 1
USE_L10N = True
USE_TZ = True

SECRET_KEY = 'local'

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'tests',
    'heythere',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

NOTIFICATIONS = {
    'DEFAULT': {
        'persistent': True,  # stays until dismissed
        'send_as_email': False,  # send as email
        'headline_template': '{{headline}}',  # Django template for headline
        'body_template': '{{body}}',  # Django template for body
        'email_field': 'email'  # Assume field named 'email' is user's email
    },
    'CUSTOM_USER': {
        'persistent': True,
        'send_onsite': True,
        'send_as_email': False,
        'headline_template': 'My headline: {{headline}}',
        'body_template': 'My body: {{body}}',
        'email_field': 'contact'
    },
    'TEMPORARY': {
        'persistent': False,
        'send_onsite': True,
        'send_as_email': True,
        'headline_template': 'My headline: {{headline}}',
        'body_template': 'My body: {{body}}',
    },
    'SEND_EMAIL': {
        'persistent': True,
        'send_onsite': False,
        'send_as_email': True,
        'headline_template': 'My headline: {{headline}}',
        'body_template': 'My body: {{body}}',
    }
}
