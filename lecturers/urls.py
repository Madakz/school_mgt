from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('profile/', views.lecturer_profile, name='lecturer_profile'),
    path('courses/assigned/', views.lecturer_courses, name='lecturer_courses'),
    path('courses/<int:course_id>/submit-results/', views.submit_results, name='submit_results'),
    path('courses/<int:course_id>/results/manage/', views.manage_results, name='manage_results'),
    path('courses/<int:course_id>/results/view/', views.view_results, name='view_results'),
]
