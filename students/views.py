from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentProfileForm
from .models import Student, Result, CourseRegistration
from academics.models import Course
from .utils import calculate_grade
from collections import defaultdict


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages



@login_required
def student_dashboard(request):
    """Display all results grouped by session and semester, with GPA and CGPA."""
    student = get_object_or_404(Student, user=request.user)

    # Fetch all course registrations grouped by session and semester
    registrations = CourseRegistration.objects.filter(student=student).select_related('course').order_by('session', 'semester')

    results_grouped = {}
    total_points_all = 0
    total_credits_all = 0

    for reg in registrations:
        key = f"{reg.session} - {reg.semester}"
        if key not in results_grouped:
            results_grouped[key] = {'results': [], 'total_points': 0, 'total_credits': 0}

        result = getattr(reg, 'result', None)
        if result:
            score = result.score
            grade = result.grade
            status = result.status
            lecturer = result.submitted_by.user.get_full_name() if result.submitted_by else '-'

            # Grade to point conversion
            grade_point = 0
            if grade == 'A':
                grade_point = 5
            elif grade == 'B':
                grade_point = 4
            elif grade == 'C':
                grade_point = 3
            elif grade == 'D':
                grade_point = 2
            elif grade == 'E':
                grade_point = 1
            else:
                grade_point = 0

            # Update semester totals
            results_grouped[key]['total_points'] += grade_point * reg.course.credit_unit
            results_grouped[key]['total_credits'] += reg.course.credit_unit

            # Update overall CGPA totals
            total_points_all += grade_point * reg.course.credit_unit
            total_credits_all += reg.course.credit_unit
        else:
            score = None
            grade = None
            status = 'Pending'
            lecturer = '-'

        results_grouped[key]['results'].append({
            'course': reg.course,
            'score': score,
            'grade': grade,
            'status': status,
            'lecturer': lecturer,
        })

    # Compute GPA per semester
    for key, data in results_grouped.items():
        total_credits = data['total_credits']
        data['gpa'] = round(data['total_points'] / total_credits, 2) if total_credits > 0 else 0.00

    # Compute CGPA
    cgpa = round(total_points_all / total_credits_all, 2) if total_credits_all > 0 else 0.00

    return render(request, 'students/dashboard.html', {
        'student': student,
        'results_grouped': results_grouped,
        'cgpa': cgpa,
    })

    return render(request, 'students/dashboard.html')


@login_required
def student_profile_view(request):
    """Display logged-in student's profile."""
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'students/student_profile.html', {'student': student})


@login_required
def student_edit_profile(request):
    student = get_object_or_404(Student, user=request.user)
    user = student.user

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            # ✅ Keep the user logged in if password was changed
            if form.cleaned_data.get('password'):
                update_session_auth_hash(request, user)
            messages.success(request, "Profile updated successfully!")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=user)

    return render(request, 'students/student_edit_profile.html', {'form': form, 'student': student})


@login_required
def student_view_results(request):
    """Display all results grouped by session and semester, with GPA and CGPA."""
    student = get_object_or_404(Student, user=request.user)

    # Fetch all course registrations grouped by session and semester
    registrations = CourseRegistration.objects.filter(student=student).select_related('course').order_by('session', 'semester')

    results_grouped = {}
    total_points_all = 0
    total_credits_all = 0

    for reg in registrations:
        key = f"{reg.session} - {reg.semester}"
        if key not in results_grouped:
            results_grouped[key] = {'results': [], 'total_points': 0, 'total_credits': 0}

        result = getattr(reg, 'result', None)
        if result:
            score = result.score
            grade = result.grade
            status = result.status
            lecturer = result.submitted_by.user.get_full_name() if result.submitted_by else '-'

            # Grade to point conversion
            grade_point = 0
            if grade == 'A':
                grade_point = 5
            elif grade == 'B':
                grade_point = 4
            elif grade == 'C':
                grade_point = 3
            elif grade == 'D':
                grade_point = 2
            elif grade == 'E':
                grade_point = 1
            else:
                grade_point = 0

            # Update semester totals
            results_grouped[key]['total_points'] += grade_point * reg.course.credit_unit
            results_grouped[key]['total_credits'] += reg.course.credit_unit

            # Update overall CGPA totals
            total_points_all += grade_point * reg.course.credit_unit
            total_credits_all += reg.course.credit_unit
        else:
            score = None
            grade = None
            status = 'Pending'
            lecturer = '-'

        results_grouped[key]['results'].append({
            'course': reg.course,
            'score': score,
            'grade': grade,
            'status': status,
            'lecturer': lecturer,
        })

    # Compute GPA per semester
    for key, data in results_grouped.items():
        total_credits = data['total_credits']
        data['gpa'] = round(data['total_points'] / total_credits, 2) if total_credits > 0 else 0.00

    # Compute CGPA
    cgpa = round(total_points_all / total_credits_all, 2) if total_credits_all > 0 else 0.00

    return render(request, 'students/student_results.html', {
        'student': student,
        'results_grouped': results_grouped,
        'cgpa': cgpa,
    })


@login_required
def register_courses(request):
    student = get_object_or_404(Student, user=request.user)

    available_courses = Course.objects.filter(
        department=student.department,
        offered_level=student.level
    )

    if request.method == 'POST':
        session = request.POST.get('session')
        semester = request.POST.get('semester')
        selected_courses = request.POST.getlist('courses')

        if not session or not semester:
            messages.error(request, "Please select both session and semester.")
            return redirect('register_courses')

        if not selected_courses:
            messages.error(request, "Please select at least one course.")
            return redirect('register_courses')

        for course_id in selected_courses:
            course = get_object_or_404(Course, id=course_id)

            # -------- PREREQUISITE CHECK --------
            for prereq in course.prerequisites.all():
                passed = Result.objects.filter(
                    registration__student=student,
                    registration__course=prereq,
                    status='Approved',
                    score__gte=prereq.pass_mark
                ).exists()

                if not passed:
                    messages.error(
                        request,
                        f"{course.code} requires {prereq.code} (Pass mark: {prereq.pass_mark})."
                    )
                    return redirect('register_courses')

            CourseRegistration.objects.get_or_create(
                student=student,
                course=course,
                session=session,
                semester=semester
            )

        messages.success(request, "Courses registered successfully.")
        return redirect('view_registered_courses')

    return render(request, 'students/register_courses.html', {
        'available_courses': available_courses
    })


@login_required
def view_registered_courses(request):
    student = get_object_or_404(Student, user=request.user)
    registrations = CourseRegistration.objects.filter(student=student).select_related('course')
    return render(request, 'students/view_registered_courses.html', {
        'registrations': registrations
    })
    


@login_required
def drop_course(request, registration_id):
    """Allows student to drop a course if results haven't been submitted."""
    student = get_object_or_404(Student, user=request.user)
    registration = get_object_or_404(CourseRegistration, id=registration_id, student=student)
    
    # Check if result has already been submitted for this course
    result_exists = Result.objects.filter(registration=registration).exists()
    
    if result_exists:
        messages.error(request, "You cannot drop this course because a result has already been submitted.")
        return redirect('view_registered_courses')
    
    if registration.course.course_type == 'core':
        messages.error(request, "Core courses cannot be dropped.")
        return redirect('view_registered_courses')
    
    # Only accept POST requests for dropping
    if request.method == "POST":
        course_code = registration.course.code
        course_title = registration.course.title
        registration.delete()
        messages.success(request, f"You have successfully dropped {course_code} - {course_title}.")
        return redirect('view_registered_courses')
    
    # If someone tries to access via GET, redirect them back
    messages.warning(request, "Invalid request method.")
    return redirect('view_registered_courses')
