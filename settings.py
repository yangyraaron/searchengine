#-*- coding: UTF-8 -*-

app = {'name': 'searchengine',
       'logFolder':'log'
       }

db = {
    'mongodb': {
        'host': 'localhost',
        'port': '27017'
    }
}

logging = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        },
    },
    'filters': {},
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "filename": "log/info.log",
            "maxBytes": "10485760",
            "backupCount": "20",
            "encoding": "utf8"
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "verbose",
            "filename": "log/errors.log",
            "maxBytes": "10485760",
            "backupCount": "20",
            "encoding": "utf8"
        }
    },
    'loggers': {
        app['name']: {
            'handlers': ['console', 'error_file_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'test':{
            'handlers':['console'],
            'propagate':True,
            'level':'DEBUG'
        }
    }
}