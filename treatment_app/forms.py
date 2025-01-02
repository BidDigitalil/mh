from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Div, HTML

from .models import Family, Child, Treatment, Document, TherapistProfile, SocialWorker

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
    FAMILY_STATUS_CHOICES = [
        ('intact', 'משפחה שלמה'),
        ('divorced', 'גרושים'),
        ('single_parent', 'הורה יחידני'),
        ('widowed', 'אלמן/אלמנה'),
        ('other', 'אחר')
    ]

    family_status = forms.ChoiceField(
        label='סטטוס משפחתי',
        choices=FAMILY_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_family_status'}),
        required=True
    )

    # Father details
    father_name = forms.CharField(
        label='שם האב',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    father_phone = forms.CharField(
        label='טלפון האב',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    father_email = forms.EmailField(
        label='דוא"ל האב',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Mother details
    mother_name = forms.CharField(
        label='שם האם',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    mother_phone = forms.CharField(
        label='טלפון האם',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    mother_email = forms.EmailField(
        label='דוא"ל האם',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Consent forms
    father_consent_form = forms.FileField(
        label='טופס הסכמה אב',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    mother_consent_form = forms.FileField(
        label='טופס הסכמה אם',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Dynamically show/hide fields based on family status
        if self.initial.get('family_status') or (self.instance and self.instance.family_status):
            family_status = self.initial.get('family_status') or self.instance.family_status
            
            if family_status == 'intact':
                # For intact families, show only one set of parent details
                pass
            elif family_status == 'divorced':
                # For divorced families, require both parent details and consent forms
                self.fields['father_name'].required = True
                self.fields['mother_name'].required = True
                self.fields['father_phone'].required = True
                self.fields['mother_phone'].required = True
                self.fields['father_consent_form'].required = True
                self.fields['mother_consent_form'].required = True
            elif family_status == 'single_parent':
                # For single parent, require details of the primary parent
                pass
            elif family_status == 'widowed':
                # For widowed, require details of the surviving parent
                pass

        # If user is not a superuser, make therapist field read-only or hidden
        if user and not user.is_superuser:
            # If editing an existing family, show current therapist but make it non-editable
            if self.instance and self.instance.pk:
                self.fields['therapist'].disabled = True
            else:
                # For new family, set therapist to current user
                try:
                    therapist_profile = TherapistProfile.objects.get(user=user)
                    self.fields['therapist'].initial = therapist_profile
                    self.fields['therapist'].disabled = True
                except TherapistProfile.DoesNotExist:
                    # If no therapist profile, hide or handle accordingly
                    pass

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Div(
                Row(
                    Column('name', css_class='col-md-4'),
                    Column('phone', css_class='col-md-4'),
                    Column('email', css_class='col-md-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('address', css_class='col-md-12'),
                    css_class='form-row'
                ),
                Row(
                    Column('therapist', css_class='col-md-6'),
                    Column('family_status', css_class='col-md-6'),
                    css_class='form-row'
                ),
                css_class='card-body'
            ),
            Fieldset(
                _('פרטי אב'),
                Row(
                    Column('father_name', css_class='col-md-4'),
                    Column('father_phone', css_class='col-md-4'),
                    Column('father_email', css_class='col-md-4'),
                ),
                Column('father_consent_form', css_class='col-md-6'),
            ),
            Fieldset(
                _('פרטי אם'),
                Row(
                    Column('mother_name', css_class='col-md-4'),
                    Column('mother_phone', css_class='col-md-4'),
                    Column('mother_email', css_class='col-md-4'),
                ),
                Column('mother_consent_form', css_class='col-md-6'),
            ),
            Fieldset(
                _('פרטי עובד סוציאלי'),
                Row(
                    Column('social_worker', css_class='col-md-12'),
                ),
            ),
            Fieldset(
                _('מסמכים'),
                Row(
                    Column('consent_form', css_class='col-md-6'),
                    Column('confidentiality_waiver', css_class='col-md-6'),
                ),
            ),
            'notes',
            Submit('submit', _('שמור'), css_class='btn btn-action')
        )

    def clean(self):
        cleaned_data = super().clean()
        family_status = cleaned_data.get('family_status')

        # Validate fields based on family status
        if family_status == 'divorced':
            # Require both parent details and consent forms
            if not cleaned_data.get('father_name'):
                self.add_error('father_name', _('שם האב נדרש למשפחות גרושות'))
            if not cleaned_data.get('mother_name'):
                self.add_error('mother_name', _('שם האם נדרש למשפחות גרושות'))
            if not cleaned_data.get('father_phone'):
                self.add_error('father_phone', _('טלפון האב נדרש למשפחות גרושות'))
            if not cleaned_data.get('mother_phone'):
                self.add_error('mother_phone', _('טלפון האם נדרש למשפחות גרושות'))
            if not cleaned_data.get('father_consent_form'):
                self.add_error('father_consent_form', _('טופס הסכמה לאב נדרש למשפחות גרושות'))
            if not cleaned_data.get('mother_consent_form'):
                self.add_error('mother_consent_form', _('טופס הסכמה לאם נדרש למשפחות גרושות'))

        return cleaned_data

    class Meta:
        model = Family
        fields = [
            'name', 'address', 'phone', 'email', 
            'family_status', 
            'father_name', 'father_phone', 'father_email',
            'mother_name', 'mother_phone', 'mother_email',
            'father_consent_form', 'mother_consent_form',
            'notes', 'therapist', 'social_worker'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class IconInputWidget(forms.Widget):
    def __init__(self, widget, icon=None):
        self.widget = widget
        self.icon = icon
        super().__init__(widget.attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Render the original widget
        widget_render = self.widget.render(name, value, attrs, renderer)
        
        # If icon is provided, wrap the widget with an icon container
        if self.icon:
            icon_html = f'<div class="icon-container"><i class="fas {self.icon}"></i></div>'
            return f'<div class="form-group">{widget_render}{icon_html}</div>'
        
        return widget_render

    def build_attrs(self, *args, **kwargs):
        return self.widget.build_attrs(*args, **kwargs)

class ChildForm(forms.ModelForm):
    therapist = forms.ModelChoiceField(
        queryset=TherapistProfile.objects.filter(is_active=True), 
        required=False, 
        label=_('מטפל'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-live-search': 'true',
            'data-style': 'btn-primary',
            'data-width': '100%'
        })
    )

    family = forms.ModelChoiceField(
        queryset=Family.objects.all(), 
        required=True,  
        label=_('משפחה'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-live-search': 'true',
            'data-style': 'btn-primary',
            'data-width': '100%',
            'placeholder': 'בחר משפחה'
        }),
        error_messages={
            'required': _('חובה לבחור משפחה. לא ניתן להוסיף ילד ללא משפחה.'),
            'invalid_choice': _('המשפחה שנבחרה אינה תקפה. אנא בחר משפחה מהרשימה.')
        }
    )

    birth_date = forms.DateField(
        label=_('תאריך לידה'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'dd/mm/yyyy'
        }),
        input_formats=['%d/%m/%Y', '%Y-%m-%d']
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
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        family_from_url = kwargs.pop('family', None)  
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            try:
                therapist_profile = TherapistProfile.objects.get(user=user)
                
                # If family is passed from URL, set it as the only option
                if family_from_url:
                    self.fields['family'].queryset = Family.objects.filter(pk=family_from_url.pk)
                    self.fields['family'].initial = family_from_url
                    self.fields['family'].widget = forms.HiddenInput()
                else:
                    # Filter families for this therapist
                    self.fields['family'].queryset = Family.objects.filter(
                        Q(therapist=therapist_profile) | 
                        Q(children__therapist=therapist_profile)
                    ).distinct()
                
                # Filter therapists for this user
                self.fields['therapist'].queryset = TherapistProfile.objects.filter(
                    Q(pk=therapist_profile.pk) | 
                    Q(is_active=True)
                )
                
            except TherapistProfile.DoesNotExist:
                # Restrict all choices if no therapist profile
                self.fields['family'].queryset = Family.objects.none()
                self.fields['therapist'].queryset = TherapistProfile.objects.none()
        
        # If family_from_url is provided, make it the default and only option
        if family_from_url:
            self.fields['family'].queryset = Family.objects.filter(pk=family_from_url.pk)
            self.fields['family'].initial = family_from_url

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure a family is selected
        if not cleaned_data.get('family'):
            raise forms.ValidationError({
                'family': _('חובה לבחור משפחה. לא ניתן להוסיף ילד ללא משפחה.')
            })
        
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
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'dd/mm/yyyy'
        }),
        input_formats=['%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y'],  # Added Hebrew date format
        required=False,
        validators=[validate_weekday]
    )
    
    actual_date = forms.DateField(
        label=_('תאריך בפועל'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'dd/mm/yyyy'
        }),
        input_formats=['%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y'],  # Added Hebrew date format
        required=False
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
            'scheduled_date', 'actual_date', 'start_time', 'end_time', 
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
                    Column('actual_date', css_class='form-group col-md-4 mb-0'),
                    Column('start_time', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('end_time', css_class='form-group col-md-12 mb-0'),
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
        scheduled_date = cleaned_data.get('scheduled_date')
        actual_date = cleaned_data.get('actual_date')
        status = cleaned_data.get('status')

        # If no scheduled date, use actual date
        if not scheduled_date and actual_date:
            cleaned_data['scheduled_date'] = actual_date

        # If actual date is provided, set status to COMPLETED
        if actual_date:
            cleaned_data['status'] = 'COMPLETED'

        # Validate that end time is after start time
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
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
