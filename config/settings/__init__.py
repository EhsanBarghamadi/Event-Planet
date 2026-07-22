from decouple import config

env = config('DJANGO_ENV', default='dev').lower()

if env == 'prod':
    from .prod import *
    
elif env == 'dev':
    from .dev import *