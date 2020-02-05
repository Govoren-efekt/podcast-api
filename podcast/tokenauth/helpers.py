import jwt,json
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from podcast.settings.base import get_env_variable
from . import settings as ta_settings

from podcast.users.models import ClubUser


def email_login_link(request, email):
    email = ta_settings.NORMALIZE_EMAIL(email)
    # create user and set inactive status
    user = ClubUser.objects.create_user(email=email)
    token = generate_token(user)

    # Send to the new email address if one is specified (we're trying to
    # change the email), otherwise send to the old one (we're trying to
    # log in).
    send_to_email = email

    # Send the link by email.
    send_mail(
        render_to_string(
            "tokenauth_login_subject.txt"
        ).strip(),
        render_to_string(
            "tokenauth_login_body.txt",
            {"token": token}
        ),
        'hello@podcastclub.net',
        [send_to_email],
        fail_silently=False,
    )

def generate_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + 
            timedelta(seconds=ta_settings.JWT_EXP_DELTA_SECONDS)
    }
    secret = get_env_variable('SECRET_KEY')
    jwt_token = jwt.encode(payload, secret, ta_settings.JWT_ALGORITHM)
    return jwt_token.decode('utf-8')