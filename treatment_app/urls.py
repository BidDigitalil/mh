from django.urls import path
from . import views

app_name = 'treatment_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Family URLs
    path('families/', views.FamilyListView.as_view(), name='family-list'),
    path('family/new/', views.FamilyCreateView.as_view(), name='family-create'),
    path('family/<int:pk>/', views.FamilyDetailView.as_view(), name='family-detail'),
    path('family/<int:pk>/edit/', views.FamilyUpdateView.as_view(), name='family-update'),
    path('family/<int:pk>/delete/', views.FamilyDeleteView.as_view(), name='family-delete'),
    
    # Child URLs
    path('children/', views.ChildListView.as_view(), name='child-list'),
    path('child/new/', views.ChildCreateView.as_view(), name='child-create'),
    path('child/<int:pk>/', views.ChildDetailView.as_view(), name='child-detail'),
    path('family/<int:family>/child/add/', views.ChildCreateView.as_view(), name='family-child-create'),
    path('child/<int:pk>/edit/', views.ChildUpdateView.as_view(), name='child-update'),
    path('child/<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child-delete'),
    
    # Treatment URLs
    path('treatments/', views.TreatmentListView.as_view(), name='treatment-list'),
    path('treatments/weekly/', views.weekly_calendar_view, name='weekly_calendar'),
    path('treatments/calendar/', views.treatment_calendar_data, name='treatment_calendar_data'),
    path('treatments/calendar/view/', views.calendar_view, name='calendar_view'),
    path('treatment/new/', views.TreatmentCreateView.as_view(), name='treatment-create'),
    path('family/<int:family_id>/treatment/create/', views.TreatmentCreateView.as_view(), name='family-treatment-create'),
    path('child/<int:child_id>/treatment/create/', views.TreatmentCreateView.as_view(), name='child-treatment-create'),
    path('treatment/<int:pk>/', views.TreatmentDetailView.as_view(), name='treatment-detail'),
    path('treatment/<int:pk>/update/', views.TreatmentUpdateView.as_view(), name='treatment-update'),
    path('treatment/<int:pk>/delete/', views.TreatmentDeleteView.as_view(), name='treatment-delete'),
    
    # Therapist management
    path('therapists/', views.TherapistListView.as_view(), name='therapist-list'),
    path('therapist/add/', views.TherapistCreateView.as_view(), name='therapist-create'),
    path('therapist/<int:pk>/edit/', views.TherapistUpdateView.as_view(), name='therapist-update'),
    path('therapist/<int:pk>/delete/', views.TherapistDeleteView.as_view(), name='therapist-delete'),
    
    # Document URLs
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('document/add/', views.DocumentCreateView.as_view(), name='document-create'),
    path('family/<int:family>/document/add/', views.DocumentCreateView.as_view(), name='family-document-create'),
    path('child/<int:child>/document/add/', views.DocumentCreateView.as_view(), name='child-document-create'),
    path('document/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document-update'),
    path('document/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
]
