from celery import shared_task
from utils.email import send_email


@shared_task
def send_email_task(template_path, recipient, link, site_name, **kwargs):
    send_email(template_path, recipient, link, site_name, **kwargs)
