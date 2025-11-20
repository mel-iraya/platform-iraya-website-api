# Generated migration to remove order, caption, and is_cover fields from PostImage

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postimage',
            name='caption',
        ),
        migrations.RemoveField(
            model_name='postimage',
            name='is_cover',
        ),
        migrations.RemoveField(
            model_name='postimage',
            name='order',
        ),
        migrations.AlterModelOptions(
            name='postimage',
            options={'ordering': ['created_at'], 'verbose_name': 'Post Image', 'verbose_name_plural': 'Post Images'},
        ),
    ]

