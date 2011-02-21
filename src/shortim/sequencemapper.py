# -*- coding: utf-8 -*-

from django.conf import settings
import string

## set the default shorturl chars
DEFAULT_SHORTURL_CHARS = string.uppercase
DEFAULT_SHORTURL_CHARS += string.lowercase
DEFAULT_SHORTURL_CHARS += string.digits

## allow user to configure a different chars chain
SHORTIM_SHORTURL_CHARS = getattr(settings,
    'SHORTIM_SHORTURL_CHARS', DEFAULT_SHORTURL_CHARS)

class SequenceMapper(object):

    @staticmethod
    def from_decimal(number):
        base = len(SHORTIM_SHORTURL_CHARS)
        code = ''

        ## generate the respective code of the sequence
        index = 1
        while number > 0 and index+1 > 0:
            index = number % base - 1
            code = SHORTIM_SHORTURL_CHARS[index] + code
            number = number / base
            if number > 0 and index < 0:
                number -= 1
                index = 0
        return code

    @staticmethod
    def to_decimal(code):
        base = len(SHORTIM_SHORTURL_CHARS)
        number = 0

        ## calculate the respective number of the code
        for i, c in enumerate(code[::-1]):
            index = SHORTIM_SHORTURL_CHARS.index(c)
            number += base ** i * (index+1)
        return number
