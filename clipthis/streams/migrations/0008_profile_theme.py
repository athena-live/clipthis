from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0007_billing_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='theme',
            field=models.CharField(choices=[('dark', 'Dark'), ('light', 'Light')], default='dark', max_length=10),
        ),
    ]

