# Generated by Django 4.2.7 on 2023-11-29 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trait',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
