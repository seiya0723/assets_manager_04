# Generated by Django 3.1.2 on 2021-07-10 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='income',
            field=models.BooleanField(default=False, verbose_name='収支(True=収入,False=支出)'),
        ),
    ]