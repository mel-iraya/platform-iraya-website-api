# Generated manually for Publications app

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('description', models.TextField(blank=True, help_text='Optional description of the publication/brochure')),
                ('pdf_file', models.FileField(help_text='Upload PDF file for this publication/brochure', upload_to='publications/')),
                ('publication_type', models.CharField(choices=[('publication', 'Publication'), ('brochure', 'Brochure')], default='publication', help_text='Select whether this is a publication or brochure', max_length=20)),
                ('published', models.BooleanField(default=False, help_text='Check to make this available for download')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Publication',
                'verbose_name_plural': 'Publications',
                'ordering': ['-created_at'],
            },
        ),
    ]

