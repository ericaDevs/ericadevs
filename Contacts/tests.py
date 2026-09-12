from django.core import mail
from django.test import TestCase
from django.urls import reverse

from Contacts.models import Clients


class ContactsEmailTests(TestCase):
    def test_contact_form_submission_saves_to_db_and_sends_email(self):
        url = reverse('contacts:contacts')
        post_data = {
            'full_name': 'John Doe',
            'email': 'johndoe@example.com',
            'subject': 'Project Inquiry',
            'message': 'Hello, I would like to discuss a project.',
        }

        response = self.client.post(url, post_data)

        # Should redirect after successful submission
        self.assertRedirects(response, url)

        # Verify saved in database
        self.assertEqual(Clients.objects.count(), 1)
        client = Clients.objects.first()
        self.assertEqual(client.full_name, 'John Doe')
        self.assertEqual(client.email, 'johndoe@example.com')

        # Verify email dispatched
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn('Project Inquiry', sent_email.subject)
        self.assertIn('John Doe', sent_email.subject)
        self.assertIn('johndoe@example.com', sent_email.body)
        self.assertIn('Hello, I would like to discuss a project.', sent_email.body)
        self.assertEqual(sent_email.reply_to, ['johndoe@example.com'])

    def test_invalid_contact_submission_does_not_save_or_send_email(self):
        url = reverse('contacts:contacts')
        response = self.client.post(url, {'full_name': ''})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Clients.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)
