from decouple import config
from .constants import *

def gtag(request):
    return {'gtag': config('GTAG_ID', '')}


def constants(request):
    return {
        'constants': {k:v for k, v in globals().items() if k.isupper()}
    }

