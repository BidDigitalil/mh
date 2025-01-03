# Generated by Django 5.1.4 on 2024-12-22 11:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='שם הילד')),
                ('birth_date', models.DateField(verbose_name='תאריך לידה')),
                ('gender', models.CharField(choices=[('male', 'זכר'), ('female', 'נקבה')], max_length=10, verbose_name='מגדר')),
                ('school', models.CharField(blank=True, max_length=100, verbose_name='בית ספר')),
                ('grade', models.CharField(blank=True, max_length=20, verbose_name='כיתה')),
                ('medical_info', models.TextField(blank=True, verbose_name='מידע רפואי')),
                ('notes', models.TextField(blank=True, verbose_name='הערות')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='עודכן ב')),
            ],
            options={
                'verbose_name': 'ילד',
                'verbose_name_plural': 'ילדים',
                'ordering': ['family', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='שם משפחה')),
                ('address', models.CharField(max_length=200, verbose_name='כתובת')),
                ('phone', models.CharField(max_length=20, verbose_name='טלפון')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='אימייל')),
                ('father_name', models.CharField(blank=True, max_length=100, verbose_name='שם האב')),
                ('father_phone', models.CharField(blank=True, max_length=20, verbose_name='טלפון האב')),
                ('father_email', models.EmailField(blank=True, max_length=254, verbose_name='אימייל האב')),
                ('mother_name', models.CharField(blank=True, max_length=100, verbose_name='שם האם')),
                ('mother_phone', models.CharField(blank=True, max_length=20, verbose_name='טלפון האם')),
                ('mother_email', models.EmailField(blank=True, max_length=254, verbose_name='אימייל האם')),
                ('notes', models.TextField(blank=True, verbose_name='הערות')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='עודכן ב')),
                ('therapist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='families', to=settings.AUTH_USER_MODEL, verbose_name='מטפל אחראי')),
            ],
            options={
                'verbose_name': 'משפחה',
                'verbose_name_plural': 'משפחות',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='שם המסמך')),
                ('document_type', models.CharField(choices=[('medical', 'מסמך רפואי'), ('educational', 'מסמך חינוכי'), ('psychological', 'מסמך פסיכולוגי'), ('treatment', 'סיכום טיפול'), ('other', 'אחר')], max_length=20, verbose_name='סוג מסמך')),
                ('file', models.FileField(upload_to='documents/', verbose_name='קובץ')),
                ('notes', models.TextField(blank=True, verbose_name='הערות')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='עודכן ב')),
                ('child', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='treatment_app.child', verbose_name='ילד')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='treatment_app.family', verbose_name='משפחה')),
            ],
            options={
                'verbose_name': 'מסמך',
                'verbose_name_plural': 'מסמכים',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='child',
            name='family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='treatment_app.family', verbose_name='משפחה'),
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='תאריך הטיפול')),
                ('summary', models.TextField(verbose_name='סיכום הטיפול')),
                ('next_steps', models.TextField(blank=True, verbose_name='המשך טיפול')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='נוצר ב')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='עודכן ב')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to='treatment_app.child', verbose_name='ילד')),
                ('therapist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='treatments', to=settings.AUTH_USER_MODEL, verbose_name='מטפל')),
            ],
            options={
                'verbose_name': 'טיפול',
                'verbose_name_plural': 'טיפולים',
                'ordering': ['-date'],
            },
        ),
    ]
