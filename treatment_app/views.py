from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.utils.translation import gettext_lazy as _

from .models import (
    Treatment, 
    Family, 
    Child, 
    TherapistProfile,
    Document
)
from .forms import TreatmentForm, DocumentForm, FamilyForm, ChildForm, TherapistForm

import logging
logger = logging.getLogger(__name__)

class TreatmentListView(LoginRequiredMixin, ListView):
    """
    List view for treatments with advanced filtering and sorting
    """
    model = Treatment
    template_name = 'treatment_app/treatment_list.html'
    context_object_name = 'treatments'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        
        # Superuser sees all treatments
        if user.is_superuser:
            return Treatment.objects.all()
        
        # Regular therapist sees only their treatments
        return Treatment.objects.filter(
            Q(therapist=user) |  # Treatments created by therapist
            Q(child__therapist__user=user) |  # Treatments for children assigned to therapist
            Q(family__therapist=user)  # Treatments for families assigned to therapist
        ).distinct()

    def get_context_data(self, **kwargs):
        """
        Add additional context for filtering and status management
        """
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Treatment.TreatmentStatus.choices
        context['type_choices'] = Treatment.TreatmentType.choices
        
        # Add past due treatments
        context['past_due_treatments'] = Treatment.objects.filter(
            status=Treatment.TreatmentStatus.SCHEDULED,
            scheduled_date__lt=timezone.now().date()
        )
        
        return context

class TreatmentDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed view for a single treatment
    """
    model = Treatment
    template_name = 'treatment_app/treatment_detail.html'
    
    def get_context_data(self, **kwargs):
        """
        Add related documents to the context
        """
        context = super().get_context_data(**kwargs)
        context['documents'] = Document.objects.filter(
            Q(child=self.object.child) | 
            Q(family=self.object.family)
        )
        return context

class TreatmentCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new treatment
    """
    model = Treatment
    form_class = TreatmentForm
    template_name = 'treatment_app/treatment_form.html'

    def get_initial(self):
        """
        Pre-populate form fields based on context
        """
        initial = {}
        family_id = self.kwargs.get('family_id')
        child_id = self.kwargs.get('child_id')

        if family_id:
            initial['family'] = get_object_or_404(Family, pk=family_id)
        if child_id:
            child = get_object_or_404(Child, pk=child_id)
            initial['child'] = child
            initial['family'] = child.family
        
        # Set default therapist to current user
        initial['therapist'] = self.request.user
        
        return initial

    def form_valid(self, form):
        """
        Set the current user as therapist and save
        """
        form.instance.therapist = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect to treatment list after successful creation
        """
        return reverse_lazy('treatment_app:treatment-list')

class TreatmentUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing treatment
    """
    model = Treatment
    form_class = TreatmentForm
    template_name = 'treatment_app/treatment_form.html'

    def get_context_data(self, **kwargs):
        """
        Add document upload form to context
        """
        context = super().get_context_data(**kwargs)
        context['document_form'] = DocumentForm(initial={
            'treatment': self.object,
            'child': self.object.child,
            'family': self.object.family
        })
        return context

    def form_valid(self, form):
        """
        Additional processing when form is valid
        """
        # Auto-update status if summary is provided
        if form.cleaned_data.get('summary'):
            form.instance.status = Treatment.TreatmentStatus.COMPLETED
        
        return super().form_valid(form)

class TreatmentDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a treatment
    """
    model = Treatment
    template_name = 'treatment_app/treatment_confirm_delete.html'
    success_url = reverse_lazy('treatment_list')

@login_required
def weekly_calendar_view(request):
    """
    Render a weekly calendar view of treatments
    """
    # Get current week's start and end dates
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Get treatments for the current week, Sunday to Thursday
    treatments = Treatment.objects.filter(
        scheduled_date__range=[start_of_week, end_of_week],
        scheduled_date__week_day__in=[1, 2, 3, 4, 5]  # Sunday to Thursday
    ).select_related('family', 'child', 'therapist')

    context = {
        'treatments': treatments,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
    }

    return render(request, 'treatment_app/weekly_calendar.html', context)

@login_required
def dashboard(request):
    try:
        # Log user details for debugging
        logger.info(f"Dashboard access attempt by user: {request.user}")
        logger.info(f"User is superuser: {request.user.is_superuser}")
        logger.info(f"User ID: {request.user.id}")
        logger.info(f"Username: {request.user.username}")

        # For admin users
        if request.user.is_superuser:
            treatments = Treatment.objects.all()
            families = Family.objects.all()
            children = Child.objects.all()
            
            context = {
                'total_treatments': treatments.count(),
                'upcoming_treatments': treatments.filter(
                    status='SCHEDULED', 
                    scheduled_date__gte=timezone.now()
                ).count(),
                'total_families': families.count(),
                'new_families_this_month': families.filter(
                    created_at__month=timezone.now().month, 
                    created_at__year=timezone.now().year
                ).count(),
                'total_children': children.count(),
                'active_children': children.count(),  # Remove the is_active filter
                'recent_treatments': treatments.order_by('-scheduled_date')[:5],
                'recent_families': families.order_by('-created_at')[:5]
            }
            
            return render(request, 'treatment_app/dashboard.html', context)
        
        # For regular users
        try:
            # Explicitly get the user object to ensure it's a valid User instance
            user = User.objects.get(pk=request.user.pk)
            
            # Try to get the TherapistProfile
            try:
                therapist_profile = TherapistProfile.objects.get(user=user)
                logger.info(f"Found TherapistProfile for user: {user.username}")
                
                # Treatments query
                treatments = Treatment.objects.filter(
                    Q(therapist=therapist_profile) | 
                    Q(family__therapist=therapist_profile) | 
                    Q(child__family__therapist=therapist_profile)
                ).distinct()
                
                # Families query
                families = Family.objects.filter(therapist=therapist_profile)
                
                # Children query
                children = Child.objects.filter(family__therapist=therapist_profile)
                
                # Context for dashboard
                context = {
                    'total_treatments': treatments.count(),
                    'upcoming_treatments': treatments.filter(
                        status='SCHEDULED', 
                        scheduled_date__gte=timezone.now()
                    ).count(),
                    'total_families': families.count(),
                    'new_families_this_month': families.filter(
                        created_at__month=timezone.now().month, 
                        created_at__year=timezone.now().year
                    ).count(),
                    'total_children': children.count(),
                    'active_children': children.count(),  # Remove the is_active filter
                    'recent_treatments': treatments.order_by('-scheduled_date')[:5],
                    'recent_families': families.order_by('-created_at')[:5]
                }
                
            except TherapistProfile.DoesNotExist:
                logger.warning(f"No TherapistProfile found for user: {user.username}")
                messages.warning(request, 'אנא צור פרופיל מטפל כדי לגשת ללוח הבקרה המלא')
                context = {}
            
        except User.DoesNotExist:
            logger.error("User does not exist in database")
            messages.error(request, 'אירעה שגיאה בזיהוי המשתמש')
            return redirect('login')
        
        return render(request, 'treatment_app/dashboard.html', context)
    
    except Exception as e:
        # Catch-all for any unexpected errors
        logger.error(f"Unexpected error in dashboard view: {str(e)}", exc_info=True)
        messages.error(request, 'אירעה שגיאה לא צפויה. אנא נסה שוב או פנה לתמיכה.')
        return redirect('login')

class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'treatment_app/family_list.html'
    context_object_name = 'families'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # If not a superuser, filter families by therapist
        user = self.request.user
        if not user.is_superuser:
            try:
                therapist_profile = TherapistProfile.objects.get(user=user)
                queryset = queryset.filter(
                    Q(therapist=therapist_profile) | 
                    Q(children__therapist=therapist_profile)
                ).distinct()
            except TherapistProfile.DoesNotExist:
                # If no therapist profile, return no families
                queryset = queryset.none()
        
        # Search functionality
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Family name
                Q(phone__icontains=search_query) |  # Phone number
                Q(address__icontains=search_query) |  # Address
                Q(therapist__user__first_name__icontains=search_query) |  # Therapist first name
                Q(therapist__user__last_name__icontains=search_query) |  # Therapist last name
                Q(children__name__icontains=search_query)  # Child name
            ).distinct()
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add a flag to indicate if user can create families
        context['can_create_family'] = self.request.user.is_superuser
        
        # Add search query to context for preserving search input
        context['search_query'] = self.request.GET.get('q', '')
        
        return context

class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'treatment_app/family_detail.html'

    def test_func(self):
        user = self.request.user
        
        # Superusers can see all families
        if user.is_superuser:
            return True
        
        # Get or create therapist profile
        therapist_profile, created = TherapistProfile.objects.get_or_create(
            user=user, 
            defaults={'is_active': True}
        )
        
        family = self.get_object()
        
        # Check if therapist is assigned to the family or has children in the family
        return (
            family.therapist == user or
            family.children.filter(therapist=therapist_profile).exists()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = self.object
        user = self.request.user
        
        # Get therapist profile
        therapist_profile, created = TherapistProfile.objects.get_or_create(
            user=user, 
            defaults={'is_active': True}
        )
        
        # Check if user can edit
        context['can_edit'] = (
            user.is_superuser or 
            family.therapist == user
        )
        
        # Get treatments for this family
        context['treatments'] = Treatment.objects.filter(
            Q(family=family) | 
            Q(child__family=family)
        ).order_by('-scheduled_date')
        
        return context

class FamilyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Family
    form_class = FamilyForm
    template_name = 'treatment_app/family_form.html'
    success_url = reverse_lazy('treatment_app:family-list')

    def test_func(self):
        # Only superusers can create families
        return self.request.user.is_superuser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Ensure only superusers can create families
        if not self.request.user.is_superuser:
            messages.error(self.request, 'אין לך הרשאה ליצירת משפחה חדשה')
            return redirect('treatment_app:family-list')
        
        form.instance.created_by = self.request.user
        messages.success(self.request, 'המשפחה נוצרה בהצלחה')
        return super().form_valid(form)

class FamilyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = 'treatment_app/family_form.html'

    def test_func(self):
        # Only superusers can update families
        return self.request.user.is_superuser

    def get_queryset(self):
        # Ensure only superusers can access the queryset
        if self.request.user.is_superuser:
            return Family.objects.all()
        return Family.objects.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'פרטי המשפחה עודכנו בהצלחה')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.pk})

class FamilyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Family
    template_name = 'treatment_app/family_confirm_delete.html'
    success_url = reverse_lazy('treatment_app:family-list')

    def test_func(self):
        # Only superusers can delete families
        return self.request.user.is_superuser

    def get_queryset(self):
        # Ensure only superusers can access the queryset
        if self.request.user.is_superuser:
            return Family.objects.all()
        return Family.objects.none()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'המשפחה נמחקה בהצלחה')
        return super().delete(request, *args, **kwargs)

class ChildListView(LoginRequiredMixin, ListView):
    """
    List view for children with filtering and sorting
    """
    model = Child
    template_name = 'treatment_app/child_list.html'
    context_object_name = 'children'
    ordering = ['family', 'name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add age calculation to context
        for child in context['children']:
            child.age_text = self.calculate_age(child.birth_date)
        
        return context

    @staticmethod
    def calculate_age(birth_date):
        """
        Calculate age in Hebrew with grammatically correct display
        """
        if not birth_date:
            return 'לא ידוע'

        today = date.today()
        years = today.year - birth_date.year
        months = today.month - birth_date.month

        # Adjust if birthday hasn't occurred this year
        if today.day < birth_date.day:
            months -= 1

        if months < 0:
            years -= 1
            months += 12

        # Hebrew grammar for age display
        def age_display(years, months):
            # הצגת גיל אם מדובר בשנה אחת
            if years == 0:
                return f'{months} {"חודש" if months == 1 else "חודשים"}'
            
            # הצגת גיל אם מדובר בשנה אחת ויתכן גם חודשים
            elif years == 1:
                month_text = f", {months} {'חודש' if months == 1 else 'חודשים'}" if months > 0 else ""
                return f'שנה{month_text}'
            
            # הצגת גיל אם מדובר ביותר משנתיים ויתכן גם חודשים
            else:
                month_text = f", {months} {'חודש' if months == 1 else 'חודשים'}" if months > 0 else ""
                return f'{years} שנים{month_text}'


    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        
        # Superuser sees all children
        if user.is_superuser:
            return Child.objects.all().select_related('family', 'therapist__user')
        
        # Regular therapist sees only their children or unassigned children
        return Child.objects.filter(
            Q(therapist__user=user) |  # Children assigned to therapist
            Q(therapist__isnull=True)  # Unassigned children
        ).select_related('family', 'therapist__user')

class ChildDetailView(LoginRequiredMixin, DetailView):
    model = Child
    template_name = 'treatment_app/child_detail.html'
    context_object_name = 'child'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determine the therapist to display
        child = self.object
        
        # Priority 1: Child's direct therapist
        if child.therapist:
            context['therapist'] = child.therapist
        # Priority 2: Family's therapist
        elif child.family and child.family.therapist:
            context['therapist'] = child.family.therapist
        # Priority 3: No therapist assigned
        else:
            context['therapist'] = None
        
        # Restrict view based on user permissions
        user = self.request.user
        if not user.is_superuser:
            # Check if the current user is a therapist
            try:
                current_therapist = TherapistProfile.objects.get(user=user)
                
                # Check if the therapist can view this child
                is_authorized = False
                if child.therapist and child.therapist == current_therapist:
                    is_authorized = True
                elif child.family and child.family.therapist == current_therapist:
                    is_authorized = True
                
                if not is_authorized:
                    raise PermissionDenied("אין לך הרשאה לצפות בפרטי ילד זה")
            
            except TherapistProfile.DoesNotExist:
                # If the user is not a therapist and not a superuser, deny access
                raise PermissionDenied("אין לך הרשאה לצפות בפרטי ילד זה")
        
        context['treatments'] = self.object.treatments.all()
        context['documents'] = self.object.documents.all()
        return context

class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = ChildForm
    template_name = 'treatment_app/child_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # If a family is passed in the URL, pre-populate the family field
        if 'family' in self.kwargs:
            family = get_object_or_404(Family, pk=self.kwargs['family'])
            kwargs['family'] = family
        
        return kwargs

    def form_valid(self, form):
        # If a family is specified in the URL, use that family
        if 'family' in self.kwargs:
            family = get_object_or_404(Family, pk=self.kwargs['family'])
            form.instance.family = family
        
        # If no therapist is set, try to set the current user's therapist profile
        if not form.instance.therapist and not self.request.user.is_superuser:
            try:
                therapist_profile = TherapistProfile.objects.get(user=self.request.user)
                form.instance.therapist = therapist_profile
            except TherapistProfile.DoesNotExist:
                pass
        
        # Validate user permissions
        user = self.request.user
        if not user.is_superuser:
            try:
                therapist = TherapistProfile.objects.get(user=user)
                if form.instance.family and form.instance.family.therapist and form.instance.family.therapist != therapist:
                    raise PermissionDenied("אין לך הרשאה להוסיף ילד למשפחה זו")
            except TherapistProfile.DoesNotExist:
                raise PermissionDenied("אין לך הרשאה להוסיף ילד")
        
        messages.success(self.request, 'הילד נוסף בהצלחה')
        return super().form_valid(form)

    def get_success_url(self):
        # If a family was specified, return to that family's detail page
        if 'family' in self.kwargs:
            return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.kwargs['family']})
        
        # Otherwise, go to the child list
        return reverse_lazy('treatment_app:child-list')

class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildForm
    template_name = 'treatment_app/child_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user for therapist restrictions
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add family to context for back button
        context['family'] = self.object.family
        return context

    def get_success_url(self):
        return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # If no therapist is set, try to set the current user's therapist profile
        if not form.instance.therapist and not self.request.user.is_superuser:
            try:
                therapist_profile = TherapistProfile.objects.get(user=self.request.user)
                form.instance.therapist = therapist_profile
            except TherapistProfile.DoesNotExist:
                pass
        
        messages.success(self.request, 'פרטי הילד עודכנו בהצלחה')
        return super().form_valid(form)

class ChildDeleteView(LoginRequiredMixin, DeleteView):
    model = Child
    template_name = 'treatment_app/child_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.family.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'הילד נמחק בהצלחה')
        return super().delete(request, *args, **kwargs)

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'treatment_app/document_list.html'
    context_object_name = 'documents'
    ordering = ['-created_at']

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'treatment_app/document_detail.html'
    context_object_name = 'document'

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'treatment_app/document_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'family' in self.kwargs:
            context['family'] = get_object_or_404(Family, pk=self.kwargs['family'])
        elif 'child' in self.kwargs:
            child = get_object_or_404(Child, pk=self.kwargs['child'])
            context['child'] = child
            context['family'] = child.family
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'family' in self.kwargs:
            kwargs['family'] = get_object_or_404(Family, pk=self.kwargs['family'])
        elif 'child' in self.kwargs:
            kwargs['child'] = get_object_or_404(Child, pk=self.kwargs['child'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        if self.object.child:
            return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.child.pk})
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.family.pk})

    def form_valid(self, form):
        messages.success(self.request, 'המסמך נוסף בהצלחה')
        return super().form_valid(form)

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'treatment_app/document_form.html'

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.family.pk})

    def form_valid(self, form):
        messages.success(self.request, 'פרטי המסמך עודכנו בהצלחה')
        return super().form_valid(form)

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'treatment_app/document_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.family.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'המסמך נמחק בהצלחה')
        return super().delete(request, *args, **kwargs)

class TherapistListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = TherapistProfile
    template_name = 'treatment_app/therapist_list.html'
    context_object_name = 'therapists'

    def test_func(self):
        return self.request.user.is_superuser

class TherapistCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TherapistProfile
    form_class = TherapistForm
    template_name = 'treatment_app/therapist_form.html'
    success_url = reverse_lazy('treatment_app:therapist-list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('הוספת מטפל חדש')
        return context

class TherapistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TherapistProfile
    form_class = TherapistForm
    template_name = 'treatment_app/therapist_form.html'
    success_url = reverse_lazy('treatment_app:therapist-list')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _(f'עריכת מטפל - {self.object}')
        return context

class TherapistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TherapistProfile
    template_name = 'treatment_app/therapist_confirm_delete.html'
    success_url = reverse_lazy('treatment_app:therapist-list')

    def test_func(self):
        return self.request.user.is_superuser

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse

@login_required
def treatment_calendar_data(request):
    """
    Provide treatment data for FullCalendar with optional filtering
    """
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    treatment_type = request.GET.get('type')
    treatment_status = request.GET.get('status')

    # Base queryset with date range filter
    treatments = Treatment.objects.filter(
        scheduled_date__range=[start_date, end_date]
    ).select_related('family', 'child', 'therapist')

    # Apply type filter if provided
    if treatment_type:
        treatments = treatments.filter(type=treatment_type)

    # Apply status filter if provided
    if treatment_status:
        treatments = treatments.filter(status=treatment_status)

    # Prepare event data
    events = []
    for treatment in treatments:
        # Determine client name and color
        if treatment.child:
            client_name = treatment.child.name
            color = '#007bff'  # Bootstrap primary blue
        elif treatment.family:
            client_name = treatment.family.name
            color = '#28a745'  # Bootstrap success green
        else:
            client_name = 'לקוח לא מזוהה'
            color = '#6c757d'  # Bootstrap secondary gray

        # Determine status color
        if treatment.is_past_due():
            color = '#dc3545'  # Bootstrap danger red

        # Create event
        event = {
            'id': treatment.id,
            'title': f"{client_name} - {treatment.get_type_display()}",
            'start': treatment.scheduled_date.strftime('%Y-%m-%d') + f'T{treatment.start_time}',
            'end': treatment.scheduled_date.strftime('%Y-%m-%d') + f'T{treatment.end_time}',
            'color': color,
            'url': reverse('treatment_detail', kwargs={'pk': treatment.pk})
        }
        events.append(event)

    return JsonResponse(events, safe=False)

def calendar_view(request):
    """
    Render the calendar view with context for filtering
    """
    context = {
        'status_choices': Treatment.TreatmentStatus.choices,
        'type_choices': Treatment.TreatmentType.choices,
    }
    return render(request, 'treatment_app/calendar.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Log login attempt
            logger.info(f"Login attempt for username: {username}")
            
            # Validate input
            if not username or not password:
                messages.error(request, 'אנא הזן שם משתמש וסיסמה')
                return render(request, 'treatment_app/login.html')
            
            # Attempt to find the user
            try:
                user = User.objects.get(username=username)
                logger.info(f"User found: {username}")
            except User.DoesNotExist:
                logger.warning(f"Login attempt for non-existent user: {username}")
                messages.error(request, 'שם משתמש או סיסמה שגויים')
                return render(request, 'treatment_app/login.html')
            
            # Check user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {username}")
                messages.error(request, 'החשבון שלך אינו פעיל. אנא צור קשר עם מנהל המערכת.')
                return render(request, 'treatment_app/login.html')
            
            # Authenticate user
            auth_user = authenticate(request, username=username, password=password)
            
            if auth_user is not None:
                # Successful login
                login(request, auth_user)
                logger.info(f"Successful login for user: {username}")
                
                # Redirect based on user type
                if auth_user.is_superuser:
                    return redirect('admin:index')
                
                # Check if therapist profile exists
                try:
                    TherapistProfile.objects.get(user=auth_user)
                    return redirect('treatment_app:dashboard')
                except TherapistProfile.DoesNotExist:
                    # Redirect to create therapist profile
                    messages.info(request, 'אנא השלם את פרופיל המטפל שלך')
                    return redirect('treatment_app:therapist-create')
            
            else:
                # Authentication failed
                logger.warning(f"Failed login attempt for user: {username}")
                messages.error(request, 'שם משתמש או סיסמה שגויים')
                return render(request, 'treatment_app/login.html')
        
        except Exception as e:
            # Comprehensive error logging
            logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
            messages.error(request, f'אירעה שגיאה לא צפויה: {str(e)}. אנא נסה שוב או פנה לתמיכה.')
            return redirect('login')

    # GET request
    return render(request, 'treatment_app/login.html')
