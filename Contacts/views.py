import logging
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from Contacts.forms import ClientsContacts

logger = logging.getLogger(__name__)

def contacts_view(request):
    if request.method == "POST":
        form = ClientsContacts(request.POST)
        if form.is_valid():
            contact = form.save()

            # Send email notification to site owner
            recipient = getattr(settings, 'CONTACT_RECIPIENT_EMAIL', 'erikalorot23@gmail.com')
            email_subject = f"New Portfolio Message: {contact.subject} (from {contact.full_name})"
            email_body = (
                f"You have received a new contact inquiry from your portfolio website.\n\n"
                f"From: {contact.full_name}\n"
                f"Email: {contact.email}\n"
                f"Subject: {contact.subject}\n\n"
                f"Message:\n{contact.message}\n"
            )

            email_user = getattr(settings, 'EMAIL_HOST_USER', None)
            email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
            
            if email_user and email_password:
                try:
                    email = EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', email_user),
                        to=[recipient],
                        reply_to=[contact.email],
                    )
                    email.send(fail_silently=False)
                except Exception as e:
                    logger.error("Failed to send contact notification email: %s", e)
            else:
                logger.warning("Email credentials missing. Skipping email send.")

            messages.success(request, "Message sent successfully!")
            return redirect('contacts:contacts')
        else:
            messages.error(request, "Message not sent, please check the form and try again!")
            return render(request, 'pages/contacts.html', {"form": form})

    form = ClientsContacts()
    return render(request, 'pages/contacts.html', {"form": form})