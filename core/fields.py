import os
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:
    Fernet = None
    InvalidToken = Exception


def _get_fernet():
    """Return a Fernet instance configured from env/settings.

    Expects a base64-encoded key in `FERNET_KEY` environment variable or
    `settings.FERNET_KEY`. Raises `ImproperlyConfigured` if missing.
    """
    if Fernet is None:
        raise ImproperlyConfigured('cryptography package is required for EncryptedTextField')

    key = getattr(settings, 'FERNET_KEY', None) or os.environ.get('FERNET_KEY')
    if not key:
        raise ImproperlyConfigured('FERNET_KEY is not set in environment or settings')

    # key should already be urlsafe base64 32-byte key
    try:
        return Fernet(key)
    except Exception as e:
        raise ImproperlyConfigured(f'Invalid FERNET_KEY: {e}')


class EncryptedTextField(models.TextField):
    """TextField that transparently encrypts/decrypts values using Fernet.

    - Stores ciphertext (URL-safe base64) in DB.
    - Decrypts on access.
    - Requires `FERNET_KEY` in env or `settings`.
    """

    description = "Encrypted text field using Fernet symmetric encryption"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fernet = None

    def _fernet_instance(self):
        if self._fernet is None:
            self._fernet = _get_fernet()
        return self._fernet

    def get_prep_value(self, value):
        """Encrypt before saving to DB."""
        if value is None:
            return None
        if value == '':
            return value
        f = self._fernet_instance()
        if isinstance(value, str):
            value_bytes = value.encode('utf-8')
        else:
            value_bytes = str(value).encode('utf-8')
        token = f.encrypt(value_bytes)
        return token.decode('utf-8')

    def from_db_value(self, value, expression, connection):
        """Decrypt value loaded from DB. If decryption fails, return raw value."""
        if value is None:
            return None
        if value == '':
            return value
        try:
            f = self._fernet_instance()
            # value stored as text
            plaintext = f.decrypt(value.encode('utf-8'))
            return plaintext.decode('utf-8')
        except InvalidToken:
            # Not a Fernet token — return as-is (legacy plaintext)
            return value
        except Exception:
            return value

    def to_python(self, value):
        # Whenever converted to python, attempt to decrypt if needed
        return self.from_db_value(value, None, None)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # keep path so migrations refer to this field class
        return name, path, args, kwargs
