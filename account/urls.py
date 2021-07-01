from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegistrationView.as_view()),
    path('activation/', views.ActivationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('reset_password/', views.ResetPasswordView.as_view()),
    path('reset_password_complete/', views.ResetPasswordCompleteView.as_view()),
    path('change_password/', views.ChangePasswordView.as_view()),
    path('profile/', views.ProfileListView.as_view()),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view()),
    path('profile-update/<int:pk>/', views.ProfileUpdateView.as_view()),

]
