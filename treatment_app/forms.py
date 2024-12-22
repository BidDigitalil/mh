from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Div, HTML
from .models import Family, Child, Treatment, Document, TherapistProfile
from django.contrib.auth.models import User
from django.utils import timezone

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
                        HTML("""
                            {% if form.instance.consent_form %}
                                <div class="mb-2">
                                    <a href="{{ form.instance.consent_form.url }}" class="btn btn-sm btn-success" target="_blank">
                                        <i class="fas fa-file-download"></i> הורד טופס הסכמה קיים
                                    </a>
                                </div>
                            {% endif %}
                        """),
                        'consent_form',
                        css_class='form-group col-md-6 mb-0'
                    ),
                    Column(
                        HTML("""
                            {% if form.instance.confidentiality_waiver %}
                                <div class="mb-2">
                                    <a href="{{ form.instance.confidentiality_waiver.url }}" class="btn btn-sm btn-success" target="_blank">
                                        <i class="fas fa-file-download"></i> הורד טופס ויתור סודיות קיים
                                    </a>
                                </div>
                            {% endif %}
                        """),
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
        queryset=TherapistProfile.objects.all(), 
        required=False, 
        label='מטפל',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Child
        fields = [
            'name', 'birth_date', 'gender', 'school', 'grade', 
            'teacher_name', 'teacher_phone', 
            'school_counselor_name', 'school_counselor_phone',
            'allergies', 'medications', 'special_needs',
            'medical_info', 'notes', 'therapist'
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
        }

    def __init__(self, *args, family=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Determine therapist queryset based on user role
        if user and not user.is_superuser:
            try:
                current_therapist = user.therapistprofile
                # Therapists can only select themselves or no one
                self.fields['therapist'].queryset = TherapistProfile.objects.filter(pk=current_therapist.pk)
            except TherapistProfile.DoesNotExist:
                # Non-therapist users cannot change therapist
                self.fields['therapist'].disabled = True
        
        # If a family is provided, filter children to that family
        if family:
            # Ensure the child belongs to the specified family
            self.fields['family'].initial = family
            self.fields['family'].widget = forms.HiddenInput()
        
        # If an instance exists and has a therapist, set the initial value
        if hasattr(self, 'instance') and self.instance.pk:
            self.fields['therapist'].initial = self.instance.therapist

    def save(self, commit=True):
        # Ensure the child is saved with the selected therapist
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
        return instance

class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['type', 'family', 'child', 'date', 'summary', 'next_steps']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'next_steps': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, family=None, child=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'

        # Handle initial values and field visibility
        if family:
            self.fields['family'].initial = family
            self.fields['family'].widget = forms.HiddenInput()
            self.fields['child'].queryset = Child.objects.filter(family=family)
        elif child:
            self.fields['child'].initial = child
            self.fields['child'].widget = forms.HiddenInput()
            self.fields['family'].initial = child.family
            self.fields['family'].widget = forms.HiddenInput()
            self.fields['type'].initial = 'individual'

        # Customize form layout
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי טיפול'),
                Row(
                    Column('type', css_class='form-group col-md-6 mb-0'),
                    Column('date', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Div(
                    Row(
                        Column('family', css_class='form-group col-md-6 mb-0'),
                        Column('child', css_class='form-group col-md-6 mb-0'),
                        css_class='form-row'
                    ),
                    css_id='family-child-fields'
                ),
                Row(
                    Column('summary', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('next_steps', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                )
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

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
                HTML("""
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        השאר ריק אם אינך רוצה לשנות את הסיסמה
                    </div>
                """)
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
