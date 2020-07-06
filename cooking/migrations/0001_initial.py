# Generated by Django 3.0.7 on 2020-07-06 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient_name', models.CharField(max_length=50)),
                ('ingredient_description', models.CharField(max_length=300)),
                ('ingredient_effect', models.CharField(max_length=20)),
                ('ingredient_color', models.CharField(max_length=10)),
                ('ingredient_weight', models.IntegerField()),
                ('ingredient_coefficient', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'db_table': 'soup_ingredient_info',
            },
        ),
    ]
