from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="input"),
    path('input', views.get_input, name="output"),
    #path('portnode', views.SubForm_process)
]