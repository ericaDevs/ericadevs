from django.contrib import messages
from django.shortcuts import redirect, render

from Contacts.forms import ClientsContacts


def contacts_view(request):
    if request.method == "POST":
        form = ClientsContacts(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent successfully!")
            return redirect('contacts:contacts')
        else:
            messages.error(request, "Message not sent, please check the form and try again!")
            return render(request, 'pages/contacts.html', {"form": form})

    form = ClientsContacts()
    return render(request, 'pages/contacts.html', {"form": form})