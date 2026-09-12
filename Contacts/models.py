from django.db import models

# Create your models here.
class Clients(models.Model):
    full_name = models.CharField(max_length = 150, blank = False)
    email = models.EmailField(max_length = 200, blank = False)
    subject = models.CharField(max_length = 200, blank = False)
    message = models.TextField(blank = False)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"