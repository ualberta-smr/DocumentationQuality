# Generated by Django 4.1.1 on 2022-10-13 02:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library_name', models.CharField(max_length=50)),
                ('language', models.CharField(max_length=20)),
                ('domain', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(max_length=1000)),
                ('gh_url', models.CharField(blank=True, max_length=100, null=True)),
                ('doc_url', models.CharField(max_length=100)),
                ('method_examples', models.IntegerField(blank=True, null=True, verbose_name='number of methods with documentation examples')),
                ('methods', models.IntegerField(blank=True, null=True, verbose_name='number of methods')),
                ('class_examples', models.IntegerField(blank=True, null=True, verbose_name='number of classes with documentation examples')),
                ('classes', models.IntegerField(blank=True, null=True, verbose_name='number of classes')),
                ('signature_methods', models.IntegerField(blank=True, null=True, verbose_name='number of methods found in documentation')),
                ('signature_classes', models.IntegerField(blank=True, null=True, verbose_name='number of classes found in documentation')),
                ('text_readability_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('text_readability_rating', models.CharField(blank=True, max_length=20, null=True)),
                ('code_readability_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('code_readability_rating', models.CharField(blank=True, max_length=20, null=True)),
                ('navigability', models.CharField(blank=True, max_length=500, null=True)),
                ('last_updated', models.DateTimeField(default=datetime.datetime.utcnow)),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=64)),
                ('library_name', models.CharField(max_length=100)),
                ('years_experience', models.PositiveIntegerField(blank=True, null=True, verbose_name='Years of software development experience')),
                ('familiar', models.BooleanField(blank=True, null=True, verbose_name='familiar')),
                ('general_rating', models.CharField(blank=True, max_length=100, null=True)),
                ('task_list', models.CharField(blank=True, max_length=100, null=True)),
                ('code_examples_methods', models.CharField(blank=True, max_length=100, null=True)),
                ('code_examples_classes', models.CharField(blank=True, max_length=100, null=True)),
                ('text_readability', models.CharField(blank=True, max_length=100, null=True)),
                ('code_readability', models.CharField(blank=True, max_length=100, null=True)),
                ('consistency', models.CharField(blank=True, max_length=100, null=True)),
                ('navigability', models.CharField(blank=True, max_length=100, null=True)),
                ('usefulness', models.CharField(blank=True, max_length=100, null=True)),
                ('where_see', models.CharField(blank=True, max_length=100, null=True)),
                ('general_feedback', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library_name', models.CharField(max_length=50)),
                ('paragraph', models.CharField(max_length=5000)),
                ('task', models.CharField(max_length=100)),
                ('has_example', models.BooleanField(verbose_name='has example')),
                ('example_page', models.CharField(max_length=100)),
                ('html_id', models.CharField(max_length=500)),
            ],
        ),
        migrations.AddConstraint(
            model_name='response',
            constraint=models.UniqueConstraint(fields=('session_key', 'library_name'), name='unique_session_library_combination'),
        ),
    ]
