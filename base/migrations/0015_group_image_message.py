# Generated by Django 4.2 on 2023-06-15 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_image_message_receiver_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='group_image_message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('sender', models.IntegerField()),
                ('receiver', models.IntegerField()),
                ('seen', models.CharField(max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
