from django.urls import path

from . import views

urlpatterns = [
    path('<library_name>', views.overview, name='overview'),
]