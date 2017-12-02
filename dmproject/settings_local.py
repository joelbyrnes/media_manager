# noinspection PyUnresolvedReferences
from dmproject.settings import *

from socket import gethostname, gethostbyname
ALLOWED_HOSTS = ['localhost', '127.0.0.1', gethostname(), gethostbyname(gethostname())]
ALLOWED_HOSTS += ['192.168.0.%s' % i for i in range(256)]
