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
    list_display = ('name', 'family', 'therapist', 'birth_date', 'gender')
    list_filter = ('family', 'therapist', 'gender')
    search_fields = ('name', 'family__name')
    
    def get_readonly_fields(self, request, obj=None):
        # Make therapist read-only if it's inherited from family
        if obj and obj.family and obj.family.therapist:
            return self.readonly_fields + ('therapist',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        # Ensure therapist is set to family's therapist
        if obj.family and obj.family.therapist:
            obj.therapist = obj.family.therapist
        
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        (_('פרטים אישיים'), {
            'fields': ('family', 'name', 'birth_date', 'gender', 'therapist')
        }),
        (_('פרטי בית ספר'), {
            'fields': ('school', 'grade', 'teacher_name', 'teacher_phone', 
                       'school_counselor_name', 'school_counselor_phone')
        }),
        (_('מידע רפואי'), {
            'fields': ('allergies', 'medications', 'special_needs', 
                       'medical_info', 'notes')
        }),
    )

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Treatment model.
    
    Provides enhanced management of treatment sessions with:
    - Customized list display
    - Filtering options
    - Search capabilities
    """
    list_display = [
        'get_client_name', 
        'scheduled_date', 
        'start_time', 
        'end_time', 
        'type', 
        'status', 
        'therapist'
    ]
    
    list_filter = [
        'type', 
        'status', 
        'scheduled_date', 
        'therapist'
    ]
    
    search_fields = [
        'family__name', 
        'child__name', 
        'therapist__username', 
        'therapist__first_name', 
        'therapist__last_name'
    ]
    
    date_hierarchy = 'scheduled_date'
    
    def get_client_name(self, obj):
        """
        Returns the name of the client (family or child)
        """
        return obj.child.name if obj.child else obj.family.name
    get_client_name.short_description = _('שם לקוח')
    
    def get_queryset(self, request):
        """
        Optimize the queryset by selecting related objects
        """
        return super().get_queryset(request).select_related('family', 'child', 'therapist')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Customize foreign key fields in the admin form
        """
        if db_field.name == 'family':
            kwargs['queryset'] = Family.objects.order_by('name')
        elif db_field.name == 'child':
            kwargs['queryset'] = Child.objects.order_by('family__name', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
