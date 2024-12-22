from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
from .models import Family, Child, Treatment, Document

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = [
            'name', 'address', 'phone', 'email',
            'father_name', 'father_phone', 'father_email',
            'mother_name', 'mother_phone', 'mother_email',
            'therapist', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי משפחה'),
                Row(
                    Column('name', css_class='col-md-6 mb-3'),
                    Column('phone', css_class='col-md-6 mb-3'),
                ),
                Row(
                    Column('address', css_class='col-md-6 mb-3'),
                    Column('email', css_class='col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                _('פרטי האב'),
                Row(
                    Column('father_name', css_class='col-md-4 mb-3'),
                    Column('father_phone', css_class='col-md-4 mb-3'),
                    Column('father_email', css_class='col-md-4 mb-3'),
                ),
            ),
            Fieldset(
                _('פרטי האם'),
                Row(
                    Column('mother_name', css_class='col-md-4 mb-3'),
                    Column('mother_phone', css_class='col-md-4 mb-3'),
                    Column('mother_email', css_class='col-md-4 mb-3'),
                ),
            ),
            Fieldset(
                _('מידע נוסף'),
                'therapist',
                'notes',
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = [
            'family', 'name', 'birth_date', 'gender',
            'school', 'grade', 'medical_info', 'notes'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_info': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                _('פרטים אישיים'),
                Row(
                    Column('family', css_class='col-md-6 mb-3'),
                    Column('name', css_class='col-md-6 mb-3'),
                ),
                Row(
                    Column('birth_date', css_class='col-md-6 mb-3'),
                    Column('gender', css_class='col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                _('פרטי בית ספר'),
                Row(
                    Column('school', css_class='col-md-6 mb-3'),
                    Column('grade', css_class='col-md-6 mb-3'),
                ),
            ),
            Fieldset(
                _('מידע רפואי'),
                'medical_info',
            ),
            Fieldset(
                _('הערות'),
                'notes',
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['child', 'date', 'therapist', 'summary', 'next_steps']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'next_steps': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, therapist=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        if therapist:
            self.fields['child'].queryset = Child.objects.filter(
                family__therapist=therapist
            )
            self.fields['therapist'].initial = therapist
            self.fields['therapist'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי טיפול'),
                Row(
                    Column('child', css_class='col-md-6 mb-3'),
                    Column('date', css_class='col-md-6 mb-3'),
                ),
                'therapist',
                'summary',
                'next_steps',
            ),
            Submit('submit', _('שמור'), css_class='btn btn-primary')
        )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['family', 'child', 'name', 'document_type', 'file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        if family:
            self.fields['family'].initial = family
            self.fields['family'].widget = forms.HiddenInput()
            self.fields['child'].queryset = Child.objects.filter(family=family)
        
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
