# Generated by Django 4.1.7 on 2024-01-05 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfimapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='calificacion',
            name='nota',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='conceptopago',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='curso',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='detallematricula',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='docente',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='estadoacademico',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='estadoboletap',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='estadocivil',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='maestria',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='matricula',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='periodo',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reporteecoconceptopago',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reporteeconomico',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='seccion',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='sede',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tipodocumento',
            name='ipUsuario',
            field=models.CharField(blank=True, default='192.168.0.122', max_length=100, null=True),
        ),
    ]
