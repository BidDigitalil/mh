from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    is_therapist = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    
class Family(models.Model):
    name = models.CharField(_("שם משפחה"), max_length=100)
    phone = models.CharField(_("טלפון"), max_length=20)
    address = models.TextField(_("כתובת"))
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='families')
    consent_form = models.FileField(_("טופס הסכמה"), upload_to='consent_forms/', null=True, blank=True)
    treatment_form = models.FileField(_("טופס טיפול"), upload_to='treatment_forms/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("משפחה")
        verbose_name_plural = _("משפחות")

class Child(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(_("שם"), max_length=100)
    birth_date = models.DateField(_("תאריך לידה"))
    school = models.CharField(_("בית ספר"), max_length=100, blank=True)
    contact_person = models.CharField(_("איש קשר"), max_length=100, blank=True)
    medications = models.TextField(_("תרופות"), blank=True)
    therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patients')
    notes = models.TextField(_("הערות"), blank=True)

    class Meta:
        verbose_name = _("ילד")
        verbose_name_plural = _("ילדים")

class Document(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    file = models.FileField(_("קובץ"), upload_to='documents/')
    name = models.CharField(_("שם המסמך"), max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("מסמך")
        verbose_name_plural = _("מסמכים")

class Treatment(models.Model):
    TREATMENT_TYPES = [
        ('family', _('משפחתי')),
        ('child', _('ילד')),
        ('parent', _('הורה')),
    ]

    type = models.CharField(_("סוג טיפול"), max_length=10, choices=TREATMENT_TYPES)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='treatments')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='treatments', null=True, blank=True)
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_treatments')
    date = models.DateTimeField(_("תאריך ושעה"))
    summary = models.TextField(_("סיכום פגישה"))
    basic_questions = models.JSONField(_("שאלות בסיסיות"), default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("טיפול")
        verbose_name_plural = _("טיפולים")
