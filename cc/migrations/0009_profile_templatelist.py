# Generated by Django 3.1.1 on 2020-11-05 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cc', '0008_auto_20201103_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='templateList',
            field=models.ManyToManyField(to='cc.Template'),
        ),
    ]
