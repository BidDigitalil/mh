from django.urls import path
from . import views

app_name = 'treatment_app'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Family URLs
    path('families/', views.FamilyListView.as_view(), name='family-list'),
    path('families/create/', views.FamilyCreateView.as_view(), name='family-create'),
    path('families/<int:pk>/', views.FamilyDetailView.as_view(), name='family-detail'),
    path('families/<int:pk>/update/', views.FamilyUpdateView.as_view(), name='family-update'),
    path('families/<int:pk>/delete/', views.FamilyDeleteView.as_view(), name='family-delete'),
    
    # Document URLs
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('documents/create/', views.DocumentCreateView.as_view(), name='document-create'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/update/', views.DocumentUpdateView.as_view(), name='document-update'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
]
