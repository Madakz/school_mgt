from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lecturer
from academics.models import Course
from students.models import CourseRegistration, Result
from students.forms import ResultForm
from students.utils import calculate_grade
from django.db.models import Count



# ======== lecturer ==========
def lecturer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'lecturer_profile'):
            messages.error(request, "Access denied. Lecturer account required.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@lecturer_required
def lecturer_dashboard(request):
    lecturer = request.user.lecturer_profile

    # Assigned courses
    assigned_courses = Course.objects.filter(assigned_lecturer=lecturer)
    total_courses = assigned_courses.count()

    # Students taking lecturer's courses
    total_students = CourseRegistration.objects.filter(course__in=assigned_courses).count()

    # Results submitted by lecturer
    lecturer_results = Result.objects.filter(submitted_by=lecturer)

    approved_results = lecturer_results.filter(status='Approved').count()
    pending_results = lecturer_results.filter(status='Pending').count()

    total_results = approved_results + pending_results
    approved_percent = (approved_results / total_results * 100) if total_results > 0 else 0
    pending_percent = (pending_results / total_results * 100) if total_results > 0 else 0

    # ✅ Grade Distribution Count
    grade_counts = lecturer_results.values('grade').annotate(total=Count('grade'))

    grade_map = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
    for g in grade_counts:
        grade_map[g['grade']] = g['total']

    context = {
        'lecturer': lecturer,
        'total_courses': total_courses,
        'total_students': total_students,
        'approved_results': approved_results,
        'pending_results': pending_results,
        'approved_percent': round(approved_percent, 2),
        'pending_percent': round(pending_percent, 2),
        'grades': grade_map,  # ✅ Pass grade data to template
    }

    return render(request, 'lecturers/dashboard.html', context)


@login_required
@lecturer_required
def lecturer_profile(request):
    lecturer = request.user.lecturer_profile
    return render(request, 'lecturers/profile.html', {'lecturer': lecturer})


@login_required
@lecturer_required
def lecturer_courses(request):
    lecturer = request.user.lecturer_profile
    courses = Course.objects.filter(assigned_lecturer=lecturer)

    for course in courses:
        total_students = CourseRegistration.objects.filter(course=course).count()
        submitted_results = Result.objects.filter(
            registration__course=course,
            submitted_by=lecturer
        ).count()

        if submitted_results == 0:
            course.result_status = 'none'  # No result submitted
        elif submitted_results < total_students:
            course.result_status = 'partial'  # Some results submitted
        else:
            course.result_status = 'full'  # All results submitted

    return render(request, 'lecturers/course_list.html', {'courses': courses})


@login_required
@lecturer_required
def submit_results(request, course_id):
    lecturer = request.user.lecturer_profile
    course = get_object_or_404(Course, id=course_id, assigned_lecturer=lecturer)
    registrations = CourseRegistration.objects.filter(course=course)

    if request.method == 'POST':
        for reg in registrations:
            score_input = request.POST.get(f'score_{reg.id}')
            if not score_input:
                continue  # Skip empty fields

            try:
                score = float(score_input)
            except ValueError:
                messages.error(request, f"Invalid score for {reg.student.user.get_full_name()}.")
                continue

            # Auto calculate grade using your utils
            grade = calculate_grade(score)

            # ✅ Fix: use defaults to prevent IntegrityError
            result, created = Result.objects.get_or_create(
                registration=reg,
                defaults={
                    'score': score,
                    'grade': grade,
                    'submitted_by': lecturer,
                }
            )

            #Update only if not approved
            if not created and result.status == 'Pending':
                result.score = score
                result.grade = grade
                result.submitted_by = lecturer
                result.save()

        messages.success(request, "Results submitted successfully. Grades were auto-calculated.")
        return redirect('lecturer_courses')

    context = {
        'course': course,
        'registrations': registrations,
    }
    return render(request, 'lecturers/submit_results.html', context)


@login_required
@lecturer_required
def manage_results(request, course_id):
    lecturer = request.user.lecturer_profile
    course = get_object_or_404(Course, id=course_id, assigned_lecturer=lecturer)
    registrations = CourseRegistration.objects.filter(course=course)

    if request.method == 'POST':
        for reg in registrations:
            score = request.POST.get(f'score_{reg.id}')
            if score:  # Only process filled scores
                try:
                    score = float(score)
                except ValueError:
                    messages.warning(request, f"Invalid score for {reg.student.user.get_full_name()}.")
                    continue

                # Compute grade automatically
                grade = calculate_grade(score)

                result, created = Result.objects.get_or_create(registration=reg)
                if result.status == 'Pending':
                    result.score = score
                    result.grade = grade
                    result.submitted_by = lecturer
                    result.save()

        messages.success(request, "Results saved successfully (grades auto-calculated).")
        return redirect('view_results', course_id=course.id)

    context = {
        'course': course,
        'registrations': registrations,
    }
    return render(request, 'lecturers/manage_results.html', context)


@login_required
@lecturer_required
def view_results(request, course_id):
    lecturer = request.user.lecturer_profile
    course = get_object_or_404(Course, id=course_id, assigned_lecturer=lecturer)
    registrations = CourseRegistration.objects.filter(course=course).select_related('student', 'result')

    context = {
        'course': course,
        'registrations': registrations,
    }
    return render(request, 'lecturers/view_results.html', context)


@login_required
@lecturer_required
def view_course_students(request, course_id):
    lecturer = request.user.lecturer_profile
    course = get_object_or_404(Course, id=course_id, assigned_lecturer=lecturer)

    # Students registered for this course
    registrations = CourseRegistration.objects.filter(course=course).select_related('student__user')

    return render(request, 'lecturers/course_students.html', {
        'course': course,
        'registrations': registrations
    })
