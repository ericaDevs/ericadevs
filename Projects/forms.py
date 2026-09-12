import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Project


class ProjectForm(forms.ModelForm):
    title = forms.CharField(
        label='Project Title',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. E-Commerce Platform Redesign',
            'class': 'form-input',
        }),
    )
    technologies = forms.CharField(
        required=False,
        label='Technologies & Tools',
        widget=forms.TextInput(attrs={
            'placeholder': 'React, Django, PostgreSQL, Tailwind CSS',
            'class': 'form-input',
        }),
    )
    url = forms.URLField(
        required=False,
        label='Live Demo or Repository URL',
        widget=forms.URLInput(attrs={
            'placeholder': 'https://github.com/yourname/project',
            'class': 'form-input',
        }),
    )

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'problem',
            'solution',
            'technologies',
            'url',
            'date',
            'cover_photo',
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Summary of the project, its core value proposition, and key highlights...',
                'class': 'form-textarea',
            }),
            'problem': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the core challenge or customer problem addressed...',
                'class': 'form-textarea',
            }),
            'solution': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe your technical architecture, design decisions, and solution...',
                'class': 'form-textarea',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
            }),
            'cover_photo': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'hidden',
                'id': 'id_cover_photo',
            }),
        }

    def clean_url(self):
        url = self.cleaned_data.get('url', '').strip()
        if url and not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        return url

    def clean_technologies(self):
        value = self.cleaned_data.get('technologies')
        if isinstance(value, list):
            technologies = value
        elif isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            try:
                technologies = json.loads(value)
            except json.JSONDecodeError:
                technologies = [item.strip() for item in value.split(',') if item.strip()]
        else:
            technologies = []

        if not isinstance(technologies, list) or not all(isinstance(item, str) for item in technologies):
            raise ValidationError('Enter technologies as comma-separated names.')

        return [item.strip() for item in technologies if item.strip()]

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('A project title is required.')
        slug = slugify(title)
        if not slug:
            raise ValidationError('Please provide a valid project title with letters or numbers.')
        qs = Project.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A project with this title already exists.')
        return title
