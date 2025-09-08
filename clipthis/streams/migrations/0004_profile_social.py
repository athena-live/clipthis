from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0003_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='youtube',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitch',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='kick',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='tiktok',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='instagram',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='x',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='facebook',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='reddit',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='discord',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]

