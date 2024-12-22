from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Family, Child, Document, Treatment

class ChildInline(admin.TabularInline):
    model = Child
    extra = 0

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'therapist', 'created_at')
    list_filter = ('therapist', 'created_at')
    search_fields = ('name', 'phone', 'email', 'father_name', 'mother_name')
    date_hierarchy = 'created_at'
    inlines = [ChildInline, DocumentInline]
    fieldsets = (
        (_('פרטי משפחה'), {
            'fields': ('name', 'address', 'phone', 'email', 'therapist')
        }),
        (_('פרטי האב'), {
            'fields': ('father_name', 'father_phone', 'father_email')
        }),
        (_('פרטי האם'), {
            'fields': ('mother_name', 'mother_phone', 'mother_email')
        }),
        (_('מידע נוסף'), {
            'fields': ('notes',)
        }),
    )

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'birth_date', 'school', 'grade')
    list_filter = ('family', 'grade', 'created_at')
    search_fields = ('name', 'family__name', 'school')
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('פרטים אישיים'), {
            'fields': ('family', 'name', 'birth_date', 'gender')
        }),
        (_('פרטי בית ספר'), {
            'fields': ('school', 'grade')
        }),
        (_('מידע נוסף'), {
            'fields': ('medical_info', 'notes')
        }),
    )

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('child', 'date', 'therapist')
    list_filter = ('therapist', 'date', 'created_at')
    search_fields = ('child__name', 'child__family__name', 'summary')
    date_hierarchy = 'date'
    fieldsets = (
        (_('פרטי טיפול'), {
            'fields': ('child', 'date', 'therapist')
        }),
        (_('סיכום'), {
            'fields': ('summary', 'next_steps')
        }),
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'family', 'child', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('name', 'family__name', 'child__name')
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('פרטי מסמך'), {
            'fields': ('name', 'document_type', 'file')
        }),
        (_('שיוך'), {
            'fields': ('family', 'child')
        }),
        (_('מידע נוסף'), {
            'fields': ('notes',)
        }),
    )
