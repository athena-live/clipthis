from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0002_clip'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paypal', models.CharField(blank=True, help_text='PayPal email or handle (no links)', max_length=120)),
                ('cashapp', models.CharField(blank=True, max_length=120)),
                ('venmo', models.CharField(blank=True, max_length=120)),
                ('btc_address', models.CharField(blank=True, max_length=128)),
                ('eth_address', models.CharField(blank=True, max_length=128)),
                ('sol_address', models.CharField(blank=True, max_length=128)),
                ('other_handle', models.CharField(blank=True, max_length=200)),
                ('payment_note', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
