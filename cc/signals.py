from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def user_save_handler(sender, **kwargs):
    user_instance = kwargs["instance"]
    if not hasattr(user_instance, "profile"):
        new_profile = Profile()
        new_profile.user = user_instance
        new_profile.personalList = []
        new_profile.save()
