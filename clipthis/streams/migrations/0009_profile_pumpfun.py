from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0008_profile_theme'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pumpfun_handle',
            field=models.CharField(blank=True, help_text='pump.fun handle (no links)', max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='pumpfun_url',
            field=models.URLField(blank=True, help_text='pump.fun URL (optional)'),
        ),
    ]

