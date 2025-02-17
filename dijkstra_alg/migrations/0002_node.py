# Generated by Django 4.0 on 2022-03-03 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dijkstra_alg', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_node', models.IntegerField(max_length=15)),
                ('to_node', models.IntegerField(max_length=15)),
                ('length', models.FloatField(max_length=15)),
            ],
            options={
                'verbose_name': 'Port Node',
                'verbose_name_plural': 'Port Nodes',
                'db_table': 'port_nodes',
                'managed': True,
            },
        ),
    ]
