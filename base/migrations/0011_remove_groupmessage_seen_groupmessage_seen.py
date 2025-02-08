# Generated by Django 4.2 on 2023-05-12 21:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_group_is_public'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupmessage',
            name='seen',
        ),
        migrations.AddField(
            model_name='groupmessage',
            name='seen',
            field=models.ManyToManyField(null=True, related_name='seen', to=settings.AUTH_USER_MODEL),
        ),
    ]
