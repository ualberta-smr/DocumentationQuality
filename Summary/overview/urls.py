from django.urls import path

from . import views
from . import form_views

app_name = 'overview'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('search/', views.search, name='search'),
    path('create/', views.create, name='create'),
    path('<library_name>', views.overview, name='overview'),
    path('demographics/<library_name>', views.demographics, name='demographics'),
    path('forms/demographics/', views.demographics_form, name='demographics_form'),
    path('forms/general_rating/', views.general_rating, name='general_rating'),
    path('forms/task_list/', views.task_list, name='task_list'),
    path('forms/code_examples/', views.code_examples, name='code_examples'),
    path('forms/readability/', views.readability, name='readability'),
    path('forms/consistency/', views.consistency, name='consistency'),
    path('forms/navigation/', views.navigation, name='navigation'),
    path('forms/general/', views.general, name='general')

]
