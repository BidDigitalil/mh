from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Family, Child, Document, Treatment, Therapist

class ChildInline(admin.TabularInline):
    model = Child
    extra = 0

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

class TreatmentInline(admin.TabularInline):
    model = Treatment
    extra = 0
    fields = ('therapist', 'date', 'status', 'summary')

@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'specialization', 'active')
    list_filter = ('active', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('family_name', 'family_status', 'phone_number', 'assigned_therapist')
    list_filter = ('family_status', 'assigned_therapist')
    search_fields = ('family_name', 'father_name', 'mother_name')
    inlines = [ChildInline, DocumentInline]
    fieldsets = (
        (_('פרטי משפחה'), {
            'fields': ('family_name', 'family_status', 'address', 'phone_number', 'assigned_therapist')
        }),
        (_('פרטי האב'), {
            'fields': ('father_name', 'father_phone', 'father_email', 'father_id'),
        }),
        (_('פרטי האם'), {
            'fields': ('mother_name', 'mother_phone', 'mother_email', 'mother_id'),
        }),
        (_('מידע נוסף'), {
            'fields': ('notes',),
        }),
    )

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'birth_date', 'school', 'grade')
    list_filter = ('family', 'grade')
    search_fields = ('name', 'family__family_name')
    inlines = [TreatmentInline, DocumentInline]

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('child', 'therapist', 'date', 'status')
    list_filter = ('status', 'therapist', 'date')
    search_fields = ('child__name', 'therapist__user__username', 'summary')
    date_hierarchy = 'date'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'family', 'child', 'treatment')
    list_filter = ('document_type', 'family', 'created_at')
    search_fields = ('name', 'family__family_name', 'child__name')
