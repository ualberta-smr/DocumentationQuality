from django.shortcuts import render
from .models import Task


def overview(request, library_name):
    task_list = Task.objects.filter(library_name=library_name)
    context = {
        'task_list': task_list
    }
    return render(request, 'overview/overview.html', context)
