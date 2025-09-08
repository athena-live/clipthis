from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0011_streamlink_youtube_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='clip',
            name='yt_video_id',
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_title',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_channel',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_thumbnail',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_view_count',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_like_count',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_duration',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='clip',
            name='yt_cached_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

