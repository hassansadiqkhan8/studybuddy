# Generated by Django 5.0.7 on 2024-09-28 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='message',
            name='body',
            field=models.TextField(blank=True, null=True),
        ),
    ]
