# Generated by Django 5.1.4 on 2024-12-26 09:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment_app', '0009_treatment_actual_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='family_status',
            field=models.CharField(choices=[('married', 'נשואים'), ('divorced', 'גרושים'), ('single_parent', 'הורה יחידני'), ('separated', 'פרודים'), ('other', 'אחר')], default='married', max_length=20, verbose_name='סטטוס משפחתי'),
        ),
        migrations.AddField(
            model_name='family',
            name='father_consent_form',
            field=models.FileField(blank=True, null=True, upload_to='consent_forms/father/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])], verbose_name='טופס הסכמה אב'),
        ),
        migrations.AddField(
            model_name='family',
            name='father_consent_form_date',
            field=models.DateField(blank=True, null=True, verbose_name='תאריך טופס הסכמה אב'),
        ),
        migrations.AddField(
            model_name='family',
            name='mother_consent_form',
            field=models.FileField(blank=True, null=True, upload_to='consent_forms/mother/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])], verbose_name='טופס הסכמה אם'),
        ),
        migrations.AddField(
            model_name='family',
            name='mother_consent_form_date',
            field=models.DateField(blank=True, null=True, verbose_name='תאריך טופס הסכמה אם'),
        ),
        migrations.AddField(
            model_name='family',
            name='social_worker_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='דוא״ל העו״ס'),
        ),
        migrations.AddField(
            model_name='family',
            name='social_worker_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='שם העו״ס'),
        ),
        migrations.AddField(
            model_name='family',
            name='social_worker_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='טלפון העו״ס'),
        ),
    ]
