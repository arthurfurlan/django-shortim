# -*- coding: utf-8 -*-

from django.test import TestCase
from models import SequenceMapper

class SequenceMapperTest(TestCase):

    ## raise it according to your time and/or hardware
    test_limit = 10000

    def test_sequence_mapping(self):
        for number in xrange(self.test_limit):
            code = SequenceMapper.from_decimal(number)
            number2 = SequenceMapper.to_decimal(code)
            self.assertEqual(number2, number)

    def test_sequence_uniqueness(self):
        codes = []
        for number in xrange(self.test_limit):
            self.assertTrue(number not in codes)
            codes.append(number)
