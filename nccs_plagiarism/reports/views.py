from django.shortcuts import render, redirect
from .models import Report
from .forms import ReportForm
from .utils import extract_text, calculate_jaccard_similarity


PLAGIARISM_THRESHOLD = 30.0


def home(request):
    total_reports_uploaded = Report.objects.count()
    reports_checked = Report.objects.filter(report_type='new').count()
    repository_size = Report.objects.filter(report_type='past').count()

    past_reports = list(Report.objects.filter(report_type='past').only('content'))
    new_reports = list(Report.objects.filter(report_type='new').only('content'))

    plagiarism_cases_detected = 0
    for submitted_report in new_reports:
        highest_similarity = 0
        for repository_report in past_reports:
            similarity = calculate_jaccard_similarity(
                submitted_report.content,
                repository_report.content
            )
            if similarity > highest_similarity:
                highest_similarity = similarity

        if highest_similarity >= PLAGIARISM_THRESHOLD:
            plagiarism_cases_detected += 1

    context = {
        'total_reports_uploaded': total_reports_uploaded,
        'reports_checked': reports_checked,
        'plagiarism_cases_detected': plagiarism_cases_detected,
        'repository_size': repository_size,
    }
    return render(request, 'reports/home.html', context)


def upload_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)

        if form.is_valid():
            report = form.save(commit=False)

            # Save first to create file path
            report.save()

            # Extract text after file is saved
            report.content = extract_text(report.file.path)
            report.save()

            # If new submission → go directly to result page
            if report.report_type == 'new':
                return redirect('compare_reports')

            # If past report → show success page
            return redirect('upload_success')

    else:
        form = ReportForm()

    return render(request, 'reports/upload.html', {'form': form})


def compare_reports(request):
    past_reports = Report.objects.filter(report_type='past')
    new_submission = Report.objects.filter(report_type='new').order_by('-uploaded_at').first()

    # If no repository or no new submission
    if not past_reports.exists() or not new_submission:
        return render(request, "reports/result.html", {
            "result": None,
            "report1_name": "",
            "similarity_table": []
        })

    new_text = new_submission.content
    similarity_table = []
    highest_similarity = 0

    for past_report in past_reports:
        similarity_score = calculate_jaccard_similarity(
            new_text,
            past_report.content
        )

        similarity_percentage = similarity_score

        similarity_table.append({
            "past_report_name": past_report.file.name.split('/')[-1],
            "similarity": similarity_percentage
        })

        if similarity_percentage > highest_similarity:
            highest_similarity = similarity_percentage

    return render(request, "reports/result.html", {
        "result": highest_similarity,
        "report1_name": new_submission.file.name.split('/')[-1],
        "similarity_table": similarity_table
    })


def upload_success(request):
    return render(request, "reports/success.html")


def repository(request):
    past_reports = Report.objects.filter(report_type='past').order_by('-uploaded_at')
    return render(request, "reports/repository.html", {'past_reports': past_reports})
