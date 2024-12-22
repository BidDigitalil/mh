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

@login_required
def dashboard(request):
    # Get the current user's therapist profile
    try:
        therapist = request.user.therapistprofile
    except TherapistProfile.DoesNotExist:
        therapist = None
    
    if request.user.is_superuser:
        # Superuser sees everything
        families = Family.objects.all()[:10]
        children = Child.objects.all()[:10]
        treatments = Treatment.objects.all()[:10]
    elif therapist:
        # Therapist sees only their associated families, children, and treatments
        families = Family.objects.filter(therapist=therapist)[:10]
        children = Child.objects.filter(
            Q(family__therapist=therapist) | 
            Q(therapist=therapist)
        )[:10]
        treatments = Treatment.objects.filter(
            Q(family__therapist=therapist) | 
            Q(child__family__therapist=therapist) |
            Q(child__therapist=therapist)
        )[:10]
    else:
        # Non-therapist, non-superuser sees nothing
        families = Family.objects.none()
        children = Child.objects.none()
        treatments = Treatment.objects.none()
    
    context = {
        'families': families,
        'children': children,
        'treatments': treatments,
    }
    return render(request, 'treatment_app/dashboard.html', context)

class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'treatment_app/family_list.html'
    context_object_name = 'families'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Family.objects.all()
        return Family.objects.filter(therapist=self.request.user)

class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'treatment_app/family_detail.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Family.objects.all()
        return Family.objects.filter(therapist=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = self.get_object()
        
        # Get all treatments for the family and its children
        family_treatments = Treatment.objects.filter(
            Q(family=family) | Q(child__family=family)
        ).order_by('-date')
        
        context['treatments'] = family_treatments
        context['children'] = family.children.all()
        
        # Get all documents - both family documents and children's documents
        family_documents = self.object.documents.all()
        children_documents = Document.objects.filter(child__family=self.object)
        context['documents'] = (family_documents | children_documents).order_by('-created_at')
        
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
        response = super().form_valid(form)
        messages.success(self.request, 'המשפחה נוספה בהצלחה')
        
        # עדכון תאריכי הטפסים
        if form.cleaned_data.get('consent_form'):
            self.object.consent_form_date = timezone.now()
        if form.cleaned_data.get('confidentiality_waiver'):
            self.object.confidentiality_waiver_date = timezone.now()
        self.object.save()
        
        return response

class FamilyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = 'treatment_app/family_form.html'

    def test_func(self):
        # Only superusers can update families
        return self.request.user.is_superuser

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Family.objects.all()
        return Family.objects.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'פרטי המשפחה עודכנו בהצלחה')
        
        # עדכון תאריכי הטפסים
        if form.cleaned_data.get('consent_form'):
            self.object.consent_form_date = timezone.now()
        if form.cleaned_data.get('confidentiality_waiver'):
            self.object.confidentiality_waiver_date = timezone.now()
        self.object.save()
        
        return response

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.pk})

class FamilyDeleteView(LoginRequiredMixin, DeleteView):
    model = Family
    template_name = 'treatment_app/family_confirm_delete.html'
    success_url = reverse_lazy('treatment_app:family-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'המשפחה נמחקה בהצלחה')
        return super().delete(request, *args, **kwargs)

class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'treatment_app/child_list.html'
    context_object_name = 'children'
    ordering = ['family', 'name']

class ChildDetailView(LoginRequiredMixin, DetailView):
    model = Child
    template_name = 'treatment_app/child_detail.html'
    context_object_name = 'child'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['treatments'] = self.object.treatments.all()
        context['documents'] = self.object.documents.all()
        return context

class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = ChildForm
    template_name = 'treatment_app/child_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass family if provided in URL
        if 'family_id' in self.kwargs:
            kwargs['family'] = get_object_or_404(Family, pk=self.kwargs['family_id'])
        # Pass current user for therapist restrictions
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add family to context if provided in URL
        if 'family_id' in self.kwargs:
            context['family'] = get_object_or_404(Family, pk=self.kwargs['family_id'])
        return context

    def get_success_url(self):
        # Redirect to family detail or child detail based on context
        if 'family_id' in self.kwargs:
            return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.kwargs['family_id']})
        return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
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

    def get_success_url(self):
        return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
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
        return Treatment.objects.filter(
            Q(family__therapist=self.request.user) |
            Q(child__family__therapist=self.request.user)
        ).select_related('family', 'child').order_by('-date')

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
