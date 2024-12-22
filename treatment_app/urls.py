from django.urls import path
from . import views

app_name = 'treatment_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Family URLs
    path('families/', views.FamilyListView.as_view(), name='family-list'),
    path('family/<int:pk>/', views.FamilyDetailView.as_view(), name='family-detail'),
    path('family/add/', views.FamilyCreateView.as_view(), name='family-create'),
    path('family/<int:pk>/edit/', views.FamilyUpdateView.as_view(), name='family-update'),
    path('family/<int:pk>/delete/', views.FamilyDeleteView.as_view(), name='family-delete'),
    
    # Child URLs
    path('children/', views.ChildListView.as_view(), name='child-list'),
    path('child/<int:pk>/', views.ChildDetailView.as_view(), name='child-detail'),
    path('child/add/', views.ChildCreateView.as_view(), name='child-create'),
    path('child/<int:pk>/edit/', views.ChildUpdateView.as_view(), name='child-update'),
    path('child/<int:pk>/delete/', views.ChildDeleteView.as_view(), name='child-delete'),
    
    # Treatment URLs
    path('treatments/', views.TreatmentListView.as_view(), name='treatment-list'),
    path('treatment/<int:pk>/', views.TreatmentDetailView.as_view(), name='treatment-detail'),
    path('treatment/add/', views.TreatmentCreateView.as_view(), name='treatment-create'),
    path('treatment/<int:pk>/edit/', views.TreatmentUpdateView.as_view(), name='treatment-update'),
    path('treatment/<int:pk>/delete/', views.TreatmentDeleteView.as_view(), name='treatment-delete'),
    
    # Document URLs
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('document/add/', views.DocumentCreateView.as_view(), name='document-create'),
    path('document/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document-update'),
    path('document/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
]
