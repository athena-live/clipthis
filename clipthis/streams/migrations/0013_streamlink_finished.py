from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0012_clip_youtube_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamlink',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]

