from unittest import TestCase

from . import auth


class AuthTestCase(TestCase):

    def test_verify_decode_jwt(self):
        token = ''
        payload = auth.verify_decode_jwt(token)
        self.assertIsNotNone(payload)
