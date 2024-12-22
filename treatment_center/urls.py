"""
URL configuration for treatment_center project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views, logout
from django.contrib import messages
from django.shortcuts import redirect

def custom_logout(request):
    if request.method == 'POST':
        messages.success(request, 'יצאת מהמערכת בהצלחה')
        logout(request)
        return redirect('login')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('treatment_app.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='treatment_app/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
