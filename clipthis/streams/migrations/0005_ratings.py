from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0004_profile_social'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stream_ratings', to='streams.streamlink')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stream_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('stream', 'user')},
            },
        ),
        migrations.CreateModel(
            name='ClipRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clip_ratings', to='streams.clip')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clip_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('clip', 'user')},
            },
        ),
    ]

