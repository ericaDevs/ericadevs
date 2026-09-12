from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Projects', '0002_rename_technologies_project_languages'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='languages',
            new_name='technologies',
        ),
    ]
