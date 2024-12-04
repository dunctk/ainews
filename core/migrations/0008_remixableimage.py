# Generated by Django 5.1.3 on 2024-12-04 10:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remixable_remixed_as'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemixableImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('remixable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.remixable')),
            ],
        ),
    ]
