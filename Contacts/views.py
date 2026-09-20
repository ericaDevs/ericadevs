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
            # Save the contact to the database first — this must always succeed.
            contact = form.save()

            # Attempt to send an email notification. This is best-effort only.
            # Any failure here must NOT produce a 500 — the message is already saved.
            _send_contact_notification(contact)

            messages.success(request, "Message sent successfully!")
            return redirect('contacts:contacts')
        else:
            messages.error(request, "Message not sent, please check the form and try again!")
            return render(request, 'pages/contacts.html', {"form": form})

    form = ClientsContacts()
    return render(request, 'pages/contacts.html', {"form": form})


def _send_contact_notification(contact):
    """Send a notification email to the site owner. Silently logs any failure."""
    try:
        email_user = getattr(settings, 'EMAIL_HOST_USER', None)
        email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)

        if not email_user or not email_password:
            logger.warning(
                "Email credentials not configured (EMAIL_HOST_USER / EMAIL_HOST_PASSWORD). "
                "Skipping notification email for contact from %s.",
                contact.email,
            )
            return

        recipient = getattr(settings, 'CONTACT_RECIPIENT_EMAIL', None) or email_user
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or email_user

        subject = f"New Portfolio Message: {contact.subject} (from {contact.full_name})"
        body = (
            f"You have received a new contact inquiry from your portfolio website.\n\n"
            f"From: {contact.full_name}\n"
            f"Email: {contact.email}\n"
            f"Subject: {contact.subject}\n\n"
            f"Message:\n{contact.message}\n"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[recipient],
            reply_to=[contact.email],
        )
        # fail_silently=True: any SMTP error is suppressed — we already saved the message.
        email.send(fail_silently=True)
        logger.info("Contact notification email sent to %s.", recipient)

    except Exception as exc:  # noqa: BLE001
        # Belt-and-suspenders: log but never let email issues cause a 500.
        logger.exception("Unexpected error while sending contact notification email: %s", exc)