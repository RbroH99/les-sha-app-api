# Generated by Django 4.1.13 on 2024-01-29 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_resource_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
