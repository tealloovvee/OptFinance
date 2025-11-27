from typing import Optional

from django.conf import settings
from django.core import signing

EMAIL_CONFIRMATION_SALT = "registration.email_confirmation"


def generate_email_confirmation_token(email: str) -> str:

    signer = signing.TimestampSigner(salt=EMAIL_CONFIRMATION_SALT)
    return signer.sign(email)


def verify_email_confirmation_token(token: str) -> Optional[str]:

    signer = signing.TimestampSigner(salt=EMAIL_CONFIRMATION_SALT)
    max_age = getattr(settings, "EMAIL_CONFIRMATION_TOKEN_MAX_AGE", 60 * 60 * 24)
    try:
        return signer.unsign(token, max_age=max_age)
    except (signing.BadSignature, signing.SignatureExpired):
        return None

