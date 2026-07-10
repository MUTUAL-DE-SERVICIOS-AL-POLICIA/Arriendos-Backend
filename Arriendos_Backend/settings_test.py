from Arriendos_Backend.settings import *

LDAP_STATUS = False

MIDDLEWARE = [
    m for m in MIDDLEWARE if 'threadlocals' not in m
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'CRITICAL',
    },
}
