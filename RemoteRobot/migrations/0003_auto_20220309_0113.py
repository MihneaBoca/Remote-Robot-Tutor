# Generated by Django 3.2.9 on 2022-03-09 01:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RemoteRobot', '0002_alter_code_mac_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='code',
            old_name='mac_address',
            new_name='password',
        ),
        migrations.RemoveField(
            model_name='code',
            name='connection_type',
        ),
    ]