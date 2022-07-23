from decouple import config
from .constants import (
    BANK_AMOUNT_PCT,
    FIXED_SAVINGS_PCT,
    SHOW_INCOME_CALCULATOR_HOUR
)

def gtag(request):
    return {'gtag': config('GTAG_ID', '')}


def constants(request):
    return {
        'constants': {
            'BANK_AMOUNT_PCT': BANK_AMOUNT_PCT,
            'FIXED_SAVINGS_PCT': FIXED_SAVINGS_PCT,
            'SHOW_INCOME_CALCULATOR_HOUR': SHOW_INCOME_CALCULATOR_HOUR,
        }
    }

