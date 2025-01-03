# Generated by Django 5.1.4 on 2024-12-22 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment_app', '0003_family_confidentiality_waiver_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='parents_type',
            field=models.CharField(choices=[('both', 'שני הורים'), ('father', 'אב בלבד'), ('mother', 'אם בלבד')], default='both', max_length=10, verbose_name='סוג הורות'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='family',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='family_treatments', to='treatment_app.family'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='type',
            field=models.CharField(choices=[('individual', 'טיפול פרטני'), ('family', 'טיפול משפחתי'), ('parent', 'הדרכת הורים')], default='individual', max_length=20, verbose_name='סוג טיפול'),
        ),
        migrations.AlterField(
            model_name='family',
            name='father_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='דוא"ל האב'),
        ),
        migrations.AlterField(
            model_name='family',
            name='father_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='שם האב'),
        ),
        migrations.AlterField(
            model_name='family',
            name='father_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='טלפון האב'),
        ),
        migrations.AlterField(
            model_name='family',
            name='mother_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='דוא"ל האם'),
        ),
        migrations.AlterField(
            model_name='family',
            name='mother_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='שם האם'),
        ),
        migrations.AlterField(
            model_name='family',
            name='mother_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='טלפון האם'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='child',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to='treatment_app.child'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='date',
            field=models.DateTimeField(verbose_name='תאריך'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='next_steps',
            field=models.TextField(blank=True, null=True, verbose_name='צעדים הבאים'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='summary',
            field=models.TextField(verbose_name='סיכום'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
