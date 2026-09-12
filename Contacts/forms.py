from django import forms
from . import models

class ClientsContacts(forms.ModelForm):
    class Meta:
        model = models.Clients
        fields = ["full_name", "email", "subject", "message"]