import os

env = os.getenv('DJNAGO_ENV', 'dev').lower

if env == 'prod':
    from .prod import *
    
elif env == 'dev':
    from .dev import *