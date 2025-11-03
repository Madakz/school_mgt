from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from .models import AdminUser
from .forms import AdminUserForm, CustomUserForm, LecturerForm, StudentForm, CourseAssignmentForm, ResultApprovalForm
from lecturers.models import Lecturer
from students.models import Student, Result
from academics.models import Course




# Helper decorator (optional)
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, "Access denied: Admins only.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def admin_dashboard(request):
    # Existing admins list
    admins = AdminUser.objects.select_related('user')

    # Statistics
    total_lecturers = Lecturer.objects.count()
    total_students = Student.objects.count()
    total_courses = Course.objects.count()

    # Course assignment stats
    assigned_courses = Course.objects.filter(assigned_lecturer__isnull=False).count()
    unassigned_courses = Course.objects.filter(assigned_lecturer__isnull=True).count()

    context = {
        'admins': admins,
        'total_lecturers': total_lecturers,
        'total_students': total_students,
        'total_courses': total_courses,
        'assigned_courses': assigned_courses,
        'unassigned_courses': unassigned_courses,
    }

    return render(request, 'administration/dashboard.html', context)


@login_required
@admin_required
def admin_list(request):
    admins = AdminUser.objects.select_related('user')
    return render(request, 'administration/admin_list.html', {'admins': admins})


@login_required
@admin_required
def admin_create(request):
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST)
        admin_form = AdminUserForm(request.POST)
        if user_form.is_valid() and admin_form.is_valid():
            # Save CustomUser
            user = user_form.save(commit=False)
            user.role = 'admin'
            user.is_staff = True
            user.set_password('default123')
            user.save()
            # Save AdminUser and link it to CustomUser
            admin_profile = admin_form.save(commit=False)
            admin_profile.user = user
            admin_profile.save()
            messages.success(request, "Admin created successfully.")
            return redirect('admin_list')
    else:
        user_form = CustomUserForm()
        admin_form = AdminUserForm()
    return render(request, 'administration/admin_form.html', {
        'user_form': user_form,
        'admin_form': admin_form,
        'title': 'Add Admin'
    })


@login_required
@admin_required
def admin_update(request, pk):
    admin = get_object_or_404(AdminUser, pk=pk)
    user = admin.user

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=user)
        admin_form = AdminUserForm(request.POST, instance=admin)

        if user_form.is_valid() and admin_form.is_valid():
            user_form.save()
            admin_form.save()
            messages.success(request, "Admin updated successfully.")
            return redirect('admin_list')
    else:
        user_form = CustomUserForm(instance=user)
        admin_form = AdminUserForm(instance=admin)

    return render(request, 'administration/admin_form.html', {
        'user_form': user_form,
        'admin_form': admin_form,
        'title': 'Edit Admin'
    })


@login_required
@admin_required
def admin_delete(request, pk):
    admin = get_object_or_404(AdminUser, pk=pk)
    if request.method == 'POST':
        admin.user.delete()  # delete linked CustomUser too
        admin.delete()
        messages.success(request, "Admin deleted successfully.")
        return redirect('admin_list')

    return render(request, 'administration/admin_confirm_delete.html', {'admin': admin})


@login_required
@admin_required
def lecturer_list(request):
    lecturers = Lecturer.objects.all()
    return render(request, 'administration/lecturer_list.html', {'lecturers': lecturers})

@login_required
@admin_required
def lecturer_create(request):
    if request.method == 'POST':
        form = LecturerForm(request.POST)
        if form.is_valid():
            lecturer = form.save(commit=False)

            # Ensure the related CustomUser is marked as staff
            user = lecturer.user
            user.is_staff = True
            user.save()


            lecturer.save()
            return redirect('lecturer_list')
    else:
        form = LecturerForm()
    return render(request, 'administration/lecturer_create.html', {'form': form})

@login_required
@admin_required
def lecturer_update(request, pk):
    lecturer = get_object_or_404(Lecturer, pk=pk)
    if request.method == 'POST':
        form = LecturerForm(request.POST, instance=lecturer)
        if form.is_valid():
            form.save()
            return redirect('lecturer_list')
    else:
        form = LecturerForm(instance=lecturer)
        form.fields['password'].required = False  
    return render(request, 'administration/lecturer_update.html', {'form': form})

@login_required
@admin_required
def lecturer_delete(request, pk):
    lecturer = get_object_or_404(Lecturer, pk=pk)
    if request.method == 'POST':
        lecturer.user.delete()  # also delete linked user
        lecturer.delete()
        return redirect('lecturer_list')
    return render(request, 'administration/lecturer_confirm_delete.html', {'lecturer': lecturer})


@login_required
@admin_required
def student_list(request):
    students = Student.objects.select_related('user', 'department').all()
    return render(request, 'administration/student_list.html', {'students': students})

@login_required
@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'administration/student_create.html', {'form': form})

@login_required
@admin_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student, initial={
            'email': student.user.email,
            'username': student.user.username,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
        })
    return render(request, 'administration/student_update.html', {'form': form})

@login_required
@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()  # remove linked user
        student.delete()
        return redirect('student_list')
    return render(request, 'administration/student_confirm_delete.html', {'student': student})

@login_required
@admin_required
def course_assignment_list(request):
    courses = Course.objects.select_related('assigned_lecturer', 'department').all()
    return render(request, 'administration/course_assign_list.html', {'courses': courses})

@login_required
@admin_required
def assign_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseAssignmentForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' has been assigned successfully.")
            return redirect('course_assignment_list')
    else:
        form = CourseAssignmentForm(instance=course)
    return render(request, 'administration/course_assign_form.html', {'form': form, 'course': course})

@login_required
@admin_required
def unassign_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.assigned_lecturer = None
        course.save()
        messages.success(request, f"Lecturer unassigned from course '{course.title}'.")
        return redirect('course_assignment_list')
    return render(request, 'administration/course_assign_confirm_delete.html', {'course': course})


@login_required
@admin_required
# List all results
def result_list(request):
    results = Result.objects.select_related(
        'registration__student__user',
        'registration__course',
        'submitted_by'
    ).all().order_by('-id')
    return render(request, 'administration/result_list.html', {'results': results})


@login_required
@admin_required
# Approve a single result
def approve_result(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        form = ResultApprovalForm(request.POST, instance=result)
        if form.is_valid():
            approved_result = form.save(commit=False)
            approved_result.status = 'Approved'
            approved_result.approved_by = request.user
            approved_result.save()
            messages.success(request, f"Result for {result.registration.student.user.get_full_name()} approved successfully.")
            return redirect('result_list')
    else:
        form = ResultApprovalForm(instance=result)
    return render(request, 'administration/result_confirm_approve.html', {'form': form, 'result': result})

@login_required
@admin_required
def approve_all_results(request):
    if request.method == 'POST':
        pending_results = Result.objects.filter(status='Pending')
        count = pending_results.count()
        for res in pending_results:
            res.status = 'Approved'
            res.approved_by = request.user
            res.save()
        messages.success(request, f"{count} pending results have been approved successfully.")
        return redirect('result_list')
    return redirect('result_list')


