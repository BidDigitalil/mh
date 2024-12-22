from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Family, Child, Treatment, Document, TherapistProfile
from .forms import FamilyForm, ChildForm, TreatmentForm, DocumentForm, TherapistForm
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

@login_required
def dashboard(request):
    user = request.user
    context = {}

    # Default context for all users
    context['recent_treatments'] = Treatment.objects.order_by('-date')[:5]
    context['recent_documents'] = Document.objects.order_by('-created_at')[:5]

    if user.is_superuser:
        # Superuser sees everything
        context['recent_families'] = Family.objects.all().order_by('-created_at')[:5]
        context['recent_children'] = Child.objects.all().order_by('-created_at')[:5]
    else:
        # Ensure a TherapistProfile exists for this user
        therapist_profile, created = TherapistProfile.objects.get_or_create(
            user=user, 
            defaults={'is_active': True}
        )
        
        # Fetch families where:
        # 1. Therapist is directly assigned to the family
        # 2. Therapist is assigned to a child in the family
        families_query = Family.objects.filter(
            Q(therapist=user) |  # Direct family assignment by User
            Q(children__therapist=therapist_profile)  # Child's therapist
        ).distinct().order_by('-created_at')[:5]

        # Get recent children assigned to this therapist
        children_query = Child.objects.filter(
            Q(therapist=therapist_profile) |  # Direct child assignment
            Q(family__therapist=user)  # Family's therapist
        ).distinct().order_by('-created_at')[:5]

        context['recent_families'] = families_query
        context['recent_children'] = children_query

    return render(request, 'treatment_app/dashboard.html', context)

class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'treatment_app/family_list.html'
    context_object_name = 'families'

    def get_queryset(self):
        # Get the base queryset
        queryset = super().get_queryset()
        
        # If not a superuser, filter families
        user = self.request.user
        if not user.is_superuser:
            try:
                # Get the current therapist profile
                current_therapist = TherapistProfile.objects.get(user=user)
                
                # Filter families where:
                # 1. Therapist is directly assigned to the family by User
                # 2. Therapist is assigned to a child in the family
                queryset = queryset.filter(
                    Q(therapist=user) | 
                    Q(children__therapist=current_therapist)
                ).distinct()
            
            except TherapistProfile.DoesNotExist:
                # If not a therapist, return an empty queryset
                queryset = queryset.none()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add a flag to indicate if user can create families
        context['can_create_family'] = self.request.user.is_superuser
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
        ).order_by('-date')
        
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
    model = Child
    template_name = 'treatment_app/child_list.html'
    context_object_name = 'children'
    ordering = ['family', 'name']

    def get_queryset(self):
        # Get the base queryset
        queryset = super().get_queryset()
        
        # If not a superuser, filter children
        user = self.request.user
        if not user.is_superuser:
            try:
                # Get the current therapist profile
                current_therapist = TherapistProfile.objects.get(user=user)
                
                # Filter children where:
                # 1. Therapist is directly assigned to the child, OR
                # 2. Therapist is assigned to the child's family
                queryset = queryset.filter(
                    Q(therapist=current_therapist) | 
                    Q(family__therapist=current_therapist)
                )
            
            except TherapistProfile.DoesNotExist:
                # If not a therapist, return an empty queryset
                queryset = queryset.none()
        
        return queryset

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
        
        # If a family_id is passed in the URL, add it to initial
        if 'family' in self.kwargs:
            kwargs['initial'] = {'family': self.kwargs['family']}
        
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # If a family is specified in the URL, check permissions
        if 'family' in self.kwargs:
            family = get_object_or_404(Family, pk=self.kwargs['family'])
            
            # Check if user is a superuser or the family's therapist
            user = self.request.user
            if not user.is_superuser:
                try:
                    therapist = TherapistProfile.objects.get(user=user)
                    if family.therapist != therapist:
                        raise PermissionDenied("אין לך הרשאה להוסיף ילד למשפחה זו")
                except TherapistProfile.DoesNotExist:
                    raise PermissionDenied("אין לך הרשאה להוסיף ילד למשפחה זו")
        
        return context

    def get_success_url(self):
        # If a family was specified, return to that family's detail page
        if 'family' in self.kwargs:
            return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.kwargs['family']})
        
        # Otherwise, go to the child list
        return reverse_lazy('treatment_app:child-list')

    def form_valid(self, form):
        # If a family is specified in the URL, set it
        if 'family' in self.kwargs:
            form.instance.family_id = self.kwargs['family']
        
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
                if form.instance.family and form.instance.family.therapist != therapist:
                    raise PermissionDenied("אין לך הרשאה להוסיף ילד למשפחה זו")
            except TherapistProfile.DoesNotExist:
                raise PermissionDenied("אין לך הרשאה להוסיף ילד")
        
        messages.success(self.request, 'הילד נוסף בהצלחה')
        return super().form_valid(form)

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

class TreatmentListView(LoginRequiredMixin, ListView):
    model = Treatment
    template_name = 'treatment_app/treatment_list.html'
    context_object_name = 'treatments'
    ordering = ['-date']

    def get_queryset(self):
        user = self.request.user
        
        # Superusers see all treatments
        if user.is_superuser:
            return Treatment.objects.all()
        
        # Get or create therapist profile
        therapist_profile, created = TherapistProfile.objects.get_or_create(
            user=user, 
            defaults={'is_active': True}
        )
        
        # Filter treatments for the therapist
        return Treatment.objects.filter(
            Q(therapist=user) |  # Treatments created by therapist
            Q(child__therapist=therapist_profile) |  # Treatments for children assigned to therapist
            Q(family__therapist=user)  # Treatments for families assigned to therapist
        ).distinct()

class TreatmentCreateView(LoginRequiredMixin, CreateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = 'treatment_app/treatment_form.html'

    def get_initial(self):
        initial = super().get_initial()
        if 'family_id' in self.kwargs:
            family = get_object_or_404(Family, pk=self.kwargs['family_id'])
            initial['family'] = family
            initial['type'] = 'family'
        elif 'child_id' in self.kwargs:
            child = get_object_or_404(Child, pk=self.kwargs['child_id'])
            initial['child'] = child
            initial['family'] = child.family
            initial['type'] = 'individual'
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'family_id' in self.kwargs:
            family = get_object_or_404(Family, pk=self.kwargs['family_id'])
            context['family'] = family
            context['title'] = f'הוספת טיפול למשפחת {family.name}'
        elif 'child_id' in self.kwargs:
            child = get_object_or_404(Child, pk=self.kwargs['child_id'])
            context['child'] = child
            context['title'] = f'הוספת טיפול ל{child.name}'
        else:
            context['title'] = 'הוספת טיפול'
        return context

    def form_valid(self, form):
        treatment = form.save(commit=False)
        if 'family_id' in self.kwargs:
            treatment.family = get_object_or_404(Family, pk=self.kwargs['family_id'])
        elif 'child_id' in self.kwargs:
            child = get_object_or_404(Child, pk=self.kwargs['child_id'])
            treatment.child = child
            treatment.family = child.family
        treatment.save()
        messages.success(self.request, 'הטיפול נוסף בהצלחה')
        return super().form_valid(form)

    def get_success_url(self):
        if 'family_id' in self.kwargs:
            return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.kwargs['family_id']})
        elif 'child_id' in self.kwargs:
            return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.kwargs['child_id']})
        return reverse_lazy('treatment_app:treatment-list')

class TreatmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = 'treatment_app/treatment_form.html'

    def get_success_url(self):
        return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.child.pk})

    def form_valid(self, form):
        messages.success(self.request, 'פרטי הטיפול עודכנו בהצלחה')
        return super().form_valid(form)

class TreatmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Treatment
    template_name = 'treatment_app/treatment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.child.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'הטיפול נמחק בהצלחה')
        return super().delete(request, *args, **kwargs)

class TreatmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Treatment
    template_name = 'treatment_app/treatment_detail.html'

    def test_func(self):
        user = self.request.user
        treatment = self.get_object()

        # Superusers can see all treatments
        if user.is_superuser:
            return True

        # Ensure a TherapistProfile exists, create if not
        therapist_profile, created = TherapistProfile.objects.get_or_create(
            user=user, 
            defaults={'is_active': True}
        )

        # Check if the treatment belongs to the therapist
        return (
            # Treatment's therapist is the current user
            treatment.therapist == user or
            
            # Treatment's child is assigned to the therapist
            (treatment.child and treatment.child.therapist == therapist_profile) or
            
            # Treatment's family is assigned to the therapist
            (treatment.family and treatment.family.therapist == user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        treatment = self.object

        # Add additional context for the treatment
        context['can_edit'] = (
            self.request.user.is_superuser or 
            treatment.therapist == self.request.user
        )

        return context

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
