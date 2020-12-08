from django import forms
from django.core.exceptions import ValidationError
import re


class AddressForm(forms.Form):
    zip_code = forms.CharField(label='Enter your zip code', max_length=200)

    def clean_zip_code(self):
        zip_regex = re.compile('^[0-9]{5}(?:-[0-9]{4})?$')
        data = self.cleaned_data["zip_code"]
        if zip_regex.match(data):
            return data
        else:
            raise ValidationError(f"{data} is not a US zip code.")