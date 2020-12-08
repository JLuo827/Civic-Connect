from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Address(models.Model):
    address_text = models.CharField(max_length=200, default="None")

    def __str__(self):
        return self.address_text

    def get_absolute_url(self):
        return reverse('cc:RepList')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personalList = models.JSONField()
    templateList = models.ManyToManyField("Template")

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag_name


class Template(models.Model):
    subject = models.CharField(max_length=100)
    body = models.TextField()
    admin_approved = models.BooleanField(default=False)
    date_created = models.DateField(default=timezone.now)

    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, blank=True, null=True, to_field="tag_name")

    def __str__(self):
        return self.subject
