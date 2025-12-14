from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile_view, name='student_profile'),
    path('profile/edit/', views.student_edit_profile, name='student_edit_profile'),
    path('results/', views.student_view_results, name='student_view_results'),
    path('register-courses/', views.register_courses, name='register_courses'),
    path('registered-courses/', views.view_registered_courses, name='view_registered_courses'),
    path('drop-course/<int:registration_id>/', views.drop_course, name='drop_course'),

]
