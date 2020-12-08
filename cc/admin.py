from django.contrib import admin

from .models import Address, Profile, Template, Tag

# Register your models here.
admin.site.register(Address)
admin.site.register(Profile)
admin.site.register(Template)
admin.site.register(Tag)

