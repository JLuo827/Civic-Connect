from django.urls import path

from . import views

app_name = 'cc'

urlpatterns = [
    path('', views.index, name='index'),
    path('address/', views.get_rep, name='address'),
    path('profile/', views.get_profile, name='profile'),
    path('address/RepList/', views.AddressView.as_view(), name='RepList'),
    path('submitMessage/', views.TemplateCreateView.as_view(), name='submitMessage'),
    path('viewMessages/', views.templates_view, name="viewMessages"),
    path('viewMessages/<str:tag>', views.templates_view, name='viewMessages'),
    path('profile/add', views.add_rep_to_profile, name='add_rep'),
    path('profile/removeRep', views.remove_rep_from_profile, name='remove_rep'),
    path('profile/addMessage', views.add_template_to_profile, name='add_message'),
    path('profile/removeMessage', views.remove_template_from_profile, name='remove_message')
]
