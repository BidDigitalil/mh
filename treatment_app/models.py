"""
Django models for the Treatment Center Management System.

This module defines the core data models for managing families, children, 
treatments, therapist profiles, and documents in a treatment center.

Key Models:
- Family: Represents a family unit with contact and parental information
- Child: Stores details about individual children in a family
- Treatment: Tracks treatment sessions and their details
- TherapistProfile: Extends the default User model for therapists
- Document: Manages various types of documents related to families and children

The models use Django's built-in translation and validation features to 
provide a robust and localized data management system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time, timedelta

class Family(models.Model):
    """
    Represents a family unit in the treatment center management system.
    
    Stores comprehensive information about a family, including:
    - Basic contact details
    - Parental information
    - Associated therapist
    - Consent and confidentiality documents
    
    Supports different family structures (both parents, single parent)
    and maintains a record of important family-related documents.
    """
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
    """
    Represents a child within a family in the treatment center.
    
    Captures detailed information about a child, including:
    - Basic personal details (name, birth date, gender)
    - School and educational information
    - Medical and health-related details
    - Associated therapist and family
    
    Provides a comprehensive profile for tracking a child's 
    treatment and personal information.
    """
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

    def save(self, *args, **kwargs):
        # If no therapist is set, use the family's therapist
        if not self.therapist and self.family and self.family.therapist:
            self.therapist = self.family.therapist
        
        super().save(*args, **kwargs)

    def clean(self):
        # Validation to ensure therapist consistency
        if self.family and self.family.therapist and self.therapist and self.therapist != self.family.therapist:
            raise ValidationError({
                'therapist': _('הטיפול של הילד צריך להיות זהה לטיפול של המשפחה')
            })

    class Meta:
        verbose_name = _('ילד')
        verbose_name_plural = _('ילדים')
        ordering = ['family', 'name']

    def __str__(self):
        return f"{self.name} - {self.family.name}"

    def get_absolute_url(self):
        return reverse('treatment_app:child-detail', kwargs={'pk': self.pk})

class Treatment(models.Model):
    """
    Represents a treatment session for a child or family.
    
    Tracks treatment details including scheduling, status, and summary.
    Supports both individual child treatments and family-level interventions.
    """
    class TreatmentType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('טיפול פרטני')
        GROUP = 'GROUP', _('טיפול קבוצתי')
        FAMILY = 'FAMILY', _('טיפול משפחתי')
        CONSULTATION = 'CONSULTATION', _('התייעצות')

    class TreatmentStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('מתוכנן')
        COMPLETED = 'COMPLETED', _('הושלם')
        MISSED = 'MISSED', _('לא התקיים')
        PENDING_SUMMARY = 'PENDING_SUMMARY', _('ממתין לסיכום')

    # Relationships
    family = models.ForeignKey('Family', on_delete=models.CASCADE, related_name='treatments', null=True, blank=True, verbose_name=_('משפחה'))
    child = models.ForeignKey('Child', on_delete=models.CASCADE, related_name='treatments', null=True, blank=True, verbose_name=_('ילד'))
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='treatments', verbose_name=_('מטפל'))

    # Treatment Details
    type = models.CharField(max_length=20, choices=TreatmentType.choices, default=TreatmentType.INDIVIDUAL, verbose_name=_('סוג טיפול'))
    status = models.CharField(max_length=20, choices=TreatmentStatus.choices, default=TreatmentStatus.SCHEDULED, verbose_name=_('סטטוס'))

    # Scheduling
    scheduled_date = models.DateField(null=True, blank=True, verbose_name=_('תאריך מתוכנן'))
    start_time = models.TimeField(null=True, blank=True, default=time(8, 0), verbose_name=_('שעת התחלה'))
    end_time = models.TimeField(null=True, blank=True, default=time(9, 0), verbose_name=_('שעת סיום'))

    # Treatment Summary
    summary = models.TextField(null=True, blank=True, verbose_name=_('סיכום טיפול'))
    next_steps = models.TextField(null=True, blank=True, verbose_name=_('המשך טיפול'))

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('נוצר ב'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('עודכן ב'))

    class Meta:
        verbose_name = _('טיפול')
        verbose_name_plural = _('טיפולים')
        ordering = ['-scheduled_date', 'start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(family__isnull=False) | models.Q(child__isnull=False),
                name='require_family_or_child'
            )
        ]

    def __str__(self):
        """
        String representation of the treatment.
        Prioritizes child name, then family name.
        """
        client_name = self.child.name if self.child else self.family.name if self.family else _('לקוח לא מזוהה')
        return f"{client_name} - {self.get_type_display()} ({self.scheduled_date})"

    def get_absolute_url(self):
        """
        Returns the URL for viewing this treatment's details.
        """
        return reverse('treatment_app:treatment-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        Override save method to automatically update treatment status.
        """
        # Auto-update status based on summary
        if self.summary and self.status == self.TreatmentStatus.SCHEDULED:
            self.status = self.TreatmentStatus.COMPLETED
        
        # Ensure end time is after start time
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            self.end_time = datetime.combine(datetime.today(), self.start_time) + timedelta(hours=1)
        
        super().save(*args, **kwargs)

    def is_past_due(self):
        """
        Check if the treatment is past due.
        """
        return (self.scheduled_date and self.scheduled_date < timezone.now().date() and 
                self.status == self.TreatmentStatus.SCHEDULED)

    def needs_summary(self):
        """
        Check if the treatment requires a summary.
        Returns True if:
        1. Treatment is past due
        2. No summary has been written
        """
        from django.utils import timezone
        
        # Check if treatment is past due
        if not self.scheduled_date:
            return False
        
        is_past_due = self.scheduled_date < timezone.now().date()
        
        # Check if summary is missing
        summary_missing = not self.summary
        
        return is_past_due and summary_missing

    def get_status_display_with_summary_warning(self):
        """
        Returns the status with an additional warning if summary is needed.
        """
        status = self.get_status_display()
        if self.needs_summary():
            status += " (נדרש סיכום!)"
        return status

class TherapistProfile(models.Model):
    """
    Extended profile for therapists in the treatment center.
    
    Augments Django's built-in User model with:
    - Contact information
    - Professional specialization
    - Additional notes
    - Active status
    
    Provides a more comprehensive view of therapist details.
    """
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
    """
    Manages documents associated with families or children.
    
    Supports various document types:
    - Medical
    - Educational
    - Psychological
    - Financial
    - Other
    
    Allows document upload and tracking with:
    - Flexible association (family or child)
    - Document metadata
    - Validation rules
    
    Helps in maintaining a comprehensive document repository.
    """
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
