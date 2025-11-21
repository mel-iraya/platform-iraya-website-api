# Generated manually for Publications app - Remove slug field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_add_event_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='slug',
        ),
    ]

