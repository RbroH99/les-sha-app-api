# Generated by Django 4.1.13 on 2024-01-23 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_product_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='types',
            field=models.ManyToManyField(blank=True, to='core.product_type'),
        ),
    ]