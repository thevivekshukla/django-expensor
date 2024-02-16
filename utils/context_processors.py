from .constants import *


def constants(request):
    return {"constants": {k: v for k, v in globals().items() if k.isupper()}}
