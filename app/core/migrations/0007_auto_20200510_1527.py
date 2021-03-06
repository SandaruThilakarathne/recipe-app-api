# Generated by Django 3.0.6 on 2020-05-10 15:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_recipe_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='time_miniutes',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='title',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
    ]
