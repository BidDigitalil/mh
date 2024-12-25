from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Div, HTML

from .models import Family, Child, Treatment, Document, TherapistProfile

def validate_weekday(value):
    """
    Validate that the treatment is scheduled on a weekday (Sunday to Thursday)
    """
    if value.weekday() > 4:  # Friday or Saturday
        raise ValidationError(_('טיפולים מתוכננים רק בימים ראשון עד חמישי'))

def validate_treatment_start_time(value):
    """
    Validate treatment start time (8:00 AM)
    """
    min_time = datetime.strptime('08:00', '%H:%M').time()
    if value < min_time:
        raise ValidationError(_('שעת התחלה מוקדמת מדי. טיפולים מתחילים מ-08:00'))

def validate_treatment_end_time(value):
    """
    Validate treatment end time (8:00 PM)
    """
    max_time = datetime.strptime('20:00', '%H:%M').time()
    if value > max_time:
        raise ValidationError(_('שעת סיום מאוחרת מדי. טיפולים מסתיימים עד 20:00'))

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name', 'phone', 'email', 'address', 'therapist',
                 'father_name', 'father_phone', 'father_email',
                 'mother_name', 'mother_phone', 'mother_email',
                 'consent_form', 'confidentiality_waiver', 'notes']
        widgets = {
            'consent_form': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'confidentiality_waiver': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Get the user from kwargs if passed
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  # חשוב להעלאת קבצים
        
        # If user is not a superuser, make therapist field read-only or hidden
        if user and not user.is_superuser:
            # If editing an existing family, show current therapist but make it non-editable
            if self.instance and self.instance.pk:
                self.fields['therapist'].disabled = True
                self.fields['therapist'].help_text = 'ניתן לשנות מטפל רק על ידי מנהל מערכת'
            else:
                # For new families, hide the therapist field for non-superusers
                self.fields['therapist'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי משפחה'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('therapist', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('phone', css_class='form-group col-md-6 mb-0'),
                    Column('email', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'address',
            ),
            Fieldset(
                _('פרטי האב'),
                Row(
                    Column('father_name', css_class='form-group col-md-4 mb-0'),
                    Column('father_phone', css_class='form-group col-md-4 mb-0'),
                    Column('father_email', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                _('פרטי האם'),
                Row(
                    Column('mother_name', css_class='form-group col-md-4 mb-0'),
                    Column('mother_phone', css_class='form-group col-md-4 mb-0'),
                    Column('mother_email', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                _('טפסים'),
                Row(
                    Column(
                        HTML("""{% if form.instance.consent_form %}
                            <div class="mb-2">
                                <a href="{{ form.instance.consent_form.url }}" class="btn btn-sm btn-success" target="_blank">
                                    <i class="fas fa-file-download"></i> הורד טופס הסכמה קיים
                                </a>
                            </div>
                        {% endif %}"""),
                        'consent_form',
                        css_class='form-group col-md-6 mb-0'
                    ),
                    Column(
                        HTML("""{% if form.instance.confidentiality_waiver %}
                            <div class="mb-2">
                                <a href="{{ form.instance.confidentiality_waiver.url }}" class="btn btn-sm btn-success" target="_blank">
                                    <i class="fas fa-file-download"></i> הורד טופס ויתור סודיות קיים
                                </a>
                            </div>
                        {% endif %}"""),
                        'confidentiality_waiver',
                        css_class='form-group col-md-6 mb-0'
                    ),
                    css_class='form-row'
                ),
            ),
            'notes',
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        consent_form = cleaned_data.get('consent_form')
        confidentiality_waiver = cleaned_data.get('confidentiality_waiver')

        # Set dates when files are uploaded
        if consent_form:
            cleaned_data['consent_form_date'] = timezone.now().date()
        if confidentiality_waiver:
            cleaned_data['confidentiality_waiver_date'] = timezone.now().date()

        return cleaned_data

class ChildForm(forms.ModelForm):
    therapist = forms.ModelChoiceField(
        queryset=TherapistProfile.objects.filter(is_active=True), 
        required=False, 
        label=_('מטפל')
    )

    class Meta:
        model = Child
        fields = [
            'name', 'birth_date', 'gender', 'school', 'grade', 
            'teacher_name', 'teacher_phone', 
            'school_counselor_name', 'school_counselor_phone',
            'allergies', 'medications', 'special_needs', 
            'medical_info', 'notes', 'therapist', 'family'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher_name': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher_phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'school_counselor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'school_counselor_phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'special_needs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'family': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If a specific family is passed in initial, set it as the default
        if 'initial' in kwargs and 'family' in kwargs['initial']:
            self.fields['family'].initial = kwargs['initial']['family']
            self.fields['family'].widget.attrs['readonly'] = True

        # If not a superuser, modify choices
        if user and not user.is_superuser:
            try:
                therapist_profile = TherapistProfile.objects.get(user=user)
                
                # Limit family choices to those where therapist is assigned
                # But allow no family selection
                self.fields['family'].queryset = Family.objects.filter(
                    Q(therapist=user) | 
                    Q(children__therapist=therapist_profile)
                ).distinct().union(Family.objects.none())
                
                # Set initial therapist to current therapist
                self.fields['therapist'].initial = therapist_profile
                
            except TherapistProfile.DoesNotExist:
                # Restrict all choices if no therapist profile
                self.fields['family'].queryset = Family.objects.none()
                self.fields['therapist'].queryset = TherapistProfile.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        
        # Allow therapist assignment without family
        family = cleaned_data.get('family')
        therapist = cleaned_data.get('therapist')
        
        if therapist and not family:
            pass
        
        # If family is selected, optional therapist validation
        if family and therapist:
            # Optional: Add additional validation if needed
            pass
        
        return cleaned_data

class TreatmentForm(forms.ModelForm):
    """
    Form for creating and editing treatment sessions.
    
    Supports scheduling constraints:
    - Days: Sunday to Thursday
    - Hours: 8:00 AM to 8:00 PM
    - Validation for treatment details
    """
    scheduled_date = forms.DateField(
        label=_('תאריך מתוכנן'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_weekday]
    )
    
    start_time = forms.TimeField(
        label=_('שעת התחלה'),
        widget=forms.TimeInput(attrs={'type': 'time'}),
        validators=[validate_treatment_start_time]
    )
    
    end_time = forms.TimeField(
        label=_('שעת סיום'),
        widget=forms.TimeInput(attrs={'type': 'time'}),
        validators=[validate_treatment_end_time]
    )

    class Meta:
        model = Treatment
        fields = [
            'type', 'family', 'child', 'therapist', 
            'scheduled_date', 'start_time', 'end_time', 
            'status', 'summary', 'next_steps'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'family': forms.Select(attrs={'class': 'form-control'}),
            'child': forms.Select(attrs={'class': 'form-control'}),
            'therapist': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add crispy form helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי טיפול'),
                Row(
                    Column('type', css_class='form-group col-md-6 mb-0'),
                    Column('status', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('family', css_class='form-group col-md-6 mb-0'),
                    Column('child', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('therapist', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                _('מועד הטיפול'),
                Row(
                    Column('scheduled_date', css_class='form-group col-md-4 mb-0'),
                    Column('start_time', css_class='form-group col-md-4 mb-0'),
                    Column('end_time', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                _('סיכום והמשך'),
                'summary',
                'next_steps',
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

        # Limit therapist choices if not a superuser
        if user and not user.is_superuser:
            try:
                therapist_profile = TherapistProfile.objects.get(user=user)
                self.fields['therapist'].queryset = TherapistProfile.objects.filter(pk=therapist_profile.pk)
                self.fields['therapist'].initial = therapist_profile
            except TherapistProfile.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Validate that end time is after start time
        if start_time and end_time and start_time >= end_time:
            raise ValidationError(_('שעת סיום חייבת להיות לאחר שעת ההתחלה'))

        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'document_type', 'file', 'notes', 'family', 'child']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, family=None, child=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # Handle family pre-selection
        if family:
            self.fields['family'].initial = family
            self.fields['family'].widget = forms.HiddenInput()
            self.fields['child'].queryset = Child.objects.filter(family=family)
        elif child:
            self.fields['child'].initial = child
            self.fields['child'].widget = forms.HiddenInput()
            self.fields['family'].initial = child.family
            self.fields['family'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי מסמך'),
                Row(
                    Column('name', css_class='col-md-6 mb-3'),
                    Column('document_type', css_class='col-md-6 mb-3'),
                ),
                'file',
            ),
            Fieldset(
                _('שיוך'),
                Row(
                    Column('family', css_class='col-md-6 mb-3'),
                    Column('child', css_class='col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                _('מידע נוסף'),
                'notes',
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

class TherapistForm(forms.ModelForm):
    email = forms.EmailField(label=_('אימייל'))
    first_name = forms.CharField(label=_('שם פרטי'), max_length=30)
    last_name = forms.CharField(label=_('שם משפחה'), max_length=30)
    password = forms.CharField(label=_('סיסמה'), widget=forms.PasswordInput(), required=False)

    class Meta:
        model = TherapistProfile
        fields = ['phone', 'specialization', 'is_active', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # אם זה עדכון של מטפל קיים, הוסף את הנתונים הקיימים
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                _('פרטים אישיים'),
                Row(
                    Column('first_name', css_class='form-group col-md-4 mb-0'),
                    Column('last_name', css_class='form-group col-md-4 mb-0'),
                    Column('email', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('phone', css_class='form-group col-md-6 mb-0'),
                    Column('specialization', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'notes',
                'is_active'
            ),
            Fieldset(
                _('סיסמה'),
                'password',
                HTML("""<div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    השאר ריק אם אינך רוצה לשנות את הסיסמה
                </div>""")
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

    def save(self, commit=True):
        therapist = super().save(commit=False)
        
        # יצירת או עדכון משתמש
        if not therapist.pk:
            # יצירת משתמש חדש
            username = self.cleaned_data['email'].split('@')[0]
            base_username = username[:30]  # מגביל ל-30 תווים
            counter = 1
            
            # בדיקה שהשם משתמש לא קיים כבר
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password'] or User.objects.make_random_password(),
                is_active=self.cleaned_data.get('is_active', True)
            )
            therapist.user = user
        else:
            # עדכון משתמש קיים
            user = therapist.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.is_active = self.cleaned_data.get('is_active', True)
            
            # עדכון סיסמה אם סופקה
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            
            user.save()

        if commit:
            therapist.save()
        
        return therapist
