from django.db import models
from django.utils.text import slugify


class Project(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	problem = models.TextField()
	solution = models.TextField()
	cover_photo = models.ImageField(upload_to='projects/', blank=True, null=True)
	technologies = models.JSONField(default=list)
	url = models.URLField(blank=True)
	date = models.DateField()
	slug = models.SlugField(max_length=220, unique=True, editable=False)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.title
