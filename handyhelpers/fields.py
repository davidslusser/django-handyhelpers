"""
Description:
    CryptField creates an encrypted char-based field for storing data securely. Values are
    entered as plain-text and store encrypted in the database. The SECRET_KEY from settings.py
    is used as the encryption/decryption key.
"""

# system modules
from simplecrypt import encrypt, decrypt

# django modules
from django.db import models
from django.conf import settings


def encrypt_field(value):
    """ take a plain-text value and return its encrypted equivalent
    https://github.com/andrewcooke/simple-crypt
    """
    return encrypt(settings.SECRET_KEY, value).encode('base64')


def decrypt_field(value):
    """ take an encrypted value and return its plain-text equivalent
    https://github.com/andrewcooke/simple-crypt
    """
    return decrypt(settings.SECRET_KEY, value.decode('base64'))


class CryptField(models.TextField):
    """ CryptField is a generic textfield that encrypts the value for storage """
    def get_db_prep_value(self, value, connection, prepared=False):
        """ Convert plain-text value to encrypted value for database storage """
        if self.null and value is None:
            return None
        return encrypt_field(value)

    def from_db_value(self, value, expression, connection, context):
        """ Convert encrypted value to plain-text """
        if value is None:
            return value
        return decrypt_field(value)

    def to_python(self, value):
        """ Convert encrypted value to plain-text """
        if value is None or isinstance(value, int):
            return value
        return decrypt_field(value)

    def get_internal_type(self):
        return "CryptField"
