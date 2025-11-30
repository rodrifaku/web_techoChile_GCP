from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0003_reportegenerado'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportegenerado',
            name='archivo',
            field=models.FileField(blank=True, help_text='Archivo PDF almacenado en GCS', null=True, upload_to='reportes/'),
        ),
    ]
