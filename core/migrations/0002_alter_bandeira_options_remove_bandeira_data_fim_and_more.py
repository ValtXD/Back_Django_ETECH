# Generated by Django 5.2.1 on 2025-05-17 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bandeira',
            options={},
        ),
        migrations.RemoveField(
            model_name='bandeira',
            name='data_fim',
        ),
        migrations.RemoveField(
            model_name='bandeira',
            name='data_inicio',
        ),
        migrations.RemoveField(
            model_name='bandeira',
            name='vigente',
        ),
        migrations.AlterField(
            model_name='bandeira',
            name='cor',
            field=models.CharField(choices=[('verde', 'Verde'), ('amarela', 'Amarela'), ('vermelha1', 'Vermelha - Patamar 1'), ('vermelha2', 'Vermelha - Patamar 2')], max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='bandeira',
            name='descricao',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='bandeira',
            name='valor_adicional',
            field=models.DecimalField(decimal_places=5, max_digits=6),
        ),
    ]
