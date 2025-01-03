# Generated by Django 5.1.4 on 2024-12-22 13:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment_app', '0005_alter_family_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TherapistProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='טלפון')),
                ('specialization', models.CharField(blank=True, max_length=100, verbose_name='התמחות')),
                ('notes', models.TextField(blank=True, verbose_name='הערות')),
                ('is_active', models.BooleanField(default=True, verbose_name='פעיל')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='משתמש')),
            ],
            options={
                'verbose_name': 'פרופיל מטפל',
                'verbose_name_plural': 'פרופילי מטפלים',
            },
        ),
    ]
