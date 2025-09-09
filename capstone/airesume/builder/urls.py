from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('resume/new/', views.create_resume, name='create_resume'),
    path('ai/suggest/', views.ai_suggest_view, name='ai_suggest'),
    path('resume/<int:resume_id>/pdf/', views.download_pdf, name='download_pdf'),
    
    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='builder/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
]