# Generated manually for Publications app - Add event fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='event_name',
            field=models.CharField(blank=True, help_text="Name of the event or conference (e.g., 'EAGE Annual')", max_length=255),
        ),
        migrations.AddField(
            model_name='publication',
            name='location',
            field=models.CharField(blank=True, help_text="Location or venue (e.g., 'Vienna, Austria')", max_length=255),
        ),
        migrations.AddField(
            model_name='publication',
            name='event_date',
            field=models.DateField(blank=True, help_text='Date of the event or publication (e.g., June 2023)', null=True),
        ),
    ]

