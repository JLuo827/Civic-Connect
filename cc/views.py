import os
import json
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from .forms import AddressForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Address, Profile, Template, Tag
from django.contrib.auth.decorators import login_required

key = os.environ.get("GOOGLE_API_KEY")

class AddressView(generic.ListView):
    model = Address
    template_name = 'cc/RepList.html'

    def get_queryset(self):
        return Address.objects.all()


def get_rep(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.cleaned_data['zip_code']

            rep_info_dict = requests.get("https://www.googleapis.com/civicinfo/v2/representatives",
                                         params={"key": key, "address": address}).json()

            if 'error' in rep_info_dict:
                return render(request, 'cc/address.html', {'form': AddressForm, 'valid': False})

            else:
                rep_position = rep_info_dict["offices"]
                rep_info_dict = rep_info_dict["officials"]
                senator = 1
                for rep, position in zip(rep_info_dict, rep_position):
                    if senator == 3:
                        current = position
                        rep['position'] = position
                    elif senator == 4:
                        rep['position'] = current
                    else:
                        rep['position'] = position
                    senator += 1
                logged_in = request.user.is_authenticated
                return render(request, 'cc/RepList.html', {"rep_info_dict": rep_info_dict, "logged_in": logged_in})

    else:
        form = AddressForm()
    return render(request, 'cc/address.html', {'form': form, 'valid': True})


def index(request):
    return render(request, 'cc/index.html')


@login_required
def get_profile(request):
    representatives = request.user.profile.personalList

    templates = request.user.profile.templateList

    return render(request, 'cc/profile.html', {"representatives": representatives, "templates": templates})


@login_required
def add_rep_to_profile(request):
    new_content = request.body.decode()
    new_content = json.loads(new_content)

    old_content = request.user.profile.personalList
    if type(old_content) == list and new_content not in old_content:
        old_content.append(new_content)

        request.user.profile.personalList = old_content
    else:
        request.user.profile.personalList = [new_content]
    request.user.profile.save()
    return HttpResponse()


@login_required
def remove_rep_from_profile(request):
    rep_to_be_removed = request.body.decode()
    rep_to_be_removed = json.loads(rep_to_be_removed)
    request.user.profile.personalList.remove(rep_to_be_removed)
    request.user.profile.save()
    return HttpResponse()


class TemplateCreateView(LoginRequiredMixin, generic.CreateView):
    model = Template
    fields = ['subject', 'body', 'tag']
    success_url = reverse_lazy('cc:viewMessages')


def templates_view(request, tag=None):
    query = tag
    tags = Tag.objects.all()
    logged_in = request.user.is_authenticated
    if query:
        query = Template.objects.filter(tag__tag_name=query)
    else:
        query = Template.objects.all()
    return render(request, "cc/viewTemplates.html", {"templates": query, "tags": tags, "logged_in": logged_in})


@login_required
def add_template_to_profile(request):
    status_code = 200
    try:
        new_template = request.body.decode()
        new_template = json.loads(new_template)

        new_template = Template.objects.get(id=new_template["pk"])

        request.user.profile.templateList.add(new_template)
    except json.JSONDecodeError:
        status_code = 500
    except Template.DoesNotExist:
        status_code = 500

    finally:
        return HttpResponse(status=status_code)


@login_required
def remove_template_from_profile(request):
    template_to_be_removed = request.body.decode()
    template_to_be_removed = json.loads(template_to_be_removed)

    template_to_be_removed = Template.objects.get(id=template_to_be_removed["pk"])
    request.user.profile.templateList.remove(template_to_be_removed)
    request.user.profile.save()
    return HttpResponse()
