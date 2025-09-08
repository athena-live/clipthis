from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0006_profile_plan'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(choices=[('plus', 'Plus'), ('premium', 'Premium')], max_length=20)),
                ('amount_cents', models.IntegerField()),
                ('currency', models.CharField(default='usd', max_length=10)),
                ('stripe_session_id', models.CharField(blank=True, db_index=True, max_length=255)),
                ('stripe_payment_intent', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('canceled', 'Canceled'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

