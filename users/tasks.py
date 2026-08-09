from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_registration_email(user_email, username):
    subject = 'Welcome to GroceryOps'
    message = f'Hi {username},\n\nYour household account profile has been successfully provisioned. Welcome aboard!'

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False
    )


@shared_task
def send_async_reset_email(subject, body, from_email, to_email):
    """ Asynchronously processes and dispatches password recovery emails via Celery. """

    send_mail(
        subject,
        body,
        from_email,
        [to_email], fail_silently=False
    )
