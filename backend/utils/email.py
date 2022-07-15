from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail

def send_email(template_path, recipient, link, site_name, **kwargs):
    email_body = render_to_string(template_path, {"link": link, "site_name": site_name, **kwargs})
    email_subject = f"{site_name}: Email Account Verification"
    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL,[recipient])