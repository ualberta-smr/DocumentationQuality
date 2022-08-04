from django.urls import path

from . import views

app_name = 'overview'

urlpatterns = [
    path('<library_name>', views.overview, name='overview'),
    path('forms/demographics/', views.demographics, name='demographics'),
    path('forms/general/', views.general, name='general')

]
