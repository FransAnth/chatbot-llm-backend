# Generated by Django 5.0.6 on 2024-10-29 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chats', '0002_chatconfiguration_chatconversation_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatconfiguration',
            name='user_id',
            field=models.TextField(max_length=200, unique=True),
        ),
    ]
