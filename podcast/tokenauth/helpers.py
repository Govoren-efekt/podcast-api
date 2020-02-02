from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from . import settings as ta_settings
from .models import AuthToken


def email_login_link(request, email):
    current_site = get_current_site(request)

    # Create the token.
    email = ta_settings.NORMALIZE_EMAIL(email)
    token = AuthToken.objects.create(email=email)

    # Send to the new email address if one is specified (we're trying to
    # change the email), otherwise send to the old one (we're trying to
    # log in).
    send_to_email = email

    # Send the link by email.
    send_mail(
        render_to_string(
            "tokenauth_login_subject.txt",
            {"current_site": current_site},
            request=request,
        ).strip(),
        render_to_string(
            "tokenauth_login_body.txt",
            {"current_site": current_site, "token": token},
            request=request,
        ),
        ta_settings.DEFAULT_FROM_EMAIL,
        [send_to_email],
        fail_silently=False,
    )
