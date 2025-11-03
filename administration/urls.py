from django.urls import path
from . import views

urlpatterns = [
    # admin handle admin
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admins/', views.admin_list, name='admin_list'),
    path('admins/add/', views.admin_create, name='admin_create'),
    path('admins/edit/<int:pk>/', views.admin_update, name='admin_update'),
    path('admins/delete/<int:pk>/', views.admin_delete, name='admin_delete'),
    # admin handle lecturers
    path('lecturers/', views.lecturer_list, name='lecturer_list'),
    path('lecturers/add/', views.lecturer_create, name='lecturer_create'),
    path('lecturers/<int:pk>/edit/', views.lecturer_update, name='lecturer_update'),
    path('lecturers/<int:pk>/delete/', views.lecturer_delete, name='lecturer_delete'),
    # Admin handle students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    # Admin handle course assignments
    path('courses/', views.course_assignment_list, name='course_assignment_list'),
    path('courses/<int:pk>/assign/', views.assign_course, name='assign_course'),
    path('courses/<int:pk>/unassign/', views.unassign_course, name='unassign_course'),
    # Admin handle results approval
    path('results/', views.result_list, name='result_list'),
    path('results/<int:pk>/approve/', views.approve_result, name='approve_result'),
    path('results/approve_all/', views.approve_all_results, name='approve_all_results'),

]


