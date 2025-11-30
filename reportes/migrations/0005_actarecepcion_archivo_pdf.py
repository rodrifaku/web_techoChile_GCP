from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0004_reportegenerado_archivo'),
    ]

    operations = [
        migrations.AddField(
            model_name='actarecepcion',
            name='archivo_pdf',
            field=models.FileField(blank=True, help_text='PDF del acta almacenado en GCS', null=True, upload_to='actas/'),
        ),
    ]
