# Generated by Django 3.1.7 on 2022-03-24 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20220323_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisments',
            name='owner',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='app.user'),
            preserve_default=False,
        ),
    ]
