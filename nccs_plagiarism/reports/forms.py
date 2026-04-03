from django import forms
from .models import Report
from .utils import validate_unique_past_report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'file', 'report_type']

    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get('report_type')
        uploaded_file = cleaned_data.get('file')

        if report_type == 'past' and uploaded_file:
            existing_past_reports = Report.objects.filter(report_type='past').only('file')
            validate_unique_past_report(uploaded_file, existing_past_reports)

        return cleaned_data
