from django.urls import path

from . import views
from . import form_views

app_name = 'overview'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('<library_name>', views.overview, name='overview'),
    path('demographics/<library_name>', views.demographics, name='demographics'),
    path('search/', form_views.search, name='search'),
    path('create/', form_views.create, name='create'),
    path('forms/demographics/', form_views.demographics_form, name='demographics_form'),
    path('forms/general_rating/', form_views.general_rating, name='general_rating'),
    path('forms/task_list/', form_views.task_list, name='task_list'),
    path('forms/method_examples/', form_views.method_examples, name='method_examples'),
    path('forms/class_examples/', form_views.class_examples, name='class_examples'),
    path('forms/text_readability/', form_views.text_readability, name='text_readability'),
    path('forms/code_readability/', form_views.code_readability, name='code_readability'),
    path('forms/consistency/', form_views.consistency, name='consistency'),
    path('forms/navigation/', form_views.navigation, name='navigation'),
    path('forms/general/', form_views.general, name='general')

]
