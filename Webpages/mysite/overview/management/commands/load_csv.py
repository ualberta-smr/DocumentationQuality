import csv
import os

from django.core.management import BaseCommand
from django.utils import timezone
from overview.models import Task


# Adapted from: https://betterprogramming.pub/3-techniques-for-importing-large-csv-files-into-a-django-app-2b6e5e47dba0
# Author: Sebastian Opałczyński
# Taken by: Henry Tang at 14:48 MDT
class Command(BaseCommand):
    help = "Loads task data from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = os.path.normpath(options["file_path"])
        with open(file_path, "r", encoding="utf-8", newline="") as csv_file:
            data = csv.reader(csv_file)
            next(data, None)
            tasks = []
            for row in data:
                tasks.append(Task(
                    library_name=row[0],
                    paragraph=row[1],
                    task=row[2],
                    has_example=row[3]
                ))
                if len(tasks) > 500:
                    Task.objects.bulk_create(tasks)
                    tasks = []
            if tasks:
                Task.objects.bulk_create(tasks)
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time - start_time).total_seconds()} seconds."
            )
        )
