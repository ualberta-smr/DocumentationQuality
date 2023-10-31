from django.urls import path
from . import views, form_views

urlpatterns = [
    # path("", views.home, name="home"),
    path('', views.landing, name='landing'),
    path('<library_name>', views.overview, name='overview'),
    path('create/', form_views.create, name='create'),
    path('search/', form_views.search, name='search'),

]
