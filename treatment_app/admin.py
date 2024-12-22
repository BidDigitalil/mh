from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Family, Child, Document, Treatment, TherapistProfile

class ChildInline(admin.TabularInline):
    model = Child
    extra = 0

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

class TherapistProfileInline(admin.StackedInline):
    model = TherapistProfile
    can_delete = False
    verbose_name_plural = 'פרופיל מטפל'

class CustomUserAdmin(UserAdmin):
    inlines = (TherapistProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_therapist', 'get_is_active')
    list_filter = ('is_staff', 'is_superuser', 'therapistprofile__is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_is_therapist(self, obj):
        return hasattr(obj, 'therapistprofile')
    get_is_therapist.short_description = 'מטפל'
    get_is_therapist.boolean = True

    def get_is_active(self, obj):
        if hasattr(obj, 'therapistprofile'):
            return obj.therapistprofile.is_active
        return obj.is_active
    get_is_active.short_description = 'פעיל'
    get_is_active.boolean = True

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('מידע אישי', {'fields': ('first_name', 'last_name', 'email')}),
        ('הרשאות', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('תאריכים חשובים', {'fields': ('last_login', 'date_joined')}),
    )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'therapist')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('therapist',)
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
    list_display = ('name', 'family', 'birth_date', 'gender')
    list_filter = ('family', 'gender')
    search_fields = ('name',)
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
