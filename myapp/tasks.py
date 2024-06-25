from celery import shared_task
from sparkpost import SparkPost
from os import environ
from django.template.loader import render_to_string


@shared_task
def send_email_with_sparkpost(to_email, from_email, subject, text, invoice_data):
    # Render the email content
    print(invoice_data)
    html = render_to_string('main/invoice_email.html', invoice_data)

    sp = SparkPost(environ.get('SPARKPOST_API_KEY')) # uses the API key from your settings
    response = sp.transmissions.send(
        recipients=[to_email],
        html=html,
        from_email=from_email,
        subject=subject
    )
    return response