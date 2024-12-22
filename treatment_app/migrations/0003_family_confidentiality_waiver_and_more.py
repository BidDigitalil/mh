# Generated by Django 5.1.4 on 2024-12-22 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment_app', '0002_alter_document_child_alter_document_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='confidentiality_waiver',
            field=models.FileField(blank=True, null=True, upload_to='confidentiality_waivers/', verbose_name='ויתור סודיות'),
        ),
        migrations.AddField(
            model_name='family',
            name='confidentiality_waiver_date',
            field=models.DateField(blank=True, null=True, verbose_name='תאריך ויתור סודיות'),
        ),
        migrations.AddField(
            model_name='family',
            name='consent_form',
            field=models.FileField(blank=True, null=True, upload_to='consent_forms/', verbose_name='טופס הסכמה'),
        ),
        migrations.AddField(
            model_name='family',
            name='consent_form_date',
            field=models.DateField(blank=True, null=True, verbose_name='תאריך טופס הסכמה'),
        ),
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='דוא"ל'),
        ),
    ]
