# Generated by Django 2.1.8 on 2019-11-22 08:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('buyer', '0005_auto_20191121_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsrelave',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
