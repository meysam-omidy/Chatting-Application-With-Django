# Generated by Django 4.2 on 2023-06-13 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_alter_message_receiver_alter_message_sender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image_message',
            name='receiver',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='image_message',
            name='sender',
            field=models.IntegerField(),
        ),
    ]
