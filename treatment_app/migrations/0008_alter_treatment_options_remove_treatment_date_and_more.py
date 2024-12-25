# Generated by Django 5.1.4 on 2024-12-25 14:11

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment_app', '0007_child_allergies_child_medications_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='treatment',
            options={'ordering': ['-scheduled_date', 'start_time'], 'verbose_name': 'טיפול', 'verbose_name_plural': 'טיפולים'},
        ),
        migrations.RemoveField(
            model_name='treatment',
            name='date',
        ),
        migrations.AddField(
            model_name='treatment',
            name='end_time',
            field=models.TimeField(blank=True, default=datetime.time(9, 0), null=True, verbose_name='שעת סיום'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='scheduled_date',
            field=models.DateField(blank=True, null=True, verbose_name='תאריך מתוכנן'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='start_time',
            field=models.TimeField(blank=True, default=datetime.time(8, 0), null=True, verbose_name='שעת התחלה'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='status',
            field=models.CharField(choices=[('SCHEDULED', 'מתוכנן'), ('COMPLETED', 'הושלם'), ('MISSED', 'לא התקיים'), ('PENDING_SUMMARY', 'ממתין לסיכום')], default='SCHEDULED', max_length=20, verbose_name='סטטוס'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='child',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to='treatment_app.child', verbose_name='ילד'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='family',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to='treatment_app.family', verbose_name='משפחה'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='next_steps',
            field=models.TextField(blank=True, null=True, verbose_name='המשך טיפול'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='summary',
            field=models.TextField(blank=True, null=True, verbose_name='סיכום טיפול'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='type',
            field=models.CharField(choices=[('INDIVIDUAL', 'טיפול פרטני'), ('GROUP', 'טיפול קבוצתי'), ('FAMILY', 'טיפול משפחתי'), ('CONSULTATION', 'התייעצות')], default='INDIVIDUAL', max_length=20, verbose_name='סוג טיפול'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='עודכן ב'),
        ),
        migrations.AddConstraint(
            model_name='treatment',
            constraint=models.CheckConstraint(condition=models.Q(('family__isnull', False), ('child__isnull', False), _connector='OR'), name='require_family_or_child'),
        ),
    ]
