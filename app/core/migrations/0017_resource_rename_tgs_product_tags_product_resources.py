# Generated by Django 4.1.13 on 2024-01-29 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_tag_product_tgs'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.RenameField(
            model_name='product',
            old_name='tgs',
            new_name='tags',
        ),
        migrations.AddField(
            model_name='product',
            name='resources',
            field=models.ManyToManyField(blank=True, to='core.resource'),
        ),
    ]