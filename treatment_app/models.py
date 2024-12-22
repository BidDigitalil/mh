from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class Family(models.Model):
    PARENTS_TYPE_CHOICES = [
        ('both', _('שני הורים')),
        ('father', _('אב בלבד')),
        ('mother', _('אם בלבד')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('שם משפחה'))
    address = models.CharField(max_length=200, verbose_name=_('כתובת'))
    phone = models.CharField(max_length=20, verbose_name=_('טלפון'))
    email = models.EmailField(verbose_name=_('דוא"ל'), blank=True, null=True)
    parents_type = models.CharField(max_length=10, choices=PARENTS_TYPE_CHOICES, verbose_name=_('סוג הורות'), default='both')
    
    # פרטי האב
    father_name = models.CharField(max_length=100, verbose_name=_('שם האב'), blank=True, null=True)
    father_phone = models.CharField(max_length=20, verbose_name=_('טלפון האב'), blank=True, null=True)
    father_email = models.EmailField(verbose_name=_('דוא"ל האב'), blank=True, null=True)
    
    # פרטי האם
    mother_name = models.CharField(max_length=100, verbose_name=_('שם האם'), blank=True, null=True)
    mother_phone = models.CharField(max_length=20, verbose_name=_('טלפון האם'), blank=True, null=True)
    mother_email = models.EmailField(verbose_name=_('דוא"ל האם'), blank=True, null=True)
    
    # מטפל
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('מטפל'), related_name='families')
    
    # טפסים
    consent_form = models.FileField(
        upload_to='consent_forms/',
        verbose_name=_('טופס הסכמה'),
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    confidentiality_waiver = models.FileField(
        upload_to='confidentiality_waivers/',
        verbose_name=_('טופס ויתור סודיות'),
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    consent_form_date = models.DateField(verbose_name=_('תאריך טופס הסכמה'), blank=True, null=True)
    confidentiality_waiver_date = models.DateField(verbose_name=_('תאריך ויתור סודיות'), blank=True, null=True)

    # פרטים נוספים
    notes = models.TextField(verbose_name=_('הערות'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    def clean(self):
        if self.parents_type == 'father':
            self.mother_name = None
            self.mother_phone = None
            self.mother_email = None
        elif self.parents_type == 'mother':
            self.father_name = None
            self.father_phone = None
            self.father_email = None

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('משפחה')
        verbose_name_plural = _('משפחות')
        ordering = ['name']

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
    
    # New fields for additional child information
    teacher_name = models.CharField(max_length=100, verbose_name=_('שם המורה'), blank=True)
    teacher_phone = models.CharField(max_length=20, verbose_name=_('טלפון המורה'), blank=True)
    school_counselor_name = models.CharField(max_length=100, verbose_name=_('שם היועץ/ת'), blank=True)
    school_counselor_phone = models.CharField(max_length=20, verbose_name=_('טלפון היועץ/ת'), blank=True)
    
    # Additional child-specific details
    allergies = models.TextField(verbose_name=_('אלרגיות'), blank=True)
    medications = models.TextField(verbose_name=_('תרופות'), blank=True)
    special_needs = models.TextField(verbose_name=_('צרכים מיוחדים'), blank=True)
    
    medical_info = models.TextField(verbose_name=_('מידע רפואי'), blank=True)
    notes = models.TextField(verbose_name=_('הערות'), blank=True)
    
    therapist = models.ForeignKey(
        'TherapistProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('מטפל')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    class Meta:
        verbose_name = _('ילד')
        verbose_name_plural = _('ילדים')
        ordering = ['family', 'name']

    def __str__(self):
        return f"{self.name} - {self.family.name}"

    def get_absolute_url(self):
        return reverse('treatment_app:child-detail', kwargs={'pk': self.pk})

class Treatment(models.Model):
    TREATMENT_TYPE_CHOICES = [
        ('individual', _('טיפול פרטני')),
        ('family', _('טיפול משפחתי')),
        ('parent', _('הדרכת הורים')),
    ]

    type = models.CharField(max_length=20, choices=TREATMENT_TYPE_CHOICES, verbose_name=_('סוג טיפול'), default='individual')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='family_treatments', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='treatments', null=True, blank=True)
    date = models.DateTimeField(verbose_name=_('תאריך'))
    therapist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('מטפל'),
        related_name='treatments'
    )
    summary = models.TextField(verbose_name=_('סיכום'))
    next_steps = models.TextField(verbose_name=_('צעדים הבאים'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.family and not self.child:
            raise ValidationError(_('חובה לבחור משפחה או ילד'))
        if self.type == 'individual' and not self.child:
            raise ValidationError(_('בטיפול פרטני חובה לבחור ילד'))
        if self.type == 'family' and not self.family:
            raise ValidationError(_('בטיפול משפחתי חובה לבחור משפחה'))
        if self.child and self.family and self.child.family != self.family:
            raise ValidationError(_('הילד אינו שייך למשפחה זו'))
        if self.child:
            self.family = self.child.family

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('טיפול')
        verbose_name_plural = _('טיפולים')
        ordering = ['-date']

    def __str__(self):
        if self.child:
            return f"{self.child.name} - {self.date.strftime('%d/%m/%Y')}"
        return f"{self.family.name} - {self.date.strftime('%d/%m/%Y')}"

class TherapistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('משתמש'))
    phone = models.CharField(max_length=20, verbose_name=_('טלפון'), blank=True)
    specialization = models.CharField(max_length=100, verbose_name=_('התמחות'), blank=True)
    notes = models.TextField(verbose_name=_('הערות'), blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_('פעיל'))

    class Meta:
        verbose_name = _('פרופיל מטפל')
        verbose_name_plural = _('פרופילי מטפלים')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('medical', _('מסמך רפואי')),
        ('educational', _('מסמך חינוכי')),
        ('psychological', _('מסמך פסיכולוגי')),
        ('financial', _('מסמך פיננסי')),
        ('other', _('אחר')),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name=_('שם המסמך'))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name=_('סוג המסמך'))
    file = models.FileField(upload_to='documents/', verbose_name=_('קובץ'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('הערות'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר בתאריך'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן בתאריך'))

    class Meta:
        verbose_name = _('מסמך')
        verbose_name_plural = _('מסמכים')
        ordering = ['-created_at']

    def __str__(self):
        if self.child:
            return f"{self.name} - {self.child.name}"
        return f"{self.name} - {self.family.name if self.family else _('ללא שיוך')}"

    def clean(self):
        if not self.family and not self.child:
            raise ValidationError(_('חובה לשייך את המסמך למשפחה או לילד'))
        if self.family and self.child and self.child.family != self.family:
            raise ValidationError(_('הילד אינו שייך למשפחה זו'))
        if self.child:
            self.family = self.child.family

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
