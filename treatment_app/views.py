from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Family, Child, Treatment, Document
from .forms import FamilyForm, ChildForm, TreatmentForm, DocumentForm

@login_required
def dashboard(request):
    families = Family.objects.all()[:10]
    context = {
        'families': families,
    }
    return render(request, 'treatment_app/dashboard.html', context)

class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'treatment_app/family_list.html'
    context_object_name = 'families'
    ordering = ['-created_at']

class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'treatment_app/family_detail.html'
    context_object_name = 'family'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['children'] = self.object.children.all()
        context['documents'] = self.object.documents.all()
        return context

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

    def form_valid(self, form):
        messages.success(self.request, 'המשפחה עודכנה בהצלחה')
        return super().form_valid(form)

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

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.family.pk})

    def form_valid(self, form):
        messages.success(self.request, 'הילד נוסף בהצלחה')
        return super().form_valid(form)

class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildForm
    template_name = 'treatment_app/child_form.html'

    def get_success_url(self):
        return reverse_lazy('treatment_app:family-detail', kwargs={'pk': self.object.family.pk})

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

class TreatmentDetailView(LoginRequiredMixin, DetailView):
    model = Treatment
    template_name = 'treatment_app/treatment_detail.html'
    context_object_name = 'treatment'

class TreatmentCreateView(LoginRequiredMixin, CreateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = 'treatment_app/treatment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['therapist'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('treatment_app:child-detail', kwargs={'pk': self.object.child.pk})

    def form_valid(self, form):
        messages.success(self.request, 'הטיפול נוסף בהצלחה')
        return super().form_valid(form)

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'family' in self.kwargs:
            kwargs['family'] = get_object_or_404(Family, pk=self.kwargs['family'])
        return kwargs

    def get_success_url(self):
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
