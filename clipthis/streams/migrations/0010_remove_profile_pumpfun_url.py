from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0009_profile_pumpfun.py'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='pumpfun_url',
        ),
    ]

