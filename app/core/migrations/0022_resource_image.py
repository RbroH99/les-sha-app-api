# Generated by Django 4.1.13 on 2024-02-03 17:47

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.image_file_path),
        ),
    ]
