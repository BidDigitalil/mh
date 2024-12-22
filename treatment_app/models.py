from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Family(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('שם משפחה'))
    address = models.CharField(max_length=200, verbose_name=_('כתובת'))
    phone = models.CharField(max_length=20, verbose_name=_('טלפון'))
    email = models.EmailField(verbose_name=_('אימייל'), blank=True)
    
    # פרטי האב
    father_name = models.CharField(max_length=100, verbose_name=_('שם האב'), blank=True)
    father_phone = models.CharField(max_length=20, verbose_name=_('טלפון האב'), blank=True)
    father_email = models.EmailField(verbose_name=_('אימייל האב'), blank=True)
    
    # פרטי האם
    mother_name = models.CharField(max_length=100, verbose_name=_('שם האם'), blank=True)
    mother_phone = models.CharField(max_length=20, verbose_name=_('טלפון האם'), blank=True)
    mother_email = models.EmailField(verbose_name=_('אימייל האם'), blank=True)
    
    therapist = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_('מטפל אחראי'),
        related_name='families'
    )
    notes = models.TextField(verbose_name=_('הערות'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    class Meta:
        verbose_name = _('משפחה')
        verbose_name_plural = _('משפחות')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('treatment_app:family-detail', kwargs={'pk': self.pk})

class Child(models.Model):
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('משפחה')
    )
    name = models.CharField(max_length=100, verbose_name=_('שם הילד'))
    birth_date = models.DateField(verbose_name=_('תאריך לידה'))
    gender = models.CharField(
        max_length=10,
        choices=[('male', _('זכר')), ('female', _('נקבה'))],
        verbose_name=_('מגדר')
    )
    school = models.CharField(max_length=100, verbose_name=_('בית ספר'), blank=True)
    grade = models.CharField(max_length=20, verbose_name=_('כיתה'), blank=True)
    medical_info = models.TextField(verbose_name=_('מידע רפואי'), blank=True)
    notes = models.TextField(verbose_name=_('הערות'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    class Meta:
        verbose_name = _('ילד')
        verbose_name_plural = _('ילדים')
        ordering = ['family', 'name']

    def __str__(self):
        return f"{self.name} - {self.family.name}"

class Treatment(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='treatments',
        verbose_name=_('ילד')
    )
    date = models.DateTimeField(verbose_name=_('תאריך הטיפול'))
    therapist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('מטפל'),
        related_name='treatments'
    )
    summary = models.TextField(verbose_name=_('סיכום הטיפול'))
    next_steps = models.TextField(verbose_name=_('המשך טיפול'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    class Meta:
        verbose_name = _('טיפול')
        verbose_name_plural = _('טיפולים')
        ordering = ['-date']

    def __str__(self):
        return f"{self.child.name} - {self.date.strftime('%d/%m/%Y')}"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('medical', _('מסמך רפואי')),
        ('educational', _('מסמך חינוכי')),
        ('psychological', _('מסמך פסיכולוגי')),
        ('treatment', _('סיכום טיפול')),
        ('other', _('אחר')),
    ]

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('משפחה')
    )
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('ילד'),
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name=_('שם המסמך'))
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        verbose_name=_('סוג מסמך')
    )
    file = models.FileField(upload_to='documents/', verbose_name=_('קובץ'))
    notes = models.TextField(verbose_name=_('הערות'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    class Meta:
        verbose_name = _('מסמך')
        verbose_name_plural = _('מסמכים')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.family.name}"
