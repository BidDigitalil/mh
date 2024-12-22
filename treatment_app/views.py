from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Family, Document
from .forms import FamilyForm, DocumentForm

@login_required
def dashboard(request):
    if request.user.is_staff:
        families = Family.objects.all()
    else:
        families = Family.objects.filter(therapist=request.user)
    
    return render(request, 'treatment_app/dashboard.html', {
        'families': families[:10]  # Show only last 10 families
    })

# Family Views
class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'treatment_app/family_list.html'
    context_object_name = 'families'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Family.objects.all()
        return Family.objects.filter(therapist=self.request.user)

class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'treatment_app/family_detail.html'
    context_object_name = 'family'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Family.objects.all()
        return Family.objects.filter(therapist=self.request.user)

class FamilyCreateView(LoginRequiredMixin, CreateView):
    model = Family
    form_class = FamilyForm
    template_name = 'treatment_app/family_form.html'
    success_url = reverse_lazy('treatment_app:family-list')

    def form_valid(self, form):
        messages.success(self.request, 'המשפחה נוצרה בהצלחה')
        return super().form_valid(form)

class FamilyUpdateView(LoginRequiredMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = 'treatment_app/family_form.html'
    success_url = reverse_lazy('treatment_app:family-list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Family.objects.all()
        return Family.objects.filter(therapist=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'המשפחה עודכנה בהצלחה')
        return super().form_valid(form)

class FamilyDeleteView(LoginRequiredMixin, DeleteView):
    model = Family
    template_name = 'treatment_app/family_confirm_delete.html'
    success_url = reverse_lazy('treatment_app:family-list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Family.objects.all()
        return Family.objects.filter(therapist=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'המשפחה נמחקה בהצלחה')
        return super().delete(request, *args, **kwargs)

# Document Views
class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'treatment_app/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(family__therapist=self.request.user)

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'treatment_app/document_detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(family__therapist=self.request.user)

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'treatment_app/document_form.html'
    success_url = reverse_lazy('treatment_app:document-list')

    def form_valid(self, form):
        messages.success(self.request, 'המסמך נוצר בהצלחה')
        return super().form_valid(form)

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'treatment_app/document_form.html'
    success_url = reverse_lazy('treatment_app:document-list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(family__therapist=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'המסמך עודכן בהצלחה')
        return super().form_valid(form)

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'treatment_app/document_confirm_delete.html'
    success_url = reverse_lazy('treatment_app:document-list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(family__therapist=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'המסמך נמחק בהצלחה')
        return super().delete(request, *args, **kwargs)
