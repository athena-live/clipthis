from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0005_ratings'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='plan',
            field=models.CharField(choices=[('free', 'Free'), ('plus', 'Plus'), ('premium', 'Premium')], default='free', max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='plan_set_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]

