# Generated by Django 4.0 on 2022-03-03 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dijkstra_alg', '0005_delete_node'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('From_Node0', models.IntegerField()),
                ('Route_Freq', models.FloatField()),
                ('Impedence0', models.FloatField()),
                ('node_identification', models.TextField()),
                ('To_Node0', models.IntegerField()),
                ('Name0', models.TextField()),
                ('Length0', models.FloatField()),
            ],
        ),
    ]
