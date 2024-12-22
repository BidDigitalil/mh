from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('קובץ לא נתמך. אנא העלה קובץ PDF או Word.'))

class BaseModel(models.Model):
    """
    מודל בסיס שמכיל שדות משותפים לכל המודלים
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('הערות'))

    class Meta:
        abstract = True

class Therapist(models.Model):
    """
    מודל המייצג מטפל במערכת
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile')
    phone = models.CharField(max_length=20, verbose_name=_('טלפון'))
    specialization = models.CharField(max_length=100, verbose_name=_('התמחות'))
    active = models.BooleanField(default=True, verbose_name=_('פעיל'))

    class Meta:
        verbose_name = _('מטפל')
        verbose_name_plural = _('מטפלים')

    def __str__(self):
        return f'{self.user.get_full_name()}'

class Family(BaseModel):
    """
    מודל המייצג משפחה במערכת
    """
    FAMILY_STATUS_CHOICES = [
        ('married', _('נשואים')),
        ('divorced', _('גרושים')),
        ('single_father', _('אב יחיד')),
        ('single_mother', _('אם יחידה')),
        ('other', _('אחר')),
    ]
    
    family_name = models.CharField(max_length=100, verbose_name=_('שם משפחה'))
    family_status = models.CharField(
        max_length=20, 
        choices=FAMILY_STATUS_CHOICES, 
        default='married', 
        verbose_name=_('סטטוס משפחתי')
    )
    address = models.TextField(verbose_name=_('כתובת'))
    phone_number = models.CharField(max_length=20, verbose_name=_('טלפון ראשי'))
    
    father_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('שם האב'))
    father_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('טלפון האב'))
    father_email = models.EmailField(blank=True, null=True, verbose_name=_('אימייל האב'))
    father_id = models.CharField(max_length=9, blank=True, null=True, verbose_name=_('תעודת זהות האב'))
    
    mother_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('שם האם'))
    mother_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('טלפון האם'))
    mother_email = models.EmailField(blank=True, null=True, verbose_name=_('אימייל האם'))
    mother_id = models.CharField(max_length=9, blank=True, null=True, verbose_name=_('תעודת זהות האם'))

    assigned_therapist = models.ForeignKey(
        Therapist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_families',
        verbose_name=_('מטפל מוקצה')
    )

    class Meta:
        verbose_name = _('משפחה')
        verbose_name_plural = _('משפחות')
        ordering = ['family_name']

    def __str__(self):
        return f'{self.family_name}'

    def clean(self):
        super().clean()
        status = self.family_status

        if status == 'single_father':
            if not all([self.father_name, self.father_phone, self.father_id]):
                raise ValidationError(_('יש למלא את כל פרטי האב עבור אב יחיד'))
        
        elif status == 'single_mother':
            if not all([self.mother_name, self.mother_phone, self.mother_id]):
                raise ValidationError(_('יש למלא את כל פרטי האם עבור אם יחידה'))
        
        elif status in ['married', 'divorced']:
            if not all([self.father_name, self.father_phone, self.father_id,
                       self.mother_name, self.mother_phone, self.mother_id]):
                raise ValidationError(_('יש למלא את פרטי שני ההורים'))

class Child(BaseModel):
    """
    מודל המייצג ילד במערכת
    """
    family = models.ForeignKey(
        Family, 
        on_delete=models.CASCADE, 
        related_name='children', 
        verbose_name=_('משפחה')
    )
    name = models.CharField(max_length=100, verbose_name=_('שם'))
    birth_date = models.DateField(verbose_name=_('תאריך לידה'))
    school = models.CharField(max_length=100, verbose_name=_('בית ספר'))
    grade = models.CharField(max_length=20, verbose_name=_('כיתה'))
    medical_info = models.TextField(blank=True, null=True, verbose_name=_('מידע רפואי'))
    special_needs = models.TextField(blank=True, null=True, verbose_name=_('צרכים מיוחדים'))

    class Meta:
        verbose_name = _('ילד')
        verbose_name_plural = _('ילדים')
        ordering = ['family', 'name']

    def __str__(self):
        return f'{self.name} ({self.family.family_name})'

class Treatment(BaseModel):
    """
    מודל המייצג טיפול במערכת
    """
    TREATMENT_STATUS_CHOICES = [
        ('scheduled', _('מתוכנן')),
        ('in_progress', _('בטיפול')),
        ('completed', _('הושלם')),
        ('cancelled', _('בוטל')),
    ]

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='treatments',
        verbose_name=_('ילד')
    )
    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.SET_NULL,
        null=True,
        related_name='treatments',
        verbose_name=_('מטפל')
    )
    date = models.DateTimeField(verbose_name=_('תאריך ושעה'))
    status = models.CharField(
        max_length=20,
        choices=TREATMENT_STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('סטטוס')
    )
    summary = models.TextField(blank=True, null=True, verbose_name=_('סיכום טיפול'))

    class Meta:
        verbose_name = _('טיפול')
        verbose_name_plural = _('טיפולים')
        ordering = ['-date']

    def __str__(self):
        return f'טיפול: {self.child.name} - {self.date.strftime("%d/%m/%Y %H:%M")}'

class Document(BaseModel):
    """
    מודל המייצג מסמך במערכת
    """
    DOCUMENT_TYPES = [
        ('consent', _('טופס הסכמה')),
        ('treatment', _('טופס טיפול')),
        ('medical', _('מסמך רפואי')),
        ('educational', _('מסמך חינוכי')),
        ('other', _('אחר')),
    ]

    name = models.CharField(max_length=200, verbose_name=_('שם המסמך'))
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES, 
        default='other', 
        verbose_name=_('סוג מסמך')
    )
    file = models.FileField(
        upload_to='documents/',
        validators=[validate_file_extension],
        verbose_name=_('קובץ')
    )
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
        null=True, 
        blank=True,
        verbose_name=_('ילד')
    )
    treatment = models.ForeignKey(
        Treatment,
        on_delete=models.SET_NULL,
        related_name='documents',
        null=True,
        blank=True,
        verbose_name=_('טיפול קשור')
    )

    class Meta:
        verbose_name = _('מסמך')
        verbose_name_plural = _('מסמכים')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.family.family_name}'

    def clean(self):
        super().clean()
        if self.child and self.child.family != self.family:
            raise ValidationError(_('הילד חייב להיות שייך למשפחה הנבחרת'))
        if self.treatment and self.treatment.child != self.child:
            raise ValidationError(_('הטיפול חייב להיות קשור לילד הנבחר'))
