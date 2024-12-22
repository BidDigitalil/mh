from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from .models import Family, Document

class BaseForm(forms.ModelForm):
    """
    טופס בסיסי שמכיל פונקציונליות משותפת
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.setup_layout()

    def setup_layout(self):
        """
        הגדרת הלייאאוט של הטופס - יש לממש בכל טופס יורש
        """
        pass

class FamilyForm(BaseForm):
    class Meta:
        model = Family
        fields = ['family_name', 'family_status', 'address', 'phone_number',
            'father_name', 'father_phone', 'father_email', 'father_id',
            'mother_name', 'mother_phone', 'mother_email', 'mother_id',
            'notes', 'assigned_therapist']
        widgets = {
            'family_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'assigned_therapist': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'family_name': _('שם משפחה'),
            'family_status': _('סטטוס משפחתי'),
            'address': _('כתובת'),
            'phone_number': _('טלפון ראשי'),
            'father_name': _('שם האב'),
            'father_phone': _('טלפון האב'),
            'father_email': _('אימייל האב'),
            'father_id': _('תעודת זהות האב'),
            'mother_name': _('שם האם'),
            'mother_phone': _('טלפון האם'),
            'mother_email': _('אימייל האם'),
            'mother_id': _('תעודת זהות האם'),
            'notes': _('הערות'),
            'assigned_therapist': _('מטפל מוקצה'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.setup_layout()

    def setup_layout(self):
        self.helper.layout = Layout(
            Fieldset(
                'פרטי משפחה',
                Row(
                    Column('family_name', css_class='col-md-6 mb-3'),
                    Column('family_status', css_class='col-md-6 mb-3'),
                    css_class='row'
                ),
                Row(
                    Column('address', css_class='col-md-8 mb-3'),
                    Column('phone_number', css_class='col-md-4 mb-3'),
                    css_class='row'
                ),
                'assigned_therapist',
            ),
            Fieldset(
                'פרטי האב',
                Row(
                    Column('father_name', css_class='col-md-6 mb-3'),
                    Column('father_id', css_class='col-md-6 mb-3'),
                    css_class='row'
                ),
                Row(
                    Column('father_phone', css_class='col-md-6 mb-3'),
                    Column('father_email', css_class='col-md-6 mb-3'),
                    css_class='row'
                ),
                css_class='father-details'
            ),
            Fieldset(
                'פרטי האם',
                Row(
                    Column('mother_name', css_class='col-md-6 mb-3'),
                    Column('mother_id', css_class='col-md-6 mb-3'),
                    css_class='row'
                ),
                Row(
                    Column('mother_phone', css_class='col-md-6 mb-3'),
                    Column('mother_email', css_class='col-md-6 mb-3'),
                    css_class='row'
                ),
                css_class='mother-details'
            ),
            Fieldset(
                'מידע נוסף',
                'notes',
                css_class='mb-3'
            )
        )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 9 or len(phone) > 10:
                raise forms.ValidationError(_('מספר טלפון חייב להכיל 9-10 ספרות'))
        return phone

    def clean_father_phone(self):
        phone = self.cleaned_data.get('father_phone')
        if phone:
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 9 or len(phone) > 10:
                raise forms.ValidationError(_('מספר טלפון חייב להכיל 9-10 ספרות'))
        return phone

    def clean_mother_phone(self):
        phone = self.cleaned_data.get('mother_phone')
        if phone:
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 9 or len(phone) > 10:
                raise forms.ValidationError(_('מספר טלפון חייב להכיל 9-10 ספרות'))
        return phone

    def clean_father_id(self):
        id_number = self.cleaned_data.get('father_id')
        if id_number:
            id_number = ''.join(filter(str.isdigit, id_number))
            if len(id_number) != 9:
                raise forms.ValidationError(_('תעודת זהות חייבת להכיל 9 ספרות'))
        return id_number

    def clean_mother_id(self):
        id_number = self.cleaned_data.get('mother_id')
        if id_number:
            id_number = ''.join(filter(str.isdigit, id_number))
            if len(id_number) != 9:
                raise forms.ValidationError(_('תעודת זהות חייבת להכיל 9 ספרות'))
        return id_number

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('family_status')
        
        if status == 'single_father':
            # וידוא שפרטי האב מלאים
            father_fields = ['father_name', 'father_phone', 'father_id']
            for field in father_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('שדה זה נדרש עבור אב יחיד'))
        
        elif status == 'single_mother':
            # וידוא שפרטי האם מלאים
            mother_fields = ['mother_name', 'mother_phone', 'mother_id']
            for field in mother_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('שדה זה נדרש עבור אם יחידה'))
        
        elif status == 'married' or status == 'divorced':
            # וידוא שפרטי שני ההורים מלאים
            parent_fields = ['father_name', 'father_phone', 'father_id',
                           'mother_name', 'mother_phone', 'mother_id']
            for field in parent_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('שדה זה נדרש'))
        
        return cleaned_data

class DocumentForm(BaseForm):
    class Meta:
        model = Document
        fields = ['name', 'document_type', 'file', 'family', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': _('כותרת המסמך'),
            'document_type': _('סוג מסמך'),
            'file': _('קובץ'),
            'notes': _('הערות'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.setup_layout()

    def setup_layout(self):
        self.helper.layout = Layout(
            Fieldset(
                _('פרטי מסמך'),
                Row(
                    Column('name', css_class='col-md-6 mb-3'),
                    Column('document_type', css_class='col-md-6 mb-3'),
                    css_class='row'
                ),
                'file',
            ),
            Fieldset(
                _('שיוך'),
                Row(
                    Column('family', css_class='col-md-4 mb-3'),
                    css_class='row'
                ),
            ),
            Fieldset(
                _('מידע נוסף'),
                'notes',
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        family = cleaned_data.get('family')

        return cleaned_data
