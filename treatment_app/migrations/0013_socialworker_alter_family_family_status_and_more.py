# Generated by Django 5.1.4 on 2024-12-26 09:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treatment_app', '0012_remove_family_primary_contact_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialWorker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='שם')),
                ('phone', models.CharField(max_length=20, verbose_name='טלפון')),
                ('email', models.EmailField(max_length=254, verbose_name='דוא"ל')),
                ('organization', models.CharField(blank=True, max_length=100, null=True, verbose_name='ארגון')),
            ],
            options={
                'verbose_name': 'עובד סוציאלי',
                'verbose_name_plural': 'עובדים סוציאליים',
            },
        ),
        migrations.AlterField(
            model_name='family',
            name='family_status',
            field=models.CharField(blank=True, choices=[('intact', 'משפחה שלמה'), ('divorced', 'גרושים'), ('single_parent', 'הורה יחידני'), ('widowed', 'אלמן/אלמנה'), ('other', 'אחר')], max_length=20, null=True, verbose_name='סטטוס משפחתי'),
        ),
        migrations.AddField(
            model_name='family',
            name='social_worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='treatment_app.socialworker', verbose_name='עובד סוציאלי'),
        ),
    ]