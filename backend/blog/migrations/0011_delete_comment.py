from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_alter_postimage_order'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]

